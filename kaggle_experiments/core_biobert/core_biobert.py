import os
import sys
import subprocess

print("Installing required packages (umap-learn, hdbscan)...")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "umap-learn", "hdbscan"], check=False)

import re
import nltk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score
import umap
import hdbscan
import warnings

warnings.filterwarnings('ignore')

# Visual style setup
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

OUT_DIR = "."

print("\n=== STEP 1: Data Loading ===")
data_url = "https://huggingface.co/datasets/MohsinElis/pubmed-disease-mapping/resolve/main/pubmed_dataset.csv"
print(f"Fetching dataset from {data_url}...")
try:
    df = pd.read_csv("pubmed_dataset.csv")
except Exception:
    df = pd.read_csv(data_url)

print(f"Dataset loaded: {df.shape[0]} documents")
df.to_csv(os.path.join(OUT_DIR, "step1_raw_data.csv"), index=False)

# Graph 1: Document length distribution (Raw)
df['raw_length'] = df['Abstract'].fillna('').apply(lambda x: len(x.split()))
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
ax.hist(df['raw_length'], bins=50, color='darkseagreen', edgecolor='white', alpha=0.85)
ax.set_title('Step 1 – Raw Document Word Count Distribution', fontweight='bold', fontsize=13)
ax.set_xlabel('Words per Abstract', fontsize=11)
ax.set_ylabel('Frequency', fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'step1_raw_length_distribution.png'), dpi=300)
plt.close()

print("\n=== STEP 2: Preprocessing ===")
try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except Exception:
    nltk.download('stopwords', quiet=True)
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    tokens = [t for t in text.split() if t not in stop_words and len(t) > 2]
    return " ".join(tokens)

print("Preprocessing abstracts...")
df['Cleaned_Abstract'] = df['Abstract'].apply(preprocess_text)
df = df[df['Cleaned_Abstract'].str.strip() != ""].copy().reset_index(drop=True)
print(f"Cleaned corpus size: {len(df)}")
df.to_csv(os.path.join(OUT_DIR, 'step2_cleaned_corpus.csv'), index=False)

# Graph 2: Token length distribution after cleaning
df['clean_length'] = df['Cleaned_Abstract'].apply(lambda x: len(x.split()))
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
ax.hist(df['clean_length'], bins=50, color='steelblue', edgecolor='white', alpha=0.85)
ax.set_title('Step 2 – Cleaned Token Count Distribution', fontweight='bold', fontsize=13)
ax.set_xlabel('Tokens per Abstract', fontsize=11)
ax.set_ylabel('Frequency', fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'step2_preprocessing_stats.png'), dpi=300)
plt.close()

print("\n=== STEP 3: BioBERT Feature Extraction (GPU) ===")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"BioBERT extraction utilizing: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

MODEL_NAME = "dmis-lab/biobert-v1.1"
print(f"Loading {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME).to(device)
model.eval()

BATCH_SIZE = 64 if torch.cuda.is_available() else 16
texts = df['Cleaned_Abstract'].tolist()
embeddings = []

print(f"Extracting 768-dim embeddings in batches of {BATCH_SIZE}...")
with torch.no_grad():
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i+BATCH_SIZE]
        inputs = tokenizer(batch_texts, padding=True, truncation=True, max_length=128, return_tensors="pt").to(device)
        outputs = model(**inputs)
        attention_mask = inputs['attention_mask'].unsqueeze(-1).expand(outputs.last_hidden_state.size()).float()
        sum_embeddings = torch.sum(outputs.last_hidden_state * attention_mask, 1)
        sum_mask = torch.clamp(attention_mask.sum(1), min=1e-9)
        mean_pooled = sum_embeddings / sum_mask
        embeddings.append(mean_pooled.cpu().numpy())

embeddings_matrix = np.vstack(embeddings)
X_norm = normalize(embeddings_matrix, norm='l2')
print(f"BioBERT embedding matrix shape: {embeddings_matrix.shape}")

# Save sample CSV
pd.DataFrame(embeddings_matrix[:100]).to_csv(os.path.join(OUT_DIR, 'step3_biobert_sample.csv'), index=False)

# Graph 3: Correlation matrix of first 50 embedding dimensions
corr_mat = np.corrcoef(X_norm[:500, :50].T)
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
sns.heatmap(corr_mat, cmap='coolwarm', center=0, ax=ax, cbar_kws={'label': 'Pearson Correlation'})
ax.set_title('Step 3 – BioBERT Dimensions Correlation (First 50 Dimensions)', fontweight='bold', fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'step3_biobert_correlation.png'), dpi=300)
plt.close()

print("\n=== STEP 4: Contrastive Learning / Centroid Diagnostics ===")
km_pseudo = KMeans(n_clusters=10, random_state=42, n_init=5)
pseudo_labels = km_pseudo.fit_predict(X_norm)

