import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

print("=== Generating Canonical Cross-Disease Knowledge Network Suite ===")

# 1. Load dataset & assign disease labels
data_path = 'data/pubmed_dataset.csv' if os.path.exists('data/pubmed_dataset.csv') else 'pubmed_dataset.csv'
df = pd.read_csv(data_path)
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

# Load canonical BioBERT and TF-IDF cluster assignments
df_bio = pd.read_csv('BioBERT_Results/step6_cluster_assignments.csv')
df = df.merge(df_bio[['PMID', 'HDBSCAN_Cluster']], on='PMID', how='inner')

# Clean text for keyword extraction
stopwords = {'i', 'me', 'my', 'we', 'our', 'you', 'he', 'him', 'she', 'her', 'it', 'they', 'them',
             'what', 'which', 'who', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were',
             'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'a', 'an', 'the', 'and', 'but',
             'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
             'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
             'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
             'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
             'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
             'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'}

def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    tokens = [t for t in text.split() if t not in stopwords and len(t) > 2]
    return ' '.join(tokens)

df['clean_abstract'] = df['Abstract'].apply(clean_text)

# Filter non-noise
clean = df[df['HDBSCAN_Cluster'] != -1].reset_index(drop=True)
diseases = sorted(df['disease_query'].unique())
clusters = sorted(clean['HDBSCAN_Cluster'].unique())

# Compute probability distribution P(C_k | D_i)
prob_matrix = np.zeros((len(diseases), len(clusters)))
for i, d in enumerate(diseases):
    d_docs = clean[clean['disease_query'] == d]
    tot = len(d_docs)
    for j, c in enumerate(clusters):
        cnt = (d_docs['HDBSCAN_Cluster'] == c).sum()
        prob_matrix[i, j] = cnt / tot if tot > 0 else 0

# Cosine affinity matrix
affinity_matrix = cosine_similarity(prob_matrix)
df_affinity = pd.DataFrame(affinity_matrix, index=diseases, columns=diseases)

out_dir = 'Q1_Experiments_Results/exp8_disease_network'
os.makedirs(out_dir, exist_ok=True)
df_affinity.round(4).to_csv(os.path.join(out_dir, 'disease_comorbidity_matrix.csv'))

# Cluster keywords dictionary
cluster_topics = {}
for c in clusters:
    c_docs = clean[clean['HDBSCAN_Cluster'] == c]['clean_abstract']
    if len(c_docs) > 0:
        vec = TfidfVectorizer(max_features=50, stop_words='english')
        t = vec.fit_transform(c_docs)
        fn = np.array(vec.get_feature_names_out())
        sc = np.asarray(t.mean(axis=0)).ravel()
        top_w = fn[sc.argsort()[::-1][:5]]
        cluster_topics[c] = (f"{top_w[0].capitalize()} & {top_w[1].capitalize()}", ', '.join(top_w[:4]))

# Find top bridge clusters
bridge_rows = []
for i in range(len(diseases)):
    for j in range(i + 1, len(diseases)):
        d1 = diseases[i]
        d2 = diseases[j]
        aff = affinity_matrix[i, j]
        
        # Joint product of shares
        joint = prob_matrix[i, :] * prob_matrix[j, :]
        best_idx = np.argmax(joint)
        best_c = clusters[best_idx]
        title, kws = cluster_topics.get(best_c, (f"Cluster {best_c}", ""))
        
        bridge_rows.append({
            'Disease_1': d1,
            'Disease_2': d2,
            'Comorbidity_Affinity': round(aff, 4),
            'Top_Bridge_Cluster_ID': best_c,
            'Bridge_Joint_Product': round(joint[best_idx], 6),
            'Disease1_Share': round(prob_matrix[i, best_idx], 4),
            'Disease2_Share': round(prob_matrix[j, best_idx], 4),
            'Inferred_Bridge_Topic': title,
            'Top_Bridge_Keywords': kws
        })

