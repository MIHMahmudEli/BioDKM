import os
import sys
import subprocess

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "umap-learn", "hdbscan"], check=False)

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import normalize
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import (
    adjusted_rand_score,
    normalized_mutual_info_score,
    homogeneity_completeness_v_measure,
    silhouette_score,
    davies_bouldin_score
)
from transformers import AutoTokenizer, AutoModel
import umap
import hdbscan

def calculate_purity(y_true, y_pred):
    contingency_matrix = pd.crosstab(y_true, y_pred)
    return np.sum(contingency_matrix.max(axis=0)) / len(y_true)

print("--- Step 1: Loading Dataset ---")
data_url = "https://huggingface.co/datasets/MohsinElis/pubmed-disease-mapping/resolve/main/pubmed_dataset.csv"
df = pd.read_csv(data_url)

# Ground-truth disease queries
disease_slices = [
    ('cancer neoplasm', 1951),
    ('diabetes mellitus', 1922),
    ('stroke cerebrovascular', 1880),
    ('Alzheimer disease dementia', 1753),
    ('hypertension blood pressure', 1747),
    ('cardiovascular disease', 1722),
    ('neurological disorders', 1586),
    ('Parkinson disease', 1504)
]
disease_labels = []
for name, count in disease_slices:
    disease_labels.extend([name] * count)
df['Disease'] = disease_labels[:len(df)]

print("--- Step 2: Preprocessing ---")
import nltk
try:
    from nltk.corpus import stopwords
    stop_words_set = set(stopwords.words('english'))
except Exception:
    nltk.download('stopwords', quiet=True)
    from nltk.corpus import stopwords
    stop_words_set = set(stopwords.words('english'))

def preprocess(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    tokens = [w for w in text.split() if w not in stop_words_set and len(w) > 2]
    return " ".join(tokens)

df['clean_abstract'] = df['Abstract'].apply(preprocess)
df = df[df['clean_abstract'].str.strip() != ""].copy().reset_index(drop=True)
print(f"Cleaned corpus size: {len(df)}")
true_labels = df['Disease'].values

print("--- Step 3: Extracting PubMedBERT Embeddings ---")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"PubMedBERT using device: {device}")
model_name = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).to(device)
model.eval()

batch_size = 64 if torch.cuda.is_available() else 16
pubmedbert_embeddings = []

with torch.no_grad():
    for i in range(0, len(df), batch_size):
        batch_texts = df['clean_abstract'].iloc[i:i+batch_size].tolist()
        encoded = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors='pt'
        ).to(device)
        outputs = model(**encoded)
        mask = encoded['attention_mask'].unsqueeze(-1).expand(outputs.last_hidden_state.size()).float()
        sum_embeddings = torch.sum(outputs.last_hidden_state * mask, 1)
        sum_mask = torch.clamp(mask.sum(1), min=1e-9)
        mean_pooled = sum_embeddings / sum_mask
        pubmedbert_embeddings.append(mean_pooled.cpu().numpy())

X_pmb = np.vstack(pubmedbert_embeddings)
X_pmb_norm = normalize(X_pmb, norm='l2')
print(f"PubMedBERT normalized shape: {X_pmb_norm.shape}")

print("--- Step 4: UMAP 2D Projection ---")
umap_reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42)
umap_2d = umap_reducer.fit_transform(X_pmb_norm)

print("--- Step 5: Preparing Binary Co-occurrence Matrix for NPMI ---")
count_vec = CountVectorizer(min_df=5, max_df=0.95, binary=True, stop_words='english')
dtm_binary = count_vec.fit_transform(df['clean_abstract'])
vocab = count_vec.get_feature_names_out()
word2idx = {w: i for i, w in enumerate(vocab)}
N_docs = dtm_binary.shape[0]
doc_counts = np.array(dtm_binary.sum(axis=0)).flatten()

def compute_npmi_for_topic(words, top_n=10):
    valid_words = [w for w in words[:top_n] if w in word2idx]
    if len(valid_words) < 2:
        return 0.0
    
    indices = [word2idx[w] for w in valid_words]
    sub_dtm = dtm_binary[:, indices]
    cooccur = (sub_dtm.T @ sub_dtm).toarray()
    
    npmi_vals = []
    k = len(valid_words)
    for i in range(k):
        for j in range(i + 1, k):
            c_ij = cooccur[i, j]
            if c_ij == 0:
                npmi_vals.append(-1.0)
                continue
            p_ij = c_ij / N_docs
            p_i = doc_counts[indices[i]] / N_docs
            p_j = doc_counts[indices[j]] / N_docs
            pmi = np.log(p_ij / (p_i * p_j))
            npmi = pmi / (-np.log(p_ij))
            npmi_vals.append(npmi)
            
    return np.mean(npmi_vals) if npmi_vals else 0.0