unique_concepts = np.unique(pseudo_labels)
centroids = {}
for concept in unique_concepts:
    mask = pseudo_labels == concept
    centroids[concept] = np.asarray(X_norm[mask].mean(axis=0)).flatten()

centroid_matrix = np.stack([centroids[c] for c in unique_concepts])
sim_matrix = cosine_similarity(centroid_matrix)
sim_df = pd.DataFrame(sim_matrix, index=[f'Anchor_{c}' for c in unique_concepts], 
                      columns=[f'Anchor_{c}' for c in unique_concepts])
sim_df.to_csv(os.path.join(OUT_DIR, 'step4_inter_concept_similarity.csv'))

# Graph 4: Contrastive Similarity Heatmap
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
sns.heatmap(sim_df.values, xticklabels=sim_df.columns, yticklabels=sim_df.index,
            annot=True, fmt='.2f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Cosine Similarity'})
ax.set_title('Step 4 – Inter-Anchor Cosine Similarity (Contrastive BioBERT)', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'step4_inter_concept_similarity.png'), dpi=300)
plt.close()

print("\n=== STEP 5: UMAP Dimensionality Reduction ===")
reducer_2d = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42)
print("Fitting 2-D UMAP on BioBERT manifold...")
embedding_2d = reducer_2d.fit_transform(X_norm)

umap_df = pd.DataFrame(embedding_2d, columns=['UMAP1', 'UMAP2'])
umap_df.to_csv(os.path.join(OUT_DIR, 'step5_umap_embeddings.csv'), index=False)

# Graph 5: Raw UMAP
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
ax.scatter(embedding_2d[:, 0], embedding_2d[:, 1], alpha=0.3, s=5, color='gray')
ax.set_title('Step 5 – UMAP 2-D Projection (BioBERT Embeddings)', fontsize=13, fontweight='bold')
ax.set_xlabel('UMAP1', fontsize=11); ax.set_ylabel('UMAP2', fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'step5_umap2d_unlabeled.png'), dpi=300)
plt.close()

print("\n=== STEP 6: Automated K Selection & Clustering ===")
inertias = []
k_range = list(range(2, 16))
for k in k_range:
    km_tmp = KMeans(n_clusters=k, random_state=42, n_init=10)
    km_tmp.fit(embedding_2d)
    inertias.append(km_tmp.inertia_)

p1 = np.array([k_range[0], inertias[0]])
p2 = np.array([k_range[-1], inertias[-1]])
distances = []
for i in range(len(k_range)):
    p0 = np.array([k_range[i], inertias[i]])
    dist = np.abs(np.cross(p2 - p1, p1 - p0)) / np.linalg.norm(p2 - p1)
    distances.append(dist)

OPTIMAL_K = k_range[np.argmax(distances)]
print(f"--> Automated Elbow Optimal K = {OPTIMAL_K}")

# Graph 6a: Elbow Method
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
ax.plot(k_range, inertias, marker='o', color='steelblue', lw=2)
ax.axvline(OPTIMAL_K, ls='--', color='red', label=f'Optimal K = {OPTIMAL_K}')
ax.set_title('Step 6a – Elbow Method for Optimal K (BioBERT)', fontweight='bold', fontsize=14)
ax.set_xlabel('Number of Clusters (K)', fontsize=11); ax.set_ylabel('Inertia', fontsize=11)
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'step6a_automated_elbow_method.png'), dpi=300)
plt.close()

# Multi-algorithm clustering
print(f"Running KMeans (K={OPTIMAL_K})...")
km = KMeans(n_clusters=OPTIMAL_K, random_state=42, n_init=20)
km_labels = km.fit_predict(embedding_2d)

print("Running HDBSCAN...")
hdb = hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, metric='euclidean')
hdb_labels = hdb.fit_predict(embedding_2d)

print(f"Running Hierarchical Clustering (K={OPTIMAL_K})...")
hc = AgglomerativeClustering(n_clusters=OPTIMAL_K, linkage='ward')
hc_labels = hc.fit_predict(embedding_2d)

df['KMeans_Cluster'] = km_labels
df['HDBSCAN_Cluster'] = hdb_labels
df['Hierarchical_Cluster'] = hc_labels
df[['PMID', 'KMeans_Cluster', 'HDBSCAN_Cluster', 'Hierarchical_Cluster']].to_csv(
    os.path.join(OUT_DIR, 'step6_cluster_assignments.csv'), index=False)

# Graph 6b: Sub-plots of Clusters
def plot_clusters(ax, emb, labels, title):
    unique = set(labels)
    cmap = plt.get_cmap('tab10', max(len(unique), 1))
    for i, cid in enumerate(unique):
        mask = labels == cid
        color = 'lightgray' if cid == -1 else cmap(i/len(unique))
        ax.scatter(emb[mask, 0], emb[mask, 1], c=[color], alpha=0.5, s=5)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xticks([]); ax.set_yticks([])

