import os
import sys
import subprocess

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "umap-learn", "hdbscan", "scikit-learn"], check=False)

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.manifold import trustworthiness
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

print("--- Step 3: Feature Extraction ---")
# TF-IDF
tfidf_vec = TfidfVectorizer(max_features=5000, min_df=5, max_df=0.9, stop_words='english')
X_tfidf = normalize(tfidf_vec.fit_transform(df['clean_abstract']), norm='l2').toarray()

# BioBERT
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

print("--- Step 4: Computing Dimension Reductions ---")
dim_variants = {}

# TF-IDF variants
print("Generating TF-IDF reductions...")
dim_variants['TF-IDF_Direct_HighDim'] = ('TF-IDF', 'Direct (5000D)', X_tfidf, 1.0)

pca_tfidf_50 = PCA(n_components=50, random_state=42).fit_transform(X_tfidf)
trust_t50 = trustworthiness(X_tfidf, pca_tfidf_50, n_neighbors=15, metric='cosine')
dim_variants['TF-IDF_PCA_50D'] = ('TF-IDF', 'PCA (50D)', pca_tfidf_50, trust_t50)

pca_tfidf_2 = PCA(n_components=2, random_state=42).fit_transform(X_tfidf)
trust_t2 = trustworthiness(X_tfidf, pca_tfidf_2, n_neighbors=15, metric='cosine')
dim_variants['TF-IDF_PCA_2D'] = ('TF-IDF', 'PCA (2D)', pca_tfidf_2, trust_t2)

umap_tfidf_2 = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42).fit_transform(X_tfidf)
trust_tu2 = trustworthiness(X_tfidf, umap_tfidf_2, n_neighbors=15, metric='cosine')
dim_variants['TF-IDF_UMAP_2D'] = ('TF-IDF', 'UMAP (2D)', umap_tfidf_2, trust_tu2)

# BioBERT variants
print("Generating BioBERT reductions...")
dim_variants['BioBERT_Direct_HighDim'] = ('BioBERT', 'Direct (768D)', X_biobert, 1.0)

pca_bio_50 = PCA(n_components=50, random_state=42).fit_transform(X_biobert)
trust_b50 = trustworthiness(X_biobert, pca_bio_50, n_neighbors=15, metric='cosine')
dim_variants['BioBERT_PCA_50D'] = ('BioBERT', 'PCA (50D)', pca_bio_50, trust_b50)

pca_bio_2 = PCA(n_components=2, random_state=42).fit_transform(X_biobert)
trust_b2 = trustworthiness(X_biobert, pca_bio_2, n_neighbors=15, metric='cosine')
dim_variants['BioBERT_PCA_2D'] = ('BioBERT', 'PCA (2D)', pca_bio_2, trust_b2)

umap_bio_2 = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42).fit_transform(X_biobert)
trust_bu2 = trustworthiness(X_biobert, umap_bio_2, n_neighbors=15, metric='cosine')
dim_variants['BioBERT_UMAP_2D'] = ('BioBERT', 'UMAP (2D)', umap_bio_2, trust_bu2)

print("--- Step 5: Clustering across Reductions ---")
ablation_records = []

for key, (emb_name, red_name, X_data, trust_val) in dim_variants.items():
    print(f"Clustering {key}...")
    
    # KMeans (K=5)
    km = KMeans(n_clusters=5, n_init=10, random_state=42)
    labels_km = km.fit_predict(X_data)
    sil_km = silhouette_score(X_data, labels_km)
    db_km = davies_bouldin_score(X_data, labels_km)
    
    ablation_records.append({
        'Embedding': emb_name,
        'Reduction_Strategy': red_name,
        'Algorithm': 'KMeans (K=5)',
        'Dimensions': X_data.shape[1],
        'Num_Clusters': 5,
        'Silhouette': round(sil_km, 4),
        'Davies_Bouldin': round(db_km, 4),
        'Trustworthiness': round(trust_val, 4)
    })
    
    # HDBSCAN
    metric_to_use = 'cosine' if 'Direct' in red_name else 'euclidean'
    try:
        hdb = hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, metric=metric_to_use)
        labels_hdb = hdb.fit_predict(X_data)
        n_clusters = len(set(labels_hdb)) - (1 if -1 in labels_hdb else 0)
        mask = labels_hdb != -1
        if mask.sum() > 0 and n_clusters > 1:
            sil_hdb = silhouette_score(X_data[mask], labels_hdb[mask])
            db_hdb = davies_bouldin_score(X_data[mask], labels_hdb[mask])
        else:
            sil_hdb, db_hdb = 0.0, 9.99
    except Exception:
        n_clusters = 0
        sil_hdb, db_hdb = 0.0, 9.99
        
    ablation_records.append({
        'Embedding': emb_name,
        'Reduction_Strategy': red_name,
        'Algorithm': 'HDBSCAN',
        'Dimensions': X_data.shape[1],
        'Num_Clusters': n_clusters,
        'Silhouette': round(sil_hdb, 4),
        'Davies_Bouldin': round(db_hdb, 4),
        'Trustworthiness': round(trust_val, 4)
    })

res_df = pd.DataFrame(ablation_records)
res_df.to_csv("dim_reduction_ablation_metrics.csv", index=False)
print("\n--- Ablation Results ---")
print(res_df.to_string())

# Plot Trustworthiness & Silhouette comparison
plt.figure(figsize=(12, 5))
sub_df = res_df[res_df['Algorithm'] == 'HDBSCAN']
plt.subplot(1, 2, 1)
plt.barh(sub_df['Embedding'] + " - " + sub_df['Reduction_Strategy'], sub_df['Trustworthiness'], color='#2b5c8f', edgecolor='black')
plt.title("Neighborhood Trustworthiness Score", fontsize=11, fontweight='bold')
plt.xlabel("Trustworthiness (1.0 = Perfect Local Topology)", fontsize=10)
plt.xlim(0.5, 1.05)
plt.grid(axis='x', linestyle='--', alpha=0.6)

plt.subplot(1, 2, 2)
plt.barh(sub_df['Embedding'] + " - " + sub_df['Reduction_Strategy'], sub_df['Silhouette'], color='#38a169', edgecolor='black')
plt.title("Cluster Separation (Silhouette Score)", fontsize=11, fontweight='bold')
plt.xlabel("Silhouette Score", fontsize=10)
plt.grid(axis='x', linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig("trustworthiness_comparison.png", dpi=300)
print("Saved dim_reduction_ablation_metrics.csv and trustworthiness_comparison.png")
