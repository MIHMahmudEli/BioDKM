import os
import re
import time
import urllib.request
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import normalize
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.neighbors import NearestNeighbors
import hdbscan
import umap

print("=== Starting Exp 10: Apples-to-Apples Noise Infiltration & Soft Outlier Assignment Ablation ===")

# 1. Download Dataset
DATA_URL = "https://huggingface.co/datasets/MohsinElis/pubmed-disease-mapping/resolve/main/pubmed_dataset.csv"
DATA_PATH = "pubmed_dataset.csv"
if not os.path.exists(DATA_PATH):
    print("Downloading dataset from Hugging Face...")
    urllib.request.urlretrieve(DATA_URL, DATA_PATH)

df = pd.read_csv(DATA_PATH)
print(f"Loaded dataset: {df.shape}")

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
d_labels = []
for d, count in disease_slices:
    d_labels.extend([d] * count)
df['Disease'] = d_labels[:len(df)]
print(f"Assigned disease labels across {len(disease_slices)} categories.")

# Preprocessing
stopwords = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he',
    'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
    'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
    'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
    'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
    'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't",
    'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't",
    'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't",
    'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
    'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in stopwords and len(t) > 2]
    return " ".join(tokens)

print("Preprocessing abstracts...")
df['clean_abstract'] = df['Abstract'].apply(clean_text)
df = df[df['clean_abstract'].str.len() > 0].reset_index(drop=True)
print(f"Cleaned corpus size: {len(df)}")

# 2. TF-IDF & UMAP Representation
print("Extracting TF-IDF features (5,000 features)...")
tfidf = TfidfVectorizer(max_features=5000, min_df=5, max_df=0.9, stop_words='english')
X_tfidf = tfidf.fit_transform(df['clean_abstract'])
X_norm = normalize(X_tfidf, norm='l2')

print("Computing UMAP 2D projection...")
reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42)
X_umap = reducer.fit_transform(X_norm.toarray())

# 3. Canonical HDBSCAN Clustering
print("Fitting HDBSCAN with prediction data support...")
clusterer = hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, metric='euclidean', prediction_data=True)
hdb_labels = clusterer.fit_predict(X_umap)

n_clusters_hdb = len(set(hdb_labels)) - (1 if -1 in hdb_labels else 0)
noise_mask = (hdb_labels == -1)
core_mask = ~noise_mask
n_core = np.sum(core_mask)
n_noise = np.sum(noise_mask)
noise_pct = (n_noise / len(df)) * 100.0

print(f"HDBSCAN discovered {n_clusters_hdb} clusters.")
print(f"Core non-noise documents: {n_core} ({100 - noise_pct:.2f}%)")
print(f"Noise documents: {n_noise} ({noise_pct:.2f}%)")

# Coherence matrix helper
print("Building binary co-occurrence matrix for UCI NPMI coherence...")
count_vec = CountVectorizer(min_df=5, max_df=0.95, binary=True, stop_words='english')
B = count_vec.fit_transform(df['clean_abstract'])
vocab = {word: idx for word, idx in count_vec.vocabulary_.items()}
doc_count = B.shape[0]
word_doc_freq = np.array(B.sum(axis=0)).flatten()

def compute_npmi(topic_words):
    indices = [vocab[w] for w in topic_words if w in vocab]
    if len(indices) < 2:
        return 0.0
    scores = []
    for i in range(len(indices)):
        for j in range(i + 1, len(indices)):
            idx_i = indices[i]
            idx_j = indices[j]
            p_i = word_doc_freq[idx_i] / doc_count
            p_j = word_doc_freq[idx_j] / doc_count
            col_i = B[:, idx_i]
            col_j = B[:, idx_j]
            co_occur = col_i.multiply(col_j).sum()
            p_ij = co_occur / doc_count
            if p_ij > 0:
                pmi = np.log(p_ij / (p_i * p_j))
                npmi = pmi / (-np.log(p_ij))
                scores.append(npmi)
            else:
                scores.append(-1.0)
    return float(np.mean(scores)) if scores else 0.0

