import os
import re
import urllib.request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
import hdbscan
import umap

print("=== Starting Exp 8: Cross-Disease Comorbidity & Relational Network Discovery ===")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# 1. Download Dataset
DATA_URL = "https://huggingface.co/datasets/MohsinElis/pubmed-disease-mapping/resolve/main/pubmed_dataset.csv"
DATA_PATH = "pubmed_dataset.csv"
if not os.path.exists(DATA_PATH):
    print("Downloading dataset from Hugging Face...")
    urllib.request.urlretrieve(DATA_URL, DATA_PATH)

df = pd.read_csv(DATA_PATH)
print(f"Loaded dataset: {df.shape}")

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

# 2. Assign Ground-Truth Disease Query Categories
disease_counts = [
    ('Cancer Neoplasm', 1951),
    ('Diabetes Mellitus', 1922),
    ('Stroke Cerebrovascular', 1880),
    ('Alzheimer Disease', 1753),
    ('Hypertension', 1747),
    ('Cardiovascular Disease', 1722),
    ('Neurological Disorders', 1586),
    ('Parkinson Disease', 1504)
]

labels_list = []
for disease_name, count in disease_counts:
    labels_list.extend([disease_name] * count)

df['disease_query'] = labels_list[:len(df)]
print("Disease category distribution:")
print(df['disease_query'].value_counts())

# 3. Extract BioBERT Embeddings
print("Extracting BioBERT embeddings on GPU...")
biobert_name = "dmis-lab/biobert-v1.1"
tokenizer = AutoTokenizer.from_pretrained(biobert_name)
model = AutoModel.from_pretrained(biobert_name).to(device)
model.eval()

batch_size = 64
embeddings = []
texts = df['clean_abstract'].tolist()

with torch.no_grad():
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        encoded = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors='pt'
        ).to(device)
        outputs = model(**encoded)
        last_hidden = outputs.last_hidden_state
        attention_mask = encoded['attention_mask'].unsqueeze(-1)
        mean_pooled = (last_hidden * attention_mask).sum(dim=1) / attention_mask.sum(dim=1)
        embeddings.append(mean_pooled.cpu().numpy())

X_biobert = np.vstack(embeddings)
X_biobert = normalize(X_biobert, norm='l2')

# 4. UMAP Reduction & HDBSCAN Density Clustering
print("Running UMAP and HDBSCAN...")
umap_reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42)
umap_coords = umap_reducer.fit_transform(X_biobert)

hdb = hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, metric='euclidean')
df['cluster'] = hdb.fit_predict(umap_coords)

num_clusters = len(set(df['cluster'])) - (1 if -1 in df['cluster'] else 0)
noise_count = (df['cluster'] == -1).sum()
print(f"Discovered {num_clusters} HDBSCAN clusters ({noise_count} noise documents).")

# Extract cluster keyword signatures
cluster_names = {}
for c in range(num_clusters):
    c_docs = df[df['cluster'] == c]['clean_abstract']
    if len(c_docs) > 0:
        vec = TfidfVectorizer(max_features=100, stop_words='english')
        t = vec.fit_transform(c_docs)
        fn = np.array(vec.get_feature_names_out())
        sc = np.asarray(t.mean(axis=0)).ravel()
        top_words = fn[sc.argsort()[::-1][:5]]
        cluster_names[c] = f"{top_words[0].capitalize()} & {top_words[1].capitalize()} ({', '.join(top_words[:4])})"

# 5. Compute Disease-Disease Comorbidity / Affinity Matrix
# Filter to non-noise documents for pure thematic affinity
clean_df = df[df['cluster'] != -1].reset_index(drop=True)
diseases = sorted(df['disease_query'].unique())
num_diseases = len(diseases)

# Compute probability distribution of each disease over clusters: P(C_k | D_i)
cluster_ids = sorted(clean_df['cluster'].unique())
disease_cluster_probs = np.zeros((num_diseases, len(cluster_ids)))

for i, d in enumerate(diseases):
    d_docs = clean_df[clean_df['disease_query'] == d]
    total_d = len(d_docs)
    for j, c in enumerate(cluster_ids):
        count_c = (d_docs['cluster'] == c).sum()
        disease_cluster_probs[i, j] = count_c / total_d if total_d > 0 else 0

# Cosine affinity between disease cluster distribution vectors
affinity_matrix = cosine_similarity(disease_cluster_probs)
df_affinity = pd.DataFrame(affinity_matrix, index=diseases, columns=diseases)
print("\n=== Cross-Disease Comorbidity Affinity Matrix ===")
print(df_affinity.round(3))

# Save matrix to CSV
df_affinity.round(4).to_csv("disease_comorbidity_matrix.csv")

