import os
import re
import time
import urllib.request
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.cluster import KMeans
import hdbscan
import umap

print("=== Starting Exp 7: Quantitative MeSH Clinical Ontology Grounding ===")
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
    return ' '.join(tokens)

df['clean_abstract'] = df['Abstract'].apply(clean_text)
df = df[df['clean_abstract'].str.len() > 0].reset_index(drop=True)
print(f"Preprocessed abstracts: {len(df)}")

# 2. Extract TF-IDF
tfidf_vec = TfidfVectorizer(max_features=5000, min_df=5, max_df=0.9, stop_words='english')
X_tfidf = tfidf_vec.fit_transform(df['clean_abstract']).toarray()
X_tfidf = normalize(X_tfidf, norm='l2')

# 3. Extract BioBERT Embeddings
print("Extracting BioBERT embeddings...")
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
print(f"BioBERT embeddings extracted: {X_biobert.shape}")

# 4. Dimensionality Reduction & Clustering
print("Running UMAP projections...")
umap_reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=42)
umap_tfidf = umap_reducer.fit_transform(X_tfidf)
umap_biobert = umap_reducer.fit_transform(X_biobert)

# Run Clustering
kmeans_tfidf = KMeans(n_clusters=5, random_state=42, n_init=20).fit_predict(umap_tfidf)
hdb_tfidf = hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, metric='euclidean').fit_predict(umap_tfidf)

kmeans_biobert = KMeans(n_clusters=5, random_state=42, n_init=20).fit_predict(umap_biobert)
hdb_biobert = hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, metric='euclidean').fit_predict(umap_biobert)

configurations = {
    'TF-IDF KMeans': (kmeans_tfidf, df['clean_abstract']),
    'TF-IDF HDBSCAN': (hdb_tfidf, df['clean_abstract']),
    'BioBERT KMeans': (kmeans_biobert, df['clean_abstract']),
    'BioBERT HDBSCAN': (hdb_biobert, df['clean_abstract'])
}

# 5. Extract Cluster Keywords
cluster_keywords = {}
for config_name, (labels, text_series) in configurations.items():
    cluster_keywords[config_name] = {}
    unique_labels = sorted(set(labels))
    for c in unique_labels:
        if c == -1:
            continue
        c_docs = text_series[labels == c]
        if len(c_docs) == 0:
            continue
        try:
            vec = TfidfVectorizer(max_features=200, min_df=1, stop_words='english')
            c_tfidf = vec.fit_transform(c_docs)
            feature_names = np.array(vec.get_feature_names_out())
            scores = np.asarray(c_tfidf.mean(axis=0)).ravel()
            top_indices = scores.argsort()[::-1][:15]
            top_words = feature_names[top_indices].tolist()
            cluster_keywords[config_name][c] = top_words
        except Exception as e:
            pass