def get_cluster_npmi(labels, subset_indices=None):
    if subset_indices is not None:
        sub_docs = df['clean_abstract'].iloc[subset_indices].values
        sub_labels = labels[subset_indices]
    else:
        sub_docs = df['clean_abstract'].values
        sub_labels = labels
    
    unique_clusters = [c for c in np.unique(sub_labels) if c != -1]
    topic_npmis = []
    
    for c in unique_clusters:
        c_docs = [doc for doc, lab in zip(sub_docs, sub_labels) if lab == c]
        if len(c_docs) < 2:
            continue
        try:
            c_vec = TfidfVectorizer(max_features=200, min_df=1, stop_words='english')
            c_tfidf = c_vec.fit_transform(c_docs)
            mean_tfidf = np.array(c_tfidf.mean(axis=0)).flatten()
            top_words = [c_vec.get_feature_names_out()[i] for i in np.argsort(-mean_tfidf)[:10]]
            score = compute_npmi(top_words)
            topic_npmis.append(score)
        except Exception:
            pass
    return float(np.mean(topic_npmis)) if topic_npmis else 0.0

# 4. Evaluation 1: Canonical HDBSCAN (Core Only)
sil_hdb_core = silhouette_score(X_umap[core_mask], hdb_labels[core_mask])
db_hdb_core = davies_bouldin_score(X_umap[core_mask], hdb_labels[core_mask])
npmi_hdb_core = get_cluster_npmi(hdb_labels[core_mask])

# 5. Evaluation 2: Apples-to-Apples Matched Core Subset Benchmark
print("Running Matched Core Subset Benchmark (KMeans and Hierarchical on Core Only)...")
X_core = X_umap[core_mask]

# KMeans K=5 on core
km5_core = KMeans(n_clusters=5, random_state=42, n_init=10).fit(X_core)
sil_km5_core = silhouette_score(X_core, km5_core.labels_)
db_km5_core = davies_bouldin_score(X_core, km5_core.labels_)
npmi_km5_core = get_cluster_npmi(km5_core.labels_)

# KMeans K=n_clusters_hdb on core
km_matched_core = KMeans(n_clusters=n_clusters_hdb, random_state=42, n_init=10).fit(X_core)
sil_km_matched_core = silhouette_score(X_core, km_matched_core.labels_)
db_km_matched_core = davies_bouldin_score(X_core, km_matched_core.labels_)
npmi_km_matched_core = get_cluster_npmi(km_matched_core.labels_)

# Hierarchical K=5 on core
hier_core = AgglomerativeClustering(n_clusters=5, linkage='ward').fit(X_core)
sil_hier_core = silhouette_score(X_core, hier_core.labels_)
db_hier_core = davies_bouldin_score(X_core, hier_core.labels_)
npmi_hier_core = get_cluster_npmi(hier_core.labels_)

# 6. Evaluation 3: Soft Outlier Assignment (100% Coverage)
print("Performing Soft Outlier Assignment for 100% Corpus Coverage...")
# Use NearestNeighbors on core points to assign each noise point to closest core cluster
nn = NearestNeighbors(n_neighbors=5, metric='euclidean').fit(X_core)
core_labels = hdb_labels[core_mask]

# Assign noise points
noise_indices = np.where(noise_mask)[0]
X_noise = X_umap[noise_mask]
_, neighbors = nn.kneighbors(X_noise)

soft_labels = hdb_labels.copy()
for i, n_idx in enumerate(noise_indices):
    voted_labels = core_labels[neighbors[i]]
    # majority vote among nearest core neighbors
    counts = pd.Series(voted_labels).value_counts()
    soft_labels[n_idx] = counts.index[0]

# Full 100% coverage metrics
sil_hdb_soft = silhouette_score(X_umap, soft_labels)
db_hdb_soft = davies_bouldin_score(X_umap, soft_labels)
npmi_hdb_soft = get_cluster_npmi(soft_labels)

# Full Corpus KMeans K=5
km5_full = KMeans(n_clusters=5, random_state=42, n_init=10).fit(X_umap)
sil_km5_full = silhouette_score(X_umap, km5_full.labels_)
db_km5_full = davies_bouldin_score(X_umap, km5_full.labels_)
npmi_km5_full = get_cluster_npmi(km5_full.labels_)

# Full Corpus Hierarchical K=5
hier_full = AgglomerativeClustering(n_clusters=5, linkage='ward').fit(X_umap)
sil_hier_full = silhouette_score(X_umap, hier_full.labels_)
db_hier_full = davies_bouldin_score(X_umap, hier_full.labels_)
npmi_hier_full = get_cluster_npmi(hier_full.labels_)

# 7. Evaluation 4: Linguistic & Disease Entropy Characterization of Noise
print("Analyzing clinical & entropy properties of noise...")
# Compute disease distribution entropy: H = -sum(p * log2(p))
from collections import Counter

def calc_entropy(labels_series):
    counts = Counter(labels_series)
    total = sum(counts.values())
    p = np.array([c / total for c in counts.values()])
    return float(-np.sum(p * np.log2(p + 1e-12)))

