import os
import sys
import subprocess

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "umap-learn", "hdbscan"], check=False)

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
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

print("--- Step 1: Loading Dataset from Hugging Face ---")
data_url = "https://huggingface.co/datasets/MohsinElis/pubmed-disease-mapping/resolve/main/pubmed_dataset.csv"
df = pd.read_csv(data_url)
print(f"Loaded raw data: {df.shape}")

# Assign ground-truth disease query labels based on exact retrieval slices
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

print("--- Step 3: Feature Extraction ---")
# 3A. TF-IDF
tfidf_vec = TfidfVectorizer(max_features=5000, min_df=5, max_df=0.9, stop_words='english')
X_tfidf = tfidf_vec.fit_transform(df['clean_abstract'])
X_tfidf_norm = normalize(X_tfidf, norm='l2').toarray()
print(f"TF-IDF shape: {X_tfidf_norm.shape}")

# 3B. BioBERT Embeddings
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Extracting BioBERT on device: {device}")
model_name = "dmis-lab/biobert-v1.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).to(device)
model.eval()

batch_size = 64 if torch.cuda.is_available() else 16
biobert_embeddings = []

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
        biobert_embeddings.append(mean_pooled.cpu().numpy())

X_biobert = np.vstack(biobert_embeddings)
X_biobert_norm = normalize(X_biobert, norm='l2')
print(f"BioBERT shape: {X_biobert_norm.shape}")

print("--- Step 4: UMAP Dimensionality Reduction ---")
umap_tfidf = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42)
umap_2d_tfidf = umap_tfidf.fit_transform(X_tfidf_norm)

umap_biobert = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42)
umap_2d_biobert = umap_biobert.fit_transform(X_biobert_norm)

print("--- Step 5: Clustering & External Alignment Evaluation ---")
pipelines = {
    'TF-IDF': umap_2d_tfidf,
    'BioBERT': umap_2d_biobert
}

results = []
heatmaps_data = {}

