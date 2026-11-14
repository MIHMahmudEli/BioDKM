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
from sklearn.metrics import silhouette_score, davies_bouldin_score
from transformers import AutoTokenizer, AutoModel
import umap
import hdbscan

print("--- Step 1: Loading Data ---")
data_url = "https://huggingface.co/datasets/MohsinElis/pubmed-disease-mapping/resolve/main/pubmed_dataset.csv"
df = pd.read_csv(data_url)
print(f"Loaded raw data: {df.shape}")

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

print("--- Step 3: Preparing NPMI Reference Matrix ---")
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

print("--- Step 4: Extracting Features ---")
# TF-IDF
tfidf_vec = TfidfVectorizer(max_features=5000, min_df=5, max_df=0.9, stop_words='english')
X_tfidf = normalize(tfidf_vec.fit_transform(df['clean_abstract']), norm='l2').toarray()

# BioBERT (GPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"BioBERT using device: {device}")
model_name = "dmis-lab/biobert-v1.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).to(device)
model.eval()

batch_size = 64 if torch.cuda.is_available() else 16
biobert_embeddings = []
with torch.no_grad():
    for i in range(0, len(df), batch_size):
        batch_texts = df['clean_abstract'].iloc[i:i+batch_size].tolist()
        encoded = tokenizer(batch_texts, padding=True, truncation=True, max_length=128, return_tensors='pt').to(device)
        outputs = model(**encoded)
        mask = encoded['attention_mask'].unsqueeze(-1).expand(outputs.last_hidden_state.size()).float()
        mean_pooled = torch.sum(outputs.last_hidden_state * mask, 1) / torch.clamp(mask.sum(1), min=1e-9)
        biobert_embeddings.append(mean_pooled.cpu().numpy())

X_biobert = normalize(np.vstack(biobert_embeddings), norm='l2')

# Base UMAP embeddings
umap_tfidf_base = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42).fit_transform(X_tfidf)
umap_bio_base = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42).fit_transform(X_biobert)

results = []

def evaluate_clustering(embedding_name, X_2d, labels, param_name, param_val):
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    noise_ratio = np.mean(labels == -1) * 100
    mask = labels != -1
    if mask.sum() > 0 and n_clusters > 1:
        sil = silhouette_score(X_2d[mask], labels[mask])
        db = davies_bouldin_score(X_2d[mask], labels[mask])
    else:
        sil, db = 0.0, 9.99
        
    cluster_ids = sorted([c for c in set(labels) if c != -1])[:15]
    npmis = []
    for c_id in cluster_ids:
        c_texts = df['clean_abstract'].iloc[labels == c_id]
        if len(c_texts) < 2:
            continue
        c_vec = TfidfVectorizer(max_features=100, min_df=1, stop_words='english')
        try:
            mat = c_vec.fit_transform(c_texts)
            top_words = [c_vec.get_feature_names_out()[i] for i in np.argsort(np.asarray(mat.mean(axis=0)).flatten())[::-1][:10]]
            npmis.append(compute_npmi_for_topic(top_words))
        except Exception:
            pass
            
    mean_npmi = np.mean(npmis) if npmis else 0.0
    
    return {
        'Embedding': embedding_name,
        'Swept_Parameter': param_name,
        'Parameter_Value': param_val,
        'Num_Clusters': n_clusters,
        'Noise_Percent': round(noise_ratio, 2),
        'Silhouette': round(sil, 4),
        'Davies_Bouldin': round(db, 4),
        'Mean_NPMI': round(mean_npmi, 4)
    }

print("--- Step 5: Sweeping HDBSCAN min_cluster_size ---")
cluster_sizes = [15, 20, 30, 40, 50, 75, 100]
for cs in cluster_sizes:
    hdb_t = hdbscan.HDBSCAN(min_cluster_size=cs, min_samples=5, metric='euclidean')
    lbl_t = hdb_t.fit_predict(umap_tfidf_base)
    results.append(evaluate_clustering('TF-IDF', umap_tfidf_base, lbl_t, 'min_cluster_size', cs))
    
    hdb_b = hdbscan.HDBSCAN(min_cluster_size=cs, min_samples=5, metric='euclidean')
    lbl_b = hdb_b.fit_predict(umap_bio_base)
    results.append(evaluate_clustering('BioBERT', umap_bio_base, lbl_b, 'min_cluster_size', cs))

print("--- Step 6: Sweeping UMAP n_neighbors ---")
n_neighbors_list = [5, 10, 15, 25, 50]
for nn in n_neighbors_list:
    u_t = umap.UMAP(n_components=2, n_neighbors=nn, min_dist=0.1, metric='cosine', random_state=42).fit_transform(X_tfidf)
    lbl_t = hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, metric='euclidean').fit_predict(u_t)
    results.append(evaluate_clustering('TF-IDF', u_t, lbl_t, 'umap_n_neighbors', nn))
    
    u_b = umap.UMAP(n_components=2, n_neighbors=nn, min_dist=0.1, metric='cosine', random_state=42).fit_transform(X_biobert)
    lbl_b = hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, metric='euclidean').fit_predict(u_b)
    results.append(evaluate_clustering('BioBERT', u_b, lbl_b, 'umap_n_neighbors', nn))

res_df = pd.DataFrame(results)
res_df.to_csv("hyperparameter_sensitivity_results.csv", index=False)
print("\n--- Sensitivity Results Summary ---")
print(res_df.head(20).to_string())

# Plot Sensitivity Curves
plt.figure(figsize=(14, 5))
plt.subplot(1, 3, 1)
sub_mcs = res_df[res_df['Swept_Parameter'] == 'min_cluster_size']
for emb in ['TF-IDF', 'BioBERT']:
    d = sub_mcs[sub_mcs['Embedding'] == emb]
    plt.plot(d['Parameter_Value'], d['Num_Clusters'], marker='o', label=emb)
plt.title("Discovered Topics vs. min_cluster_size", fontsize=11, fontweight='bold')
plt.xlabel("min_cluster_size", fontsize=10)
plt.ylabel("Number of Topics", fontsize=10)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

plt.subplot(1, 3, 2)
for emb in ['TF-IDF', 'BioBERT']:
    d = sub_mcs[sub_mcs['Embedding'] == emb]
    plt.plot(d['Parameter_Value'], d['Silhouette'], marker='s', label=emb)
plt.title("Silhouette vs. min_cluster_size", fontsize=11, fontweight='bold')
plt.xlabel("min_cluster_size", fontsize=10)
plt.ylabel("Silhouette Score", fontsize=10)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

plt.subplot(1, 3, 3)
sub_nn = res_df[res_df['Swept_Parameter'] == 'umap_n_neighbors']
for emb in ['TF-IDF', 'BioBERT']:
    d = sub_nn[sub_nn['Embedding'] == emb]
    plt.plot(d['Parameter_Value'], d['Silhouette'], marker='^', label=emb)
plt.title("Silhouette vs. UMAP n_neighbors", fontsize=11, fontweight='bold')
plt.xlabel("n_neighbors", fontsize=10)
plt.ylabel("Silhouette Score", fontsize=10)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig("sensitivity_curves.png", dpi=300)
print("Saved hyperparameter_sensitivity_results.csv and sensitivity_curves.png")