df_bridges = pd.DataFrame(bridge_rows).sort_values(by='Comorbidity_Affinity', ascending=False)
df_bridges.to_csv(os.path.join(out_dir, 'multidisciplinary_bridge_clusters.csv'), index=False)
print("Saved CSV files.")

# Visualization 1: Clustered Comorbidity Heatmap
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
plt.savefig(os.path.join(out_dir, "disease_comorbidity_chord_heatmap.png"), dpi=300, bbox_inches='tight')
plt.close()
print("Saved disease_comorbidity_chord_heatmap.png")

# Visualization 2: Network Graph
fig, ax = plt.subplots(figsize=(14, 12), dpi=300)
G = nx.Graph()

for d in diseases:
    doc_cnt = (df['disease_query'] == d).sum()
    G.add_node(d, size=doc_cnt)

# Add edges with affinity > 0.45
threshold = 0.45
for i in range(len(diseases)):
    for j in range(i + 1, len(diseases)):
        aff = affinity_matrix[i, j]
        if aff >= threshold:
            G.add_edge(diseases[i], diseases[j], weight=aff)

pos = nx.circular_layout(G)

edges = G.edges()
weights = [G[u][v]['weight'] for u, v in edges]
min_w, max_w = min(weights), max(weights)
edge_colors = [plt.cm.Blues(0.35 + 0.65 * (w - min_w) / (max_w - min_w + 1e-6)) for w in weights]
edge_widths = [1.8 + 8.5 * (w - min_w) / (max_w - min_w + 1e-6) for w in weights]

nx.draw_networkx_edges(G, pos, edgelist=edges, width=edge_widths, edge_color=edge_colors, alpha=0.85, ax=ax)

# Draw disease nodes
node_colors = ['#EF4444', '#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#06B6D4', '#EC4899', '#84CC16']
nx.draw_networkx_nodes(G, pos, node_size=3400, node_color=node_colors, edgecolors='black', linewidths=1.8, ax=ax)

labels = {d: d.replace(' ', '\n') for d in diseases}
nx.draw_networkx_labels(G, pos, labels=labels, font_size=9.5, font_weight='bold', font_color='white', ax=ax)

# Annotate key bridge micro-clusters
top_annotations = [
    ('Cardiovascular Disease', 'Stroke Cerebrovascular'),
    ('Alzheimer Disease', 'Parkinson Disease'),
    ('Alzheimer Disease', 'Hypertension'),
    ('Diabetes Mellitus', 'Hypertension')
]

for u, v in top_annotations:
    if G.has_edge(u, v):
        row = df_bridges[(df_bridges['Disease_1'] == min(u, v)) & (df_bridges['Disease_2'] == max(u, v))]
        if len(row) > 0:
            r = row.iloc[0]
            mid_x = (pos[u][0] + pos[v][0]) / 2.0
            mid_y = (pos[u][1] + pos[v][1]) / 2.0
            ax.annotate(
                f"Bridge: {r['Inferred_Bridge_Topic']}\nAffinity: {r['Comorbidity_Affinity']:.2f}\n[{r['Top_Bridge_Keywords']}]",
                xy=(mid_x, mid_y),
                xytext=(mid_x * 0.65, mid_y * 0.65),
                fontsize=8.0,
                fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.35", fc="#FEF3C7", ec="#D97706", lw=1.2, alpha=0.95),
                ha='center',
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.1", color="#B45309", lw=1.0)
            )

ax.set_title("Unsupervised Biomedical Disease Knowledge Network\nCross-Disease Comorbidity & Multidisciplinary Thematic Bridges (BioBERT-HDBSCAN)", fontsize=14, fontweight='bold', pad=25)
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "disease_knowledge_network.png"), dpi=300, bbox_inches='tight')
plt.close()
print("Saved disease_knowledge_network.png successfully!")

print("=== Exp 8 Suite Finished! ===")