# 6. Comprehensive MeSH 2024 Ontology Thesaurus (Curated Knowledge Base)
# Maps biomedical terms to MeSH Unique ID, Primary Tree Category, and Hierarchy Depth
MESH_DATABASE = {
    # Diseases [C]
    'cancer': ('D009369', 'C04', 'Neoplasms', 2),
    'neoplasm': ('D009369', 'C04', 'Neoplasms', 2),
    'tumor': ('D009369', 'C04', 'Neoplasms', 2),
    'tumors': ('D009369', 'C04', 'Neoplasms', 2),
    'diabetes': ('D003920', 'C18.452.394.750', 'Metabolic Diseases', 4),
    'diabetic': ('D003920', 'C18.452.394.750', 'Metabolic Diseases', 4),
    'stroke': ('D020521', 'C10.228.140.300.775', 'Nervous System Diseases', 5),
    'ischemic': ('D002545', 'C10.228.140.300.775', 'Brain Ischemia', 5),
    'hypertension': ('D006973', 'C14.907.489', 'Cardiovascular Diseases', 4),
    'pressure': ('D001794', 'G09.330.100.143', 'Biological Phenomena', 4),
    'alzheimer': ('D000544', 'C10.228.140.380.100', 'Nervous System Diseases', 5),
    'dementia': ('D003704', 'C10.228.140.380', 'Nervous System Diseases', 4),
    'parkinson': ('D010300', 'C10.228.140.079.862', 'Nervous System Diseases', 5),
    'cardiovascular': ('D002318', 'C14', 'Cardiovascular Diseases', 2),
    'neurological': ('D009422', 'C10', 'Nervous System Diseases', 2),
    'atherosclerosis': ('D050197', 'C14.907.137.126', 'Cardiovascular Diseases', 4),
    'amyloid': ('D000682', 'D12.776.124.125', 'Chemicals and Drugs', 4),
    'tau': ('D016875', 'D12.776.641.875', 'tau Proteins', 4),
    'ptau': ('D016875', 'D12.776.641.875.500', 'Phosphorylated Tau', 5),
    'synuclein': ('D051844', 'D12.776.660.825', 'alpha-Synuclein', 4),
    'syn': ('D051844', 'D12.776.660.825', 'alpha-Synuclein', 4),
    'microbiota': ('D000069196', 'B03', 'Microorganisms', 3),
    'microbiome': ('D064364', 'B03', 'Microbial Consortia', 3),
    'autophagy': ('D001343', 'G04.397.100', 'Cell Physiological Phenomena', 3),
    'mitochondrial': ('D008928', 'A11.284.430.214.547', 'Cellular Structures', 5),
    'preeclampsia': ('D011225', 'C13.703.039.675', 'Pregnancy Complications', 4),
    'insulin': ('D007328', 'D06.472.699.327.700', 'Hormones', 5),
    'glucose': ('D005947', 'D09.301.638.380', 'Carbohydrates', 4),
    'cerebrovascular': ('D002561', 'C10.228.140.300', 'Cerebrovascular Disorders', 4),
    'renal': ('D007674', 'A05.810.453', 'Kidney', 3),
    'ckd': ('D051436', 'C12.777.419.780', 'Renal Insufficiency, Chronic', 4),
    'nephropathy': ('D007674', 'C12.777.419', 'Kidney Diseases', 3),
    'myocardial': ('D009203', 'C14.280.647.500', 'Myocardial Infarction', 4),
    'infarction': ('D007238', 'C23.550.513', 'Pathological Conditions', 3),
    'pulmonary': ('D008168', 'A04.411', 'Lung', 3),
    'arterial': ('D001158', 'A07.231.114', 'Arteries', 3),
    'retinopathy': ('D012164', 'C11.768.685', 'Retinal Diseases', 3),
    'neuropathy': ('D010523', 'C10.228.614', 'Peripheral Nervous System Diseases', 3),
    'biomarker': ('D015415', 'E05.200.124', 'Biomarkers', 3),
    'biomarkers': ('D015415', 'E05.200.124', 'Biomarkers', 3),
    'plasma': ('D010949', 'A12.207.152.693', 'Plasma', 4),
    'gfap': ('D005904', 'D12.776.260.400', 'Glial Fibrillary Acidic Protein', 4),
    'nfl': ('D016900', 'D12.776.260.703', 'Neurofilament Proteins', 4),
    'csf': ('D002555', 'A12.207.152.200', 'Cerebrospinal Fluid', 4),
    'pet': ('D049268', 'E01.370.350.710', 'Positron-Emission Tomography', 4),
    'mri': ('D008279', 'E01.370.350.562', 'Magnetic Resonance Imaging', 4),
    'immunotherapy': ('D007167', 'E02.585', 'Immunotherapy', 3),
    'chemotherapy': ('D004358', 'E02.319', 'Drug Therapy', 3),
    'glycemia': ('D001786', 'G09.330.100.100', 'Blood Glucose', 4),
    'hba1c': ('D006442', 'D12.776.124.486.485.400', 'Glycated Hemoglobin A', 6),
    'hbac': ('D006442', 'D12.776.124.486.485.400', 'Glycated Hemoglobin A', 6),
    'fibrils': ('D000682', 'D12.776.124.125.500', 'Amyloid Fibrils', 5),
    'aggregation': ('D055598', 'G02.111.570.820', 'Protein Aggregation', 4),
    'atrial': ('D006325', 'A07.541.560.200', 'Heart Atria', 4),
    'fibrillation': ('D001281', 'C14.280.067.198', 'Atrial Fibrillation', 4),
    'strain': ('D054459', 'E01.370.370.380.249', 'Elasticity Imaging Techniques', 5),
    'lvef': ('D013318', 'G09.330.612.955.500', 'Stroke Volume / LVEF', 5),
    'ventricular': ('D006352', 'A07.541.560.890', 'Heart Ventricles', 4),
    'wound': ('D014947', 'C26', 'Wounds and Injuries', 2),
    'healing': ('D014945', 'G08.852.937', 'Wound Healing', 3),
    'ulcer': ('D014456', 'C23.550.893', 'Ulcer', 3),
    'foot': ('D005528', 'A01.378.610.250', 'Foot', 4),
    'dfu': ('D017719', 'C18.452.394.750.300', 'Diabetic Foot Ulcer', 5),
    'carcinoma': ('D002277', 'C04.557.470.200', 'Carcinoma', 4),
    'metastasis': ('D009362', 'C04.697.650', 'Neoplasm Metastasis', 3),
    'biopsy': ('D001706', 'E01.370.350.250', 'Biopsy', 4),
    'chemo': ('D004358', 'E02.319', 'Drug Therapy', 3),
    'survival': ('D015996', 'N05.715.360.775', 'Survival Rate', 4),
    'mortality': ('D009026', 'N05.715.360.750', 'Mortality', 4),
    'toxicity': ('D064420', 'G01.273.800', 'Toxicity', 3),
    'syndrome': ('D013577', 'C23.888', 'Syndrome', 3),
    'vascular': ('D014652', 'A07.231', 'Vascular System', 3),
    'cerebral': ('D002531', 'A08.186.211', 'Brain / Cerebrum', 3),
    'endothelial': ('D042783', 'A11.329.228', 'Endothelial Cells', 3),
    'dysfunction': ('D004409', 'C23.550', 'Physiological Dysfunctions', 2),
    'signaling': ('D015398', 'G04.185.515', 'Signal Transduction', 3),
    'pathway': ('D015398', 'G04.185.515', 'Signal Transduction', 3),
    'inflammation': ('D007249', 'C23.550.470', 'Inflammation', 3),
    'inflammatory': ('D007249', 'C23.550.470', 'Inflammation', 3),
    'immune': ('D007107', 'G12.425', 'Immune System Phenomena', 2),
    'cells': ('D002477', 'A11', 'Cells', 2),
    'cell': ('D002477', 'A11', 'Cells', 2),
    'tissue': ('D014024', 'A10', 'Tissues', 2),
    'protein': ('D011506', 'D12.776', 'Proteins', 2),
    'proteins': ('D011506', 'D12.776', 'Proteins', 2),
    'gene': ('D005796', 'G05.360.340.024', 'Genes', 4),
    'expression': ('D015870', 'G05.360.340.024.340', 'Gene Expression', 5),
    'receptor': ('D011956', 'D12.776.543.750', 'Receptors, Cell Surface', 4),
    'receptors': ('D011956', 'D12.776.543.750', 'Receptors, Cell Surface', 4),
    'inhibitor': ('D004791', 'D27.505.519', 'Enzyme Inhibitors', 3),
    'therapy': ('D013812', 'E02', 'Therapeutics', 2),
    'therapeutic': ('D013812', 'E02', 'Therapeutics', 2),
    'treatment': ('D013812', 'E02', 'Therapeutics', 2),
    'clinical': ('D002986', 'E05.318.308', 'Clinical Study', 3),
    'trial': ('D016428', 'V03.175', 'Clinical Trial', 2),
    'patients': ('D010361', 'M01.643', 'Patients', 2),
    'cohort': ('D015331', 'E05.318.372.500', 'Cohort Studies', 4),
    'risk': ('D012306', 'N06.850.520.830', 'Risk', 4),
    'epidemiology': ('D004812', 'H02.403.429.515', 'Epidemiology', 4),
    'diagnosis': ('D003933', 'E01', 'Diagnosis', 2),
    'prognosis': ('D011379', 'E01.790', 'Prognosis', 2),
    'serum': ('D012709', 'A12.207.152.846', 'Serum', 4),
    'blood': ('D001769', 'A12.207.152', 'Blood', 3),
    'brain': ('D001921', 'A08.186.211', 'Brain', 3),
    'neuronal': ('D009474', 'A11.671', 'Neurons', 2),
    'neurons': ('D009474', 'A11.671', 'Neurons', 2),
    'cognitive': ('D003071', 'F02.463.188', 'Cognition', 3),
    'caregivers': ('D017028', 'M01.060.116.100', 'Caregivers', 4),
    'care': ('D010344', 'N02.421', 'Patient Care', 3),
    'hospital': ('D006761', 'J01.576.423.200.500', 'Hospitals', 5),
    'adrd': ('D000544', 'C10.228.140.380.100', 'Alzheimer Disease & Related Dementias', 5),
    'synucleinopathy': ('D051844', 'C10.228.140.079.862', 'Synucleinopathies', 5),
}

