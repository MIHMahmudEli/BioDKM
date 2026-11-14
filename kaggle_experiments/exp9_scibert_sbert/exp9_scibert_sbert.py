import os
import re
import urllib.request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import normalize
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.cluster import KMeans
import hdbscan
import umap

print("=== Starting Exp 9: SciBERT and Biomedical Sentence-Transformer Benchmark ===")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# 1. Download Dataset
DATA_URL = "https://huggingface.co/datasets/MohsinElis/pubmed-disease-mapping/resolve/main/pubmed_dataset.csv"
DATA_PATH = "pubmed_dataset.csv"
if not os.path.exists(DATA_PATH):
    print("Downloading dataset from Hugging Face...")
    urllib.request.urlretrieve(DATA_URL, DATA_PATH)

df = pd.read_csv(DATA_PATH)

# Preprocessing
stopwords = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
    'your', 'yours', 'he', 'him', 'his', 'she', 'her', 'it', 'its', 'they', 'them',
    'what', 'which', 'who', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was',
    'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'a',
    'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on',
    'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
    'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
}

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    tokens = [t for t in text.split() if t not in stopwords and len(t) > 2]
    return ' '.join(tokens)

df['clean_abstract'] = df['Abstract'].apply(clean_text)
df = df[df['clean_abstract'].str.len() > 0].reset_index(drop=True)
print(f"Preprocessed abstracts: {len(df)}")

# 2. Build Binary Co-occurrence Matrix for NPMI
count_vec = CountVectorizer(min_df=5, max_df=0.95, binary=True, stop_words='english')
doc_term = count_vec.fit_transform(df['clean_abstract'])
vocab_list = np.array(count_vec.get_feature_names_out())
word2idx = {w: i for i, w in enumerate(vocab_list)}
N_docs = doc_term.shape[0]
doc_counts = np.asarray(doc_term.sum(axis=0)).ravel()

def compute_npmi(words, top_n=10):
    valid_words = [w for w in words[:top_n] if w in word2idx]
    if len(valid_words) < 2:
        return 0.0
    indices = [word2idx[w] for w in valid_words]
    sub_dt = doc_term[:, indices].tocsc()
    p_w = doc_counts[indices] / N_docs
    pair_npmi = []
    for i in range(len(valid_words)):
        col_i = sub_dt.getcol(i)
        for j in range(i + 1, len(valid_words)):
            col_j = sub_dt.getcol(j)
            p_ij = col_i.multiply(col_j).sum() / N_docs
            if p_ij > 0:
                pmi = np.log(p_ij / (p_w[i] * p_w[j]))
                npmi = pmi / (-np.log(p_ij))
                pair_npmi.append(npmi)
            else:
                pair_npmi.append(-1.0)
    return float(np.mean(pair_npmi)) if len(pair_npmi) > 0 else 0.0

# 3. Model Extraction Helper
def extract_model_embeddings(model_name):
    print(f"\n--- Extracting: {model_name} ---")
    tok = AutoTokenizer.from_pretrained(model_name)
    m = AutoModel.from_pretrained(model_name).to(device)
    m.eval()
    
    batch_size = 64
    embs = []
    texts = df['clean_abstract'].tolist()
    
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            encoded = tok(batch, padding=True, truncation=True, max_length=128, return_tensors='pt').to(device)
            out = m(**encoded)
            mask = encoded['attention_mask'].unsqueeze(-1)
            pooled = (out.last_hidden_state * mask).sum(dim=1) / mask.sum(dim=1)
            embs.append(pooled.cpu().numpy())
            
    X = np.vstack(embs)
    return normalize(X, norm='l2')

models_to_test = {
    'SciBERT': 'allenai/scibert_scivocab_uncased',
    'Sentence-MiniLM': 'sentence-transformers/all-MiniLM-L6-v2'
}

results_rows = []
topics_rows = []

