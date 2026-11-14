import os
import re
import time
import urllib.request
import json
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import normalize
from sklearn.metrics import adjusted_rand_score, adjusted_mutual_info_score, silhouette_score, davies_bouldin_score
import hdbscan
import umap

print("=== Starting Exp 11: 10-Fold Subsampling Perturbation & Cluster Stability ===")

# 1. Download Dataset
DATA_URL = "https://huggingface.co/datasets/MohsinElis/pubmed-disease-mapping/resolve/main/pubmed_dataset.csv"
DATA_PATH = "pubmed_dataset.csv"
if not os.path.exists(DATA_PATH):
    print("Downloading dataset from Hugging Face...")
    urllib.request.urlretrieve(DATA_URL, DATA_PATH)

df = pd.read_csv(DATA_PATH)
print(f"Loaded dataset: {df.shape}")

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
N_total = len(df)
print(f"Cleaned corpus size: {N_total}")

# UCI NPMI Coherence setup
print("Building binary co-occurrence matrix...")
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

def extract_fold_topics(sub_df, labels):
    unique_clusters = [c for c in np.unique(labels) if c != -1]
    cluster_keywords = {}
    npmis = []
    
    for c in unique_clusters:
        c_docs = sub_df.loc[labels == c, 'clean_abstract'].values
        if len(c_docs) < 2:
            continue
        try:
            c_vec = TfidfVectorizer(max_features=200, min_df=1, stop_words='english')
            c_tfidf = c_vec.fit_transform(c_docs)
            mean_tfidf = np.array(c_tfidf.mean(axis=0)).flatten()
            top_words = [c_vec.get_feature_names_out()[i] for i in np.argsort(-mean_tfidf)[:15]]
            cluster_keywords[c] = top_words
            score = compute_npmi(top_words[:10])
            npmis.append(score)
        except Exception:
            pass
    mean_npmi = float(np.mean(npmis)) if npmis else 0.0
    return cluster_keywords, mean_npmi

# 2. 10-Fold Subsampling Setup (80% per fold)
SEEDS = [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]
subsample_ratio = 0.80
n_subsample = int(N_total * subsample_ratio)

fold_results = []
fold_indices = []
fold_labels = []
fold_topic_dicts = []

print(f"Starting 10-Fold Subsampling (80% = {n_subsample} docs per fold)...")

for fold_i, seed in enumerate(SEEDS):
    t0 = time.time()
    rng = np.random.RandomState(seed)
    sampled_idx = np.sort(rng.choice(N_total, size=n_subsample, replace=False))
    sub_df = df.iloc[sampled_idx].reset_index(drop=True)
    
    # TF-IDF
    tfidf = TfidfVectorizer(max_features=5000, min_df=5, max_df=0.9, stop_words='english')
    X_tfidf = tfidf.fit_transform(sub_df['clean_abstract'])
    X_norm = normalize(X_tfidf, norm='l2')
    
    # UMAP
    reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=seed)
    X_umap = reducer.fit_transform(X_norm.toarray())
    
    # HDBSCAN
    clusterer = hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, metric='euclidean')
    labels = clusterer.fit_predict(X_umap)
    
    core_mask = (labels != -1)
    n_clus = len(set(labels)) - (1 if -1 in labels else 0)
    sil = silhouette_score(X_umap[core_mask], labels[core_mask])
    db = davies_bouldin_score(X_umap[core_mask], labels[core_mask])
    
    # Topics & Coherence
    c_kws, mean_npmi = extract_fold_topics(sub_df, labels)
    
    fold_indices.append(sampled_idx)
    fold_labels.append(labels)
    fold_topic_dicts.append(c_kws)
    
    fold_res = {
        'Fold': fold_i + 1,
        'Seed': seed,
        'Subsample_Size': n_subsample,
        'Discovered_Clusters': n_clus,
        'Core_Doc_Count': int(np.sum(core_mask)),
        'Noise_Doc_Count': int(np.sum(~core_mask)),
        'Noise_Ratio_Pct': round(float(np.mean(~core_mask) * 100), 2),
        'Silhouette': round(float(sil), 4),
        'Davies_Bouldin': round(float(db), 4),
        'Mean_NPMI': round(mean_npmi, 4),
        'Elapsed_Sec': round(time.time() - t0, 1)
    }
    fold_results.append(fold_res)
    print(f"Fold {fold_i+1}/10 (Seed {seed}) -> Clusters: {n_clus}, Sil: {sil:.4f}, DB: {db:.4f}, NPMI: {mean_npmi:.4f} in {fold_res['Elapsed_Sec']}s")