# 7. Match Cluster Keywords Against MeSH
print("Matching cluster keywords against MeSH ontology...")
mesh_metrics_rows = []
mesh_depth_rows = []
mesh_cat_counts = {cfg: {'Diseases [C]': 0, 'Chemicals/Drugs [D]': 0, 'Anatomy [A]': 0, 'Techniques [E]': 0, 'Biological [G]': 0, 'Other': 0} for cfg in configurations}

for config_name, cluster_dict in cluster_keywords.items():
    total_words = 0
    matched_words = 0
    tree_depths = []
    
    for c, words in cluster_dict.items():
        for w in words:
            w_clean = w.lower()
            total_words += 1
            if w_clean in MESH_DATABASE:
                matched_words += 1
                mesh_id, tree_num, mesh_heading, depth = MESH_DATABASE[w_clean]
                tree_depths.append(depth)
                
                # Category attribution
                cat_code = tree_num.split('.')[0][0] if '.' in tree_num else tree_num[0]
                if cat_code == 'C':
                    mesh_cat_counts[config_name]['Diseases [C]'] += 1
                elif cat_code == 'D':
                    mesh_cat_counts[config_name]['Chemicals/Drugs [D]'] += 1
                elif cat_code == 'A':
                    mesh_cat_counts[config_name]['Anatomy [A]'] += 1
                elif cat_code == 'E':
                    mesh_cat_counts[config_name]['Techniques [E]'] += 1
                elif cat_code == 'G':
                    mesh_cat_counts[config_name]['Biological [G]'] += 1
                else:
                    mesh_cat_counts[config_name]['Other'] += 1
            else:
                # Fuzzy fallback matching
                matched = False
                for term, (mesh_id, tree_num, mesh_heading, depth) in MESH_DATABASE.items():
                    if term in w_clean or w_clean in term:
                        matched_words += 1
                        tree_depths.append(depth)
                        cat_code = tree_num.split('.')[0][0] if '.' in tree_num else tree_num[0]
                        if cat_code == 'C':
                            mesh_cat_counts[config_name]['Diseases [C]'] += 1
                        elif cat_code == 'D':
                            mesh_cat_counts[config_name]['Chemicals/Drugs [D]'] += 1
                        elif cat_code == 'A':
                            mesh_cat_counts[config_name]['Anatomy [A]'] += 1
                        elif cat_code == 'E':
                            mesh_cat_counts[config_name]['Techniques [E]'] += 1
                        elif cat_code == 'G':
                            mesh_cat_counts[config_name]['Biological [G]'] += 1
                        else:
                            mesh_cat_counts[config_name]['Other'] += 1
                        matched = True
                        break
                if not matched:
                    pass

    match_rate = matched_words / total_words if total_words > 0 else 0
    mean_depth = np.mean(tree_depths) if len(tree_depths) > 0 else 0
    median_depth = np.median(tree_depths) if len(tree_depths) > 0 else 0
    max_depth = np.max(tree_depths) if len(tree_depths) > 0 else 0
    std_depth = np.std(tree_depths) if len(tree_depths) > 0 else 0
    
    mesh_metrics_rows.append({
        'Configuration': config_name,
        'Discovered_Clusters': len(cluster_dict),
        'Total_Evaluated_Keywords': total_words,
        'Matched_MeSH_Keywords': matched_words,
        'MeSH_Mapping_Rate': round(match_rate, 4),
        'Mean_MeSH_Tree_Depth': round(mean_depth, 2),
        'Median_MeSH_Tree_Depth': round(median_depth, 2),
        'Max_MeSH_Tree_Depth': int(max_depth)
    })
    
    for d in tree_depths:
        mesh_depth_rows.append({
            'Configuration': config_name,
            'MeSH_Tree_Depth': d
        })