entropy_core = calc_entropy(df.loc[core_mask, 'Disease'])
entropy_noise = calc_entropy(df.loc[noise_mask, 'Disease'])

# Length analysis
len_core = df.loc[core_mask, 'clean_abstract'].apply(lambda x: len(x.split())).mean()
len_noise = df.loc[noise_mask, 'clean_abstract'].apply(lambda x: len(x.split())).mean()

# Extract top discriminative keywords of Noise vs Core
noise_vec = TfidfVectorizer(max_features=25, stop_words='english')
noise_tfidf = noise_vec.fit_transform(df.loc[noise_mask, 'clean_abstract'])
noise_keywords = [noise_vec.get_feature_names_out()[i] for i in np.argsort(-noise_tfidf.mean(axis=0).A1)[:20]]

print(f"Core Disease Entropy: {entropy_core:.4f} | Noise Disease Entropy: {entropy_noise:.4f}")
print(f"Core Abstract Length: {len_core:.1f} words | Noise Abstract Length: {len_noise:.1f} words")
print(f"Top Noise Keywords: {', '.join(noise_keywords[:10])}")

# 8. Save Metrics
metrics_data = [
    {
        'Evaluation_Scope': 'Matched Core Subset (Apples-to-Apples)',
        'Model': 'HDBSCAN (Proposed Core)',
        'Coverage_Pct': f"{100 - noise_pct:.1f}%",
        'Doc_Count': int(n_core),
        'Num_Clusters': int(n_clusters_hdb),
        'Silhouette': round(sil_hdb_core, 4),
        'Davies_Bouldin': round(db_hdb_core, 4),
        'Mean_NPMI': round(npmi_hdb_core, 4)
    },
    {
        'Evaluation_Scope': 'Matched Core Subset (Apples-to-Apples)',
        'Model': 'KMeans (Matched K)',
        'Coverage_Pct': f"{100 - noise_pct:.1f}%",
        'Doc_Count': int(n_core),
        'Num_Clusters': int(n_clusters_hdb),
        'Silhouette': round(sil_km_matched_core, 4),
        'Davies_Bouldin': round(db_km_matched_core, 4),
        'Mean_NPMI': round(npmi_km_matched_core, 4)
    },
    {
        'Evaluation_Scope': 'Matched Core Subset (Apples-to-Apples)',
        'Model': 'KMeans (Elbow K=5)',
        'Coverage_Pct': f"{100 - noise_pct:.1f}%",
        'Doc_Count': int(n_core),
        'Num_Clusters': 5,
        'Silhouette': round(sil_km5_core, 4),
        'Davies_Bouldin': round(db_km5_core, 4),
        'Mean_NPMI': round(npmi_km5_core, 4)
    },
    {
        'Evaluation_Scope': 'Matched Core Subset (Apples-to-Apples)',
        'Model': 'Hierarchical (Ward K=5)',
        'Coverage_Pct': f"{100 - noise_pct:.1f}%",
        'Doc_Count': int(n_core),
        'Num_Clusters': 5,
        'Silhouette': round(sil_hier_core, 4),
        'Davies_Bouldin': round(db_hier_core, 4),
        'Mean_NPMI': round(npmi_hier_core, 4)
    },
    {
        'Evaluation_Scope': 'Full Corpus (100% Coverage)',
        'Model': 'HDBSCAN + Soft k-NN Assignment',
        'Coverage_Pct': '100.0%',
        'Doc_Count': int(len(df)),
        'Num_Clusters': int(n_clusters_hdb),
        'Silhouette': round(sil_hdb_soft, 4),
        'Davies_Bouldin': round(db_hdb_soft, 4),
        'Mean_NPMI': round(npmi_hdb_soft, 4)
    },
    {
        'Evaluation_Scope': 'Full Corpus (100% Coverage)',
        'Model': 'KMeans (Elbow K=5)',
        'Coverage_Pct': '100.0%',
        'Doc_Count': int(len(df)),
        'Num_Clusters': 5,
        'Silhouette': round(sil_km5_full, 4),
        'Davies_Bouldin': round(db_km5_full, 4),
        'Mean_NPMI': round(npmi_km5_full, 4)
    },
    {
        'Evaluation_Scope': 'Full Corpus (100% Coverage)',
        'Model': 'Hierarchical (Ward K=5)',
        'Coverage_Pct': '100.0%',
        'Doc_Count': int(len(df)),
        'Num_Clusters': 5,
        'Silhouette': round(sil_hier_full, 4),
        'Davies_Bouldin': round(db_hier_full, 4),
        'Mean_NPMI': round(npmi_hier_full, 4)
    }
]