fold_df = pd.DataFrame(fold_results)
fold_df.to_csv("subsampling_stability_summary_metrics.csv", index=False)
print("Saved subsampling_stability_summary_metrics.csv")

# 3. Pairwise Partition Stability (ARI and AMI on intersecting documents)
print("Computing Pairwise Partition Stability across all 45 fold pairs...")
pairwise_records = []

for i, j in itertools.combinations(range(10), 2):
    idx_i = fold_indices[i]
    idx_j = fold_indices[j]
    
    common_idx, pos_i, pos_j = np.intersect1d(idx_i, idx_j, return_indices=True)
    labels_i = fold_labels[i][pos_i]
    labels_j = fold_labels[j][pos_j]
    
    # 1. Full intersection
    ari_full = adjusted_rand_score(labels_i, labels_j)
    ami_full = adjusted_mutual_info_score(labels_i, labels_j)
    
    # 2. Non-noise intersection (both non-noise)
    non_noise_mask = (labels_i != -1) & (labels_j != -1)
    if np.sum(non_noise_mask) > 10:
        ari_core = adjusted_rand_score(labels_i[non_noise_mask], labels_j[non_noise_mask])
        ami_core = adjusted_mutual_info_score(labels_i[non_noise_mask], labels_j[non_noise_mask])
    else:
        ari_core, ami_core = 0.0, 0.0
        
    pairwise_records.append({
        'Fold_A': i + 1,
        'Fold_B': j + 1,
        'Common_Docs': len(common_idx),
        'Common_Core_Docs': int(np.sum(non_noise_mask)),
        'ARI_Full': round(float(ari_full), 4),
        'AMI_Full': round(float(ami_full), 4),
        'ARI_Core': round(float(ari_core), 4),
        'AMI_Core': round(float(ami_core), 4)
    })

pairwise_df = pd.DataFrame(pairwise_records)
pairwise_df.to_csv("pairwise_fold_stability_matrix.csv", index=False)
print(f"Mean Pairwise Core ARI: {pairwise_df['ARI_Core'].mean():.4f} +/- {pairwise_df['ARI_Core'].std():.4f}")
print(f"Mean Pairwise Core AMI: {pairwise_df['AMI_Core'].mean():.4f} +/- {pairwise_df['AMI_Core'].std():.4f}")

# 4. Sentinel Clinical Topics Replication Tracking
print("Tracking replication of sentinel clinical topics across 10 folds...")
sentinels = {
    'Ptau Plasma Biomarkers': {'ptau', 'plasma', 'tau', 'csf', 'biomarkers', 'pet'},
    'Diabetic Wound Healing': {'wound', 'diabetic', 'healing', 'foot', 'dfu', 'ulcer'},
    'Gut Microbiome Axis': {'gut', 'microbiota', 'microbial', 'microbiome', 'axis'},
    'Alpha-Synuclein Aggregation': {'syn', 'synuclein', 'aggregation', 'fibrils', 'amyloid'},
    'Blood Pressure Control': {'mmhg', 'hypertension', 'pressure', 'blood', 'antihypertensive'},
    'Atrial Strain & Failure': {'atrial', 'strain', 'lvef', 'failure', 'ventricular'}
}

sentinel_replication = []

for topic_name, target_words in sentinels.items():
    found_folds = 0
    jaccard_scores = []
    
    for fold_i in range(10):
        c_kws = fold_topic_dicts[fold_i]
        best_jaccard = 0.0
        match_found = False
        
        for cid, words in c_kws.items():
            overlap = len(target_words.intersection(words))
            if overlap >= 2:
                match_found = True
                jaccard = len(target_words.intersection(words)) / len(target_words.union(words))
                if jaccard > best_jaccard:
                    best_jaccard = jaccard
        
        if match_found:
            found_folds += 1
            jaccard_scores.append(best_jaccard)
            
    rep_rate = (found_folds / 10.0) * 100.0
    mean_jaccard = float(np.mean(jaccard_scores)) if jaccard_scores else 0.0
    
    sentinel_replication.append({
        'Clinical_Topic': topic_name,
        'Keywords_Target': ", ".join(list(target_words)[:4]),
        'Folds_Discovered': found_folds,
        'Replication_Rate_Pct': f"{rep_rate:.1f}%",
        'Mean_Keyword_Jaccard': round(mean_jaccard, 4)
    })
    print(f"Sentinel: {topic_name} -> Replicated in {found_folds}/10 folds ({rep_rate:.0f}%), Jaccard: {mean_jaccard:.3f}")