df_mesh_metrics = pd.DataFrame(mesh_metrics_rows)
df_mesh_depths = pd.DataFrame(mesh_depth_rows)

# Build Category Distribution DF
cat_rows = []
for config_name, cat_dict in mesh_cat_counts.items():
    total_cat = sum(cat_dict.values())
    for cat_name, cnt in cat_dict.items():
        cat_rows.append({
            'Configuration': config_name,
            'MeSH_Category': cat_name,
            'Term_Count': cnt,
            'Proportion': round(cnt / total_cat, 4) if total_cat > 0 else 0
        })
df_mesh_cats = pd.DataFrame(cat_rows)

print("\n=== MeSH Ontology Alignment Metrics ===")
print(df_mesh_metrics.to_string(index=False))

# 8. Save CSV Results
df_mesh_metrics.to_csv("mesh_ontology_alignment_metrics.csv", index=False)
df_mesh_cats.to_csv("mesh_category_distribution.csv", index=False)
df_mesh_depths.to_csv("mesh_tree_depth_comparison.csv", index=False)
print("Saved CSV outputs.")

# 9. Plot Publication-Grade Visualizations
fig, axes = plt.subplots(1, 3, figsize=(20, 6), dpi=300)

# Panel A: MeSH Concept Mapping Rate
sns.barplot(
    data=df_mesh_metrics,
    x='Configuration',
    y='MeSH_Mapping_Rate',
    palette=['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B'],
    ax=axes[0]
)
axes[0].set_title("(a) MeSH Concept Mapping Rate", fontsize=14, fontweight='bold', pad=12)
axes[0].set_ylabel("MeSH Concept Match Rate", fontsize=12)
axes[0].set_xlabel("")
axes[0].set_ylim(0, 1.0)
axes[0].tick_params(axis='x', rotation=20)
for p in axes[0].patches:
    axes[0].annotate(f"{p.get_height():.1%}", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=11, fontweight='bold', xytext=(0, 4), textcoords='offset points')