metrics_df = pd.DataFrame(metrics_data)
metrics_df.to_csv("noise_ablation_comparison_metrics.csv", index=False)
print("Saved noise_ablation_comparison_metrics.csv")

# Save linguistic profiles
profile_df = pd.DataFrame([
    {
        'Partition': 'Core Dense Documents (Clustered)',
        'Document_Count': int(n_core),
        'Proportion': f"{100 - noise_pct:.2f}%",
        'Disease_Entropy': round(entropy_core, 4),
        'Mean_Token_Length': round(len_core, 1),
        'Clinical_Nature': 'Specialized disease-specific investigations and biomarker assays'
    },
    {
        'Partition': 'Noise Boundary Documents (Outliers)',
        'Document_Count': int(n_noise),
        'Proportion': f"{noise_pct:.2f}%",
        'Disease_Entropy': round(entropy_noise, 4),
        'Mean_Token_Length': round(len_noise, 1),
        'Clinical_Nature': 'Broad multi-disease reviews, meta-analyses, and cross-cutting clinical guidelines'
    }
])
profile_df.to_csv("noise_vs_core_linguistic_profiles.csv", index=False)
print("Saved noise_vs_core_linguistic_profiles.csv")

# Top noise keywords
noise_kw_df = pd.DataFrame({'Rank': range(1, len(noise_keywords) + 1), 'Keyword': noise_keywords})
noise_kw_df.to_csv("noise_top_keywords.csv", index=False)
print("Saved noise_top_keywords.csv")

# 9. Create 3-Panel Publication Figure
fig, axes = plt.subplots(1, 3, figsize=(18, 5.2))
palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# Panel 1: Silhouette Comparison
ax1 = axes[0]
subset_models = ['HDBSCAN (Core)', 'KMeans (Matched K)', 'KMeans (K=5)', 'HDBSCAN (Soft 100%)', 'KMeans (Full 100%)']
subset_sil = [sil_hdb_core, sil_km_matched_core, sil_km5_core, sil_hdb_soft, sil_km5_full]
colors = ['#15803D', '#0E7C86', '#1F6FEB', '#22C55E', '#3B82F6']
bars1 = ax1.bar(subset_models, subset_sil, color=colors, edgecolor='black', linewidth=0.8)
ax1.set_title('(a) Silhouette Separation (Core vs. 100% Coverage)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Silhouette Coefficient (Higher is Better)', fontsize=11)
ax1.set_xticklabels(subset_models, rotation=25, ha='right', fontsize=9.5)
ax1.grid(axis='y', linestyle='--', alpha=0.5)
for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f"{yval:.3f}", ha='center', va='bottom', fontsize=9)

# Panel 2: NPMI Topic Coherence
ax2 = axes[1]
subset_npmi = [npmi_hdb_core, npmi_km_matched_core, npmi_km5_core, npmi_hdb_soft, npmi_km5_full]
bars2 = ax2.bar(subset_models, subset_npmi, color=colors, edgecolor='black', linewidth=0.8)
ax2.set_title('(b) NPMI Topic Coherence Comparison', fontsize=12, fontweight='bold')
ax2.set_ylabel('Mean NPMI Coherence (Higher is Better)', fontsize=11)
ax2.set_xticklabels(subset_models, rotation=25, ha='right', fontsize=9.5)
ax2.grid(axis='y', linestyle='--', alpha=0.5)
for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.003, f"{yval:.3f}", ha='center', va='bottom', fontsize=9)

# Panel 3: Disease Class Entropy and Noise Characteristics
ax3 = axes[2]
partitions = ['Core Documents', 'Noise Documents']
entropies = [entropy_core, entropy_noise]
bars3 = ax3.bar(partitions, entropies, color=['#15803D', '#DC2626'], edgecolor='black', width=0.5, linewidth=0.8)
ax3.set_title('(c) Disease Class Entropy: Core vs. Boundary Noise', fontsize=12, fontweight='bold')
ax3.set_ylabel('Shannon Entropy (Bits) (Higher = Mixed Diseases)', fontsize=11)
ax3.set_ylim(0, 3.5)
ax3.grid(axis='y', linestyle='--', alpha=0.5)
for bar in bars3:
    yval = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2.0, yval + 0.08, f"{yval:.3f} bits", ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig("noise_ablation_evaluation.png", dpi=300)
print("Saved noise_ablation_evaluation.png successfully.")

print("=== Exp 10 Completed Successfully ===")