sentinel_df = pd.DataFrame(sentinel_replication)
sentinel_df.to_csv("sentinel_topic_replication_rates.csv", index=False)
print("Saved sentinel_topic_replication_rates.csv")

# 5. Create 3-Panel Publication Figure
fig, axes = plt.subplots(1, 3, figsize=(18, 5.2))

# Panel 1: Pairwise Partition Stability Distribution (Violin / Box)
ax1 = axes[0]
data_to_plot = [pairwise_df['ARI_Core'], pairwise_df['AMI_Core'], pairwise_df['ARI_Full'], pairwise_df['AMI_Full']]
labels_box = ['ARI (Core)', 'AMI (Core)', 'ARI (Full)', 'AMI (Full)']
bp = ax1.boxplot(data_to_plot, patch_artist=True, labels=labels_box, medianprops={'color': 'black', 'linewidth': 1.5})
colors = ['#15803D', '#0E7C86', '#1F6FEB', '#6E40AA']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax1.set_title('(a) Pairwise Partition Stability (45 Subsample Pairs)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Similarity Metric Score', fontsize=11)
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# Panel 2: Fold-by-Fold Cluster Count & NPMI Stability
ax2 = axes[1]
folds_x = fold_df['Fold']
color_ax2_1 = '#1F6FEB'
ax2.set_xlabel('Subsampling Fold (80% Random Subset)', fontsize=11)
ax2.set_ylabel('Discovered Topics Count', color=color_ax2_1, fontsize=11)
line1 = ax2.plot(folds_x, fold_df['Discovered_Clusters'], marker='o', color=color_ax2_1, linewidth=2, label='Discovered Topics')
ax2.tick_params(axis='y', labelcolor=color_ax2_1)
ax2.set_ylim(80, 160)
ax2.grid(axis='x', linestyle='--', alpha=0.3)

ax2_twin = ax2.twinx()
color_ax2_2 = '#15803D'
ax2_twin.set_ylabel('Mean NPMI Coherence', color=color_ax2_2, fontsize=11)
line2 = ax2_twin.plot(folds_x, fold_df['Mean_NPMI'], marker='s', color=color_ax2_2, linewidth=2, linestyle='--', label='Mean NPMI')
ax2_twin.tick_params(axis='y', labelcolor=color_ax2_2)
ax2_twin.set_ylim(0.08, 0.16)

lines = line1 + line2
labels_l = [l.get_label() for l in lines]
ax2.legend(lines, labels_l, loc='upper right')
ax2.set_title('(b) Consistency of Topic Count and NPMI across Folds', fontsize=12, fontweight='bold')

# Panel 3: Sentinel Topic Replication Rates
ax3 = axes[2]
topics_short = [r['Clinical_Topic'].replace(' ', '\n') for r in sentinel_replication]
rep_rates = [float(r['Replication_Rate_Pct'].replace('%', '')) for r in sentinel_replication]
bars = ax3.bar(topics_short, rep_rates, color='#0E7C86', edgecolor='black', width=0.55, linewidth=0.8)
ax3.set_title('(c) Sentinel Clinical Topic Replication across Folds', fontsize=12, fontweight='bold')
ax3.set_ylabel('Replication Rate across 10 Folds (%)', fontsize=11)
ax3.set_ylim(0, 115)
ax3.grid(axis='y', linestyle='--', alpha=0.5)
for bar in bars:
    yval = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f"{yval:.0f}%", ha='center', va='bottom', fontsize=9.5, fontweight='bold')

plt.tight_layout()
plt.savefig("cluster_subsampling_stability.png", dpi=300)
print("Saved cluster_subsampling_stability.png successfully.")

print("=== Exp 11 Completed Successfully ===")