print("--- Step 6: Clustering & Evaluation ---")
algorithms = {
    'KMeans': KMeans(n_clusters=5, n_init=20, random_state=42),
    'HDBSCAN': hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, metric='euclidean'),
    'Hierarchical': AgglomerativeClustering(n_clusters=5, linkage='ward')
}

metrics_list = []
topic_records = []

for name, algo in algorithms.items():
    labels = algo.fit_predict(umap_2d)
    is_hdb = (name == 'HDBSCAN')
    
    if is_hdb:
        mask = labels != -1
        eval_2d = umap_2d[mask]
        eval_labels = labels[mask]
        eval_y_true = true_labels[mask]
        eval_df = df[mask].reset_index(drop=True)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    else:
        eval_2d = umap_2d
        eval_labels = labels
        eval_y_true = true_labels
        eval_df = df.copy().reset_index(drop=True)
        n_clusters = len(set(labels))
        
    sil = silhouette_score(eval_2d, eval_labels)
    db = davies_bouldin_score(eval_2d, eval_labels)
    ari = adjusted_rand_score(eval_y_true, eval_labels)
    nmi = normalized_mutual_info_score(eval_y_true, eval_labels)
    homo, comp, v_meas = homogeneity_completeness_v_measure(eval_y_true, eval_labels)
    purity = calculate_purity(eval_y_true, eval_labels)
    
    # Extract topics & NPMI
    cluster_ids = sorted([c for c in set(eval_labels)])
    topic_npmis = []
    for c_id in cluster_ids:
        c_texts = eval_df['clean_abstract'].iloc[eval_labels == c_id]
        if len(c_texts) == 0:
            continue
        c_tfidf = TfidfVectorizer(max_features=200, min_df=1, stop_words='english')
        try:
            c_mat = c_tfidf.fit_transform(c_texts)
            top_words = [c_tfidf.get_feature_names_out()[idx] for idx in np.argsort(np.asarray(c_mat.mean(axis=0)).flatten())[::-1][:15]]
        except Exception:
            top_words = []
            
        c_npmi = compute_npmi_for_topic(top_words, top_n=10)
        topic_npmis.append(c_npmi)
        topic_records.append({
            'Model': 'PubMedBERT',
            'Algorithm': name,
            'Cluster_ID': c_id,
            'Num_Docs': len(c_texts),
            'Top_Keywords': ", ".join(top_words[:10]),
            'NPMI': round(c_npmi, 4)
        })
        
    mean_npmi = np.mean(topic_npmis) if topic_npmis else 0.0
    
    metrics_list.append({
        'Pipeline': 'PubMedBERT',
        'Method': name,
        'Num_Topics': n_clusters,
        'Silhouette': round(sil, 4),
        'Davies_Bouldin': round(db, 4),
        'NPMI_Coherence': round(mean_npmi, 4),
        'ARI': round(ari, 4),
        'NMI': round(nmi, 4),
        'Homogeneity': round(homo, 4),
        'Completeness': round(comp, 4),
        'V_Measure': round(v_meas, 4),
        'Purity': round(purity, 4)
    })

pd.DataFrame(metrics_list).to_csv("pubmedbert_evaluation_metrics.csv", index=False)
pd.DataFrame(topic_records).to_csv("pubmedbert_topics.csv", index=False)

# Visualizing UMAP
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for idx, (name, algo) in enumerate(algorithms.items()):
    labels = algo.labels_ if hasattr(algo, 'labels_') else algo.fit_predict(umap_2d)
    axes[idx].scatter(umap_2d[:, 0], umap_2d[:, 1], c=labels, cmap='tab20', s=1.5, alpha=0.6)
    axes[idx].set_title(f"PubMedBERT + {name}", fontsize=12, fontweight='bold')
    axes[idx].axis('off')

plt.tight_layout()
plt.savefig("pubmedbert_umap_clusters.png", dpi=300)
print("Completed PubMedBERT experiment!")