# 6. Discover Multidisciplinary Bridge Clusters
# Identify clusters with highest joint product P(C_k | D_i) * P(C_k | D_j) for all pairs
bridge_records = []
for i in range(num_diseases):
    for j in range(i + 1, num_diseases):
        d1 = diseases[i]
        d2 = diseases[j]
        joint_scores = disease_cluster_probs[i, :] * disease_cluster_probs[j, :]
        best_cluster_idx = np.argmax(joint_scores)
        best_cluster = cluster_ids[best_cluster_idx]
        joint_val = joint_scores[best_cluster_idx]
        
        # Clinical topic label
        topic_sig = cluster_names.get(best_cluster, f"Cluster {best_cluster}")
        
        d1_share = disease_cluster_probs[i, best_cluster_idx]
        d2_share = disease_cluster_probs[j, best_cluster_idx]
        
        bridge_records.append({
            'Disease_1': d1,
            'Disease_2': d2,
            'Comorbidity_Affinity': round(affinity_matrix[i, j], 4),
            'Top_Bridge_Cluster_ID': best_cluster,
            'Bridge_Joint_Product': round(joint_val, 6),
            'Disease1_Cluster_Share': round(d1_share, 4),
            'Disease2_Cluster_Share': round(d2_share, 4),
            'Inferred_Bridge_Topic': topic_sig
        })

df_bridges = pd.DataFrame(bridge_records).sort_values(by='Comorbidity_Affinity', ascending=False)
df_bridges.to_csv("multidisciplinary_bridge_clusters.csv", index=False)
print("\n=== Top 5 Cross-Disease Bridge Clusters ===")
print(df_bridges[['Disease_1', 'Disease_2', 'Comorbidity_Affinity', 'Inferred_Bridge_Topic']].head(5).to_string(index=False))

# 7. Visualization 1: Clustered Comorbidity Heatmap
plt.figure(figsize=(10, 8), dpi=300)
mask = np.triu(np.ones_like(affinity_matrix, dtype=bool), k=1)
sns.heatmap(
    df_affinity,
    annot=True,
    fmt=".3f",
    cmap="YlGnBu",
    cbar_kws={'label': 'Topological Comorbidity Affinity (Cosine)'},
    linewidths=0.8,
    linecolor='white',
    square=True
)
plt.title("Cross-Disease Comorbidity Affinity Matrix\n(Inferred via Unsupervised HDBSCAN Topological Clustering)", fontsize=13, fontweight='bold', pad=15)
plt.xticks(rotation=35, ha='right', fontsize=10)
plt.yticks(rotation=0, fontsize=10)
plt.tight_layout()
plt.savefig("disease_comorbidity_chord_heatmap.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved disease_comorbidity_chord_heatmap.png")

# 8. Visualization 2: Disease Knowledge Network Graph
fig, ax = plt.subplots(figsize=(13, 11), dpi=300)
G = nx.Graph()

# Add disease nodes
for d in diseases:
    doc_cnt = (df['disease_query'] == d).sum()
    G.add_node(d, size=doc_cnt)

# Add edges above threshold
threshold = 0.12
for i in range(num_diseases):
    for j in range(i + 1, num_diseases):
        aff = affinity_matrix[i, j]
        if aff >= threshold:
            G.add_edge(diseases[i], diseases[j], weight=aff)

# Circular layout for clean medical presentation
pos = nx.circular_layout(G)

# Draw edges with varying thickness and color
edges = G.edges()
weights = [G[u][v]['weight'] for u, v in edges]
edge_colors = [plt.cm.Blues(0.3 + 0.7 * (w - min(weights)) / (max(weights) - min(weights) + 1e-6)) for w in weights]
edge_widths = [1.5 + 8.0 * (w - min(weights)) / (max(weights) - min(weights) + 1e-6) for w in weights]

nx.draw_networkx_edges(G, pos, edgelist=edges, width=edge_widths, edge_color=edge_colors, alpha=0.85, ax=ax)

# Draw disease nodes
node_colors = ['#EF4444', '#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#06B6D4', '#EC4899', '#84CC16']
nx.draw_networkx_nodes(G, pos, node_size=3200, node_color=node_colors, edgecolors='black', linewidths=1.5, ax=ax)

# Draw node labels
labels = {d: d.replace(' ', '\n') for d in diseases}
nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold', font_color='white', ax=ax)

# Annotate key bridge micro-clusters on top affinity edges
top_3_bridges = df_bridges.head(3)
for _, r in top_3_bridges.iterrows():
    u, v = r['Disease_1'], r['Disease_2']
    if G.has_edge(u, v):
        mid_x = (pos[u][0] + pos[v][0]) / 2.0
        mid_y = (pos[u][1] + pos[v][1]) / 2.0
        topic_short = r['Inferred_Bridge_Topic'].split('(')[0].strip()
        ax.annotate(
            f"Bridge: {topic_short}\n(Affinity: {r['Comorbidity_Affinity']:.2f})",
            xy=(mid_x, mid_y),
            xytext=(mid_x * 0.7, mid_y * 0.7),
            fontsize=8.5,
            fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", fc="#FEF3C7", ec="#D97706", lw=1.2, alpha=0.95),
            ha='center'
        )

ax.set_title("Unsupervised Biomedical Disease Knowledge Network\nCross-Disease Comorbidity & Multidisciplinary Thematic Bridges", fontsize=15, fontweight='bold', pad=20)
ax.axis('off')
plt.tight_layout()
plt.savefig("disease_knowledge_network.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved disease_knowledge_network.png")

print("=== Exp 8 Completed Successfully! ===")