for pipe_name, X_2d in pipelines.items():
    print(f"\nEvaluating Pipeline: {pipe_name}")
    
    # 1. KMeans (K=5)
    km = KMeans(n_clusters=5, n_init=20, random_state=42)
    labels_km = km.fit_predict(X_2d)
    ari_km = adjusted_rand_score(true_labels, labels_km)
    nmi_km = normalized_mutual_info_score(true_labels, labels_km)
    homo_km, comp_km, v_km = homogeneity_completeness_v_measure(true_labels, labels_km)
    pur_km = calculate_purity(true_labels, labels_km)
    sil_km = silhouette_score(X_2d, labels_km)
    db_km = davies_bouldin_score(X_2d, labels_km)
    
    results.append({
        'Pipeline': pipe_name,
        'Method': 'KMeans (K=5)',
        'Scope': 'Full Corpus',
        'Num_Clusters': 5,
        'ARI': round(ari_km, 4),
        'NMI': round(nmi_km, 4),
        'Homogeneity': round(homo_km, 4),
        'Completeness': round(comp_km, 4),
        'V_Measure': round(v_km, 4),
        'Purity': round(pur_km, 4),
        'Silhouette': round(sil_km, 4),
        'Davies_Bouldin': round(db_km, 4)
    })
    heatmaps_data[f"{pipe_name}_KMeans"] = (true_labels, labels_km)
    
    # 2. Hierarchical (K=5)
    hier = AgglomerativeClustering(n_clusters=5, linkage='ward')
    labels_hier = hier.fit_predict(X_2d)
    ari_hier = adjusted_rand_score(true_labels, labels_hier)
    nmi_hier = normalized_mutual_info_score(true_labels, labels_hier)
    homo_hier, comp_hier, v_hier = homogeneity_completeness_v_measure(true_labels, labels_hier)
    pur_hier = calculate_purity(true_labels, labels_hier)
    sil_hier = silhouette_score(X_2d, labels_hier)
    db_hier = davies_bouldin_score(X_2d, labels_hier)
    
    results.append({
        'Pipeline': pipe_name,
        'Method': 'Hierarchical (K=5)',
        'Scope': 'Full Corpus',
        'Num_Clusters': 5,
        'ARI': round(ari_hier, 4),
        'NMI': round(nmi_hier, 4),
        'Homogeneity': round(homo_hier, 4),
        'Completeness': round(comp_hier, 4),
        'V_Measure': round(v_hier, 4),
        'Purity': round(pur_hier, 4),
        'Silhouette': round(sil_hier, 4),
        'Davies_Bouldin': round(db_hier, 4)
    })
    
    # 3. HDBSCAN
    hdb = hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, metric='euclidean')
    labels_hdb = hdb.fit_predict(X_2d)
    n_clusters = len(set(labels_hdb)) - (1 if -1 in labels_hdb else 0)
    
    # 3a. Strict Non-Noise
    mask_non_noise = labels_hdb != -1
    y_true_nn = true_labels[mask_non_noise]
    labels_hdb_nn = labels_hdb[mask_non_noise]
    X_2d_nn = X_2d[mask_non_noise]
    
    ari_hdb_nn = adjusted_rand_score(y_true_nn, labels_hdb_nn)
    nmi_hdb_nn = normalized_mutual_info_score(y_true_nn, labels_hdb_nn)
    homo_hdb_nn, comp_hdb_nn, v_hdb_nn = homogeneity_completeness_v_measure(y_true_nn, labels_hdb_nn)
    pur_hdb_nn = calculate_purity(y_true_nn, labels_hdb_nn)
    sil_hdb_nn = silhouette_score(X_2d_nn, labels_hdb_nn)
    db_hdb_nn = davies_bouldin_score(X_2d_nn, labels_hdb_nn)
    
    results.append({
        'Pipeline': pipe_name,
        'Method': 'HDBSCAN',
        'Scope': 'Non-Noise Subset',
        'Num_Clusters': n_clusters,
        'ARI': round(ari_hdb_nn, 4),
        'NMI': round(nmi_hdb_nn, 4),
        'Homogeneity': round(homo_hdb_nn, 4),
        'Completeness': round(comp_hdb_nn, 4),
        'V_Measure': round(v_hdb_nn, 4),
        'Purity': round(pur_hdb_nn, 4),
        'Silhouette': round(sil_hdb_nn, 4),
        'Davies_Bouldin': round(db_hdb_nn, 4)
    })
    
    # 3b. Full Corpus (Noise as label -1)
    ari_hdb_all = adjusted_rand_score(true_labels, labels_hdb)
    nmi_hdb_all = normalized_mutual_info_score(true_labels, labels_hdb)
    homo_hdb_all, comp_hdb_all, v_hdb_all = homogeneity_completeness_v_measure(true_labels, labels_hdb)
    pur_hdb_all = calculate_purity(true_labels, labels_hdb)
    
    results.append({
        'Pipeline': pipe_name,
        'Method': 'HDBSCAN',
        'Scope': 'Full (with Noise)',
        'Num_Clusters': n_clusters,
        'ARI': round(ari_hdb_all, 4),
        'NMI': round(nmi_hdb_all, 4),
        'Homogeneity': round(homo_hdb_all, 4),
        'Completeness': round(comp_hdb_all, 4),
        'V_Measure': round(v_hdb_all, 4),
        'Purity': round(pur_hdb_all, 4),
        'Silhouette': round(sil_hdb_nn, 4),
        'Davies_Bouldin': round(db_hdb_nn, 4)
    })

# Save Metrics CSV
res_df = pd.DataFrame(results)
res_df.to_csv("external_disease_alignment_metrics.csv", index=False)
print("\n--- Summary Results ---")
print(res_df.to_string())

# Plot Confusion / Crosstab Heatmaps
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for idx, (title, (y_true, y_pred)) in enumerate(heatmaps_data.items()):
    ct = pd.crosstab(y_true, y_pred, normalize='index') * 100
    sns.heatmap(ct, annot=True, fmt=".1f", cmap="Blues", cbar=True, ax=axes[idx])
    axes[idx].set_title(f"Disease Class Distribution (% per Category): {title}", fontsize=12, fontweight='bold')
    axes[idx].set_xlabel("Cluster ID", fontsize=10)
    axes[idx].set_ylabel("Ground-Truth Disease Query", fontsize=10)

plt.tight_layout()
plt.savefig("disease_alignment_heatmaps.png", dpi=300)
print("Saved external_disease_alignment_metrics.csv and disease_alignment_heatmaps.png")