fig, axes = plt.subplots(1, 3, figsize=(18, 5), dpi=300)
plot_clusters(axes[0], embedding_2d, km_labels, f'KMeans (K={OPTIMAL_K})')
plot_clusters(axes[1], embedding_2d, hdb_labels, f'HDBSCAN ({len(set(hdb_labels)-(set([-1])))} clusters)')
plot_clusters(axes[2], embedding_2d, hc_labels, f'Hierarchical (K={OPTIMAL_K})')
plt.suptitle('Step 6b – Clustering Results on BioBERT-UMAP Embedding', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'step6b_cluster_umap_all.png'), dpi=300)
plt.close()

print("\n=== STEP 7: Topic Analysis (c-TF-IDF) ===")
topic_records = []
for cluster_id in sorted(set(km_labels)):
    mask = km_labels == cluster_id
    texts = df.loc[mask, 'Cleaned_Abstract'].values
    if len(texts) < 5: continue
    cv = CountVectorizer(max_features=500, min_df=2, stop_words='english')
    try:
        cv_mat = cv.fit_transform(texts)
    except ValueError:
        continue
    freq = np.asarray(cv_mat.sum(axis=0)).flatten()
    words = cv.get_feature_names_out()
    top_idx = freq.argsort()[-15:][::-1]
    
    for rank, idx in enumerate(top_idx):
        topic_records.append({'Cluster': cluster_id, 'Rank': rank + 1, 'Topic_Keyword': words[idx], 'Frequency': int(freq[idx])})

topic_df = pd.DataFrame(topic_records)
topic_df.to_csv(os.path.join(OUT_DIR, 'step7_topic_keywords_per_cluster.csv'), index=False)

# Graph 7: Topic keywords per cluster
clusters = topic_df['Cluster'].unique()
ncols = 2
nrows = int(np.ceil(len(clusters) / ncols))
fig, axes = plt.subplots(nrows, ncols, figsize=(14, nrows * 3.2), dpi=300)
axes = axes.flatten()
for i, cid in enumerate(clusters):
    sub = topic_df[topic_df['Cluster'] == cid].head(8)
    axes[i].barh(sub['Topic_Keyword'][::-1], sub['Frequency'][::-1], color='mediumseagreen')
    axes[i].set_title(f'Cluster {cid}', fontsize=10, fontweight='bold')
for j in range(i+1, len(axes)): axes[j].set_visible(False)
plt.suptitle('Step 7 – Topic Analysis: Top Keywords per Cluster', fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'step7_topic_keywords_grid.png'), dpi=300, bbox_inches='tight')
plt.close()

print("\n=== STEP 8: Evaluation Metrics ===")
def eval_metrics_unsup(emb, pred):
    valid = pred != -1
    if valid.sum() < 2 or len(set(pred[valid])) < 2:
        return {'Silhouette': np.nan, 'Davies_Bouldin': np.nan}
    return {
        'Silhouette': round(silhouette_score(emb[valid], pred[valid]), 4),
        'Davies_Bouldin': round(davies_bouldin_score(emb[valid], pred[valid]), 4)
    }

methods = {'KMeans': km_labels, 'HDBSCAN': hdb_labels, 'Hierarchical': hc_labels}
eval_rows = []
for name, pred in methods.items():
    m = eval_metrics_unsup(embedding_2d, pred)
    m['Method'] = name
    eval_rows.append(m)

eval_df = pd.DataFrame(eval_rows)
eval_df.to_csv(os.path.join(OUT_DIR, 'step8_evaluation_metrics.csv'), index=False)
print(eval_df)

# Graph 8: Evaluation Metrics Bar Chart
fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
sns.barplot(data=eval_df, x='Method', y='Silhouette', palette='viridis', ax=axes[0])
axes[0].set_title('Step 8 – Silhouette Score (Higher is Better)', fontweight='bold')
sns.barplot(data=eval_df, x='Method', y='Davies_Bouldin', palette='magma', ax=axes[1])
axes[1].set_title('Step 8 – Davies-Bouldin Index (Lower is Better)', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'step8_evaluation_metrics.png'), dpi=300)
plt.close()

print("\n=== STEP 9: Keyword Extraction per Cluster ===")
kw_cluster_records = []
for cid in sorted(set(km_labels)):
    mask = km_labels == cid
    cluster_texts = df.loc[mask, 'Cleaned_Abstract'].values
    cluster_tfidf = TfidfVectorizer(max_features=200, min_df=1, stop_words='english')
    try:
        mat = cluster_tfidf.fit_transform(cluster_texts)
    except ValueError: continue
    mean_scores = np.asarray(mat.mean(axis=0)).flatten()
    top_idx = mean_scores.argsort()[-15:][::-1]
    feats = cluster_tfidf.get_feature_names_out()
    for rank, idx in enumerate(top_idx):
        kw_cluster_records.append({'Cluster': cid, 'Rank': rank + 1, 'Keyword': feats[idx], 'TF_IDF_Score': round(mean_scores[idx], 6)})