for model_label, hf_id in models_to_test.items():
    X_emb = extract_model_embeddings(hf_id)
    
    # UMAP Reduction
    reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42)
    umap_2d = reducer.fit_transform(X_emb)
    
    # KMeans (K=5)
    km = KMeans(n_clusters=5, random_state=42, n_init=20)
    km_labels = km.fit_predict(umap_2d)
    km_sil = float(silhouette_score(umap_2d, km_labels))
    km_db = float(davies_bouldin_score(umap_2d, km_labels))
    
    # HDBSCAN
    hdb = hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, metric='euclidean')
    hdb_labels = hdb.fit_predict(umap_2d)
    mask = hdb_labels != -1
    hdb_sil = float(silhouette_score(umap_2d[mask], hdb_labels[mask])) if mask.sum() > 0 else 0.0
    hdb_db = float(davies_bouldin_score(umap_2d[mask], hdb_labels[mask])) if mask.sum() > 0 else 0.0
    
    # Topic extraction & Coherence
    for method_name, labels, sil, db in [('KMeans', km_labels, km_sil, km_db), ('HDBSCAN', hdb_labels, hdb_sil, hdb_db)]:
        unique_c = sorted(set(labels))
        if -1 in unique_c:
            unique_c.remove(-1)
        
        all_top_words = []
        c_npmis = []
        
        for c in unique_c:
            c_docs = df[labels == c]['clean_abstract']
            if len(c_docs) == 0:
                continue
            vec = TfidfVectorizer(max_features=100, stop_words='english')
            t = vec.fit_transform(c_docs)
            fn = np.array(vec.get_feature_names_out())
            sc = np.asarray(t.mean(axis=0)).ravel()
            top_w = fn[sc.argsort()[::-1][:15]].tolist()
            all_top_words.extend(top_w[:10])
            
            c_npmi = compute_npmi(top_w)
            c_npmis.append(c_npmi)
            
            topics_rows.append({
                'Model': model_label,
                'Method': method_name,
                'Cluster': c,
                'Top_Words': ', '.join(top_w[:10]),
                'NPMI': round(c_npmi, 4)
            })
            
        mean_npmi = float(np.mean(c_npmis)) if len(c_npmis) > 0 else 0.0
        diversity = len(set(all_top_words)) / len(all_top_words) if len(all_top_words) > 0 else 0.0
        
        results_rows.append({
            'Model': model_label,
            'Method': method_name,
            'Num_Topics': len(unique_c),
            'Silhouette': round(sil, 4),
            'Davies_Bouldin': round(db, 4),
            'Mean_NPMI': round(mean_npmi, 4),
            'Topic_Diversity': round(diversity, 4)
        })

df_results = pd.DataFrame(results_rows)
df_topics = pd.DataFrame(topics_rows)

print("\n=== Expanded Models Evaluation Metrics ===")
print(df_results.to_string(index=False))

# Save CSVs
df_results.to_csv("expanded_models_evaluation_metrics.csv", index=False)
df_topics.to_csv("expanded_models_topics.csv", index=False)
print("Saved expanded CSV outputs.")

# Plot Comparison
fig, axes = plt.subplots(1, 3, figsize=(18, 5), dpi=300)
palette = ['#4F46E5', '#06B6D4']

sns.barplot(data=df_results, x='Model', y='Silhouette', hue='Method', palette='muted', ax=axes[0])
axes[0].set_title("(a) Cluster Separation (Silhouette)", fontsize=13, fontweight='bold', pad=10)
axes[0].set_ylabel("Silhouette Score")
axes[0].set_xlabel("")
axes[0].grid(axis='y', linestyle='--', alpha=0.5)

sns.barplot(data=df_results, x='Model', y='Mean_NPMI', hue='Method', palette='muted', ax=axes[1])
axes[1].set_title("(b) Semantic Coherence (NPMI)", fontsize=13, fontweight='bold', pad=10)
axes[1].set_ylabel("Mean NPMI Coherence")
axes[1].set_xlabel("")
axes[1].grid(axis='y', linestyle='--', alpha=0.5)

sns.barplot(data=df_results, x='Model', y='Topic_Diversity', hue='Method', palette='muted', ax=axes[2])
axes[2].set_title("(c) Topic Diversity", fontsize=13, fontweight='bold', pad=10)
axes[2].set_ylabel("Topic Diversity [0-1]")
axes[2].set_xlabel("")
axes[2].grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig("expanded_models_comparison.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved expanded_models_comparison.png")

print("=== Exp 9 Completed Successfully! ===")