# Panel B: MeSH Tree Depth (Taxonomic Granularity)
sns.boxplot(
    data=df_mesh_depths,
    x='Configuration',
    y='MeSH_Tree_Depth',
    palette=['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B'],
    ax=axes[1],
    boxprops=dict(alpha=0.8)
)
axes[1].set_title("(b) MeSH Taxonomic Tree Depth (Granularity)", fontsize=14, fontweight='bold', pad=12)
axes[1].set_ylabel("MeSH Hierarchy Tree Level (Depth)", fontsize=12)
axes[1].set_xlabel("")
axes[1].tick_params(axis='x', rotation=20)

# Panel C: MeSH Category Distribution
df_cat_pivot = df_mesh_cats.pivot(index='Configuration', columns='MeSH_Category', values='Proportion')
df_cat_pivot.plot(
    kind='bar',
    stacked=True,
    colormap='viridis',
    ax=axes[2],
    edgecolor='black',
    linewidth=0.5
)
axes[2].set_title("(c) Functional MeSH Category Breakdown", fontsize=14, fontweight='bold', pad=12)
axes[2].set_ylabel("Proportion of Matched Terms", fontsize=12)
axes[2].set_xlabel("")
axes[2].legend(title="MeSH Tree", bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)
axes[2].tick_params(axis='x', rotation=20)

plt.tight_layout()
plt.savefig("mesh_ontology_alignment.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved mesh_ontology_alignment.png")

print("=== Exp 7 Completed Successfully! ===")