kw_cluster_df = pd.DataFrame(kw_cluster_records)
kw_cluster_df.to_csv(os.path.join(OUT_DIR, 'step9_keywords_per_cluster.csv'), index=False)

# Graph 9: Keyword scores
fig, axes = plt.subplots(1, len(set(km_labels)), figsize=(20, 5), dpi=300)
for i, cid in enumerate(sorted(set(km_labels))):
    sub = kw_cluster_df[kw_cluster_df['Cluster'] == cid].head(10)
    axes[i].barh(sub['Keyword'][::-1], sub['TF_IDF_Score'][::-1], color=sns.color_palette("coolwarm", 10))
    axes[i].set_title(f'Cluster {cid}', fontsize=10, fontweight='bold')
plt.suptitle('Step 9 – Top Cluster Keywords for BioBERT Clusters', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'step9_cluster_keywords.png'), dpi=300, bbox_inches='tight')
plt.close()

print("\n=== STEP 10: Automated Disease Knowledge Mapping ===")
def map_clusters_to_keywords(labels):
    mapping = {}
    for cid in set(labels):
        if cid == -1:
            mapping[cid] = "Noise"
            continue
        mask = labels == cid
        texts = df.loc[mask, 'Cleaned_Abstract'].values
        vec = TfidfVectorizer(max_features=100, stop_words='english')
        try:
            mat = vec.fit_transform(texts)
            scores = np.asarray(mat.mean(axis=0)).flatten()
            top_words = vec.get_feature_names_out()[scores.argsort()[-2:][::-1]]
            disease_name = " & ".join([w.title() for w in top_words])
            mapping[cid] = disease_name
        except:
            mapping[cid] = f"Topic {cid}"
    return mapping

km_mapping = map_clusters_to_keywords(km_labels)
hdb_mapping = map_clusters_to_keywords(hdb_labels)
hc_mapping = map_clusters_to_keywords(hc_labels)

mapped_df = pd.DataFrame(list(km_mapping.items()), columns=['Cluster', 'Automated_Disease_Topic'])
mapped_df.to_csv(os.path.join(OUT_DIR, 'step10_disease_knowledge_mapping.csv'), index=False)

# Graph 10: Mapping visualization
fig, ax = plt.subplots(figsize=(8, len(mapped_df)*0.5 + 1), dpi=300)
ax.axis('off')
table = ax.table(cellText=mapped_df.values, colLabels=mapped_df.columns, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 2)
plt.title('Step 10 – Automated Disease Mapping (BioBERT KMeans)', fontweight='bold', fontsize=14)
plt.savefig(os.path.join(OUT_DIR, 'step10_disease_knowledge_mapping.png'), dpi=300, bbox_inches='tight')
plt.close()

print("\n=== STEP 11: Final Visualization ===")
def plot_mapped_umap(ax, emb, labels, mapping, title):
    unique_clusters = set(labels)
    cmap = plt.get_cmap('tab20', max(len(unique_clusters), 1))
    
    for i, cid in enumerate(unique_clusters):
        mask = (labels == cid)
        color = 'lightgray' if cid == -1 else cmap(i / len(unique_clusters))
        label_name = mapping[cid]
        ax.scatter(emb[mask, 0], emb[mask, 1], c=[color], alpha=0.5, s=5)
        
        if cid != -1:
            centroid_x = emb[mask, 0].mean()
            centroid_y = emb[mask, 1].mean()
            ax.text(centroid_x, centroid_y, label_name, 
                    fontsize=11, fontweight='bold', ha='center', va='center',
                    bbox=dict(facecolor='white', alpha=0.85, edgecolor='black', boxstyle='round,pad=0.3'))
            
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks([]); ax.set_yticks([])

fig, axes = plt.subplots(1, 3, figsize=(24, 8), dpi=300)
axes = axes.flatten()

plot_mapped_umap(axes[0], embedding_2d, km_labels, km_mapping, f"KMeans Clusters (K={OPTIMAL_K})")
plot_mapped_umap(axes[1], embedding_2d, hdb_labels, hdb_mapping, "HDBSCAN Clusters")
plot_mapped_umap(axes[2], embedding_2d, hc_labels, hc_mapping, f"Hierarchical Clusters (K={OPTIMAL_K})")

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'step11_final_mapped_umap_all_algorithms.png'), dpi=300, bbox_inches='tight')
plt.close()

print("BioBERT Pipeline Complete! All CSVs and 300 DPI figures saved.")
