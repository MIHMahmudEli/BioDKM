# BioDKM: An Unsupervised Topological Framework for Biomedical Disease Knowledge Mapping and Comorbidity Discovery from PubMed Literature

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Hugging Face Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-orange)](https://huggingface.co/datasets/MohsinElis/pubmed-disease-mapping)
[![Manuscript](https://img.shields.io/badge/Manuscript-Under%20Review-informational)](https://github.com/MIHMahmudEli/BioDKM)

Official open-source implementation, cloud GPU replication suite, and empirical benchmarks for the research paper:

> **BioDKM: An Unsupervised Topological Framework for Biomedical Disease Knowledge Mapping and Comorbidity Discovery from PubMed Literature**  
> *(Under Review)*

---

## 📑 Table of Contents

- [Overview & Architecture](#-overview--architecture)
- [Key Empirical Findings](#-key-empirical-findings)
- [Repository Structure](#-repository-structure)
- [Quick Start](#-quick-start)
- [Cloud GPU Replication Suite](#-cloud-gpu-replication-suite)
- [Core Benchmark Results](#-core-benchmark-results)
- [Comorbidity Knowledge Discovery](#-comorbidity-knowledge-discovery)
- [Data & Pretrained Models](#-data--pretrained-models)
- [Citation](#-citation)
- [License](#-license)

---

## 📌 Overview & Architecture

Biomedical literature is expanding exponentially, creating acute challenges for clinical researchers attempting to synthesize multi-disease interactions, identify emerging pathophysiological pathways, and discover latent comorbidity relationships.

**BioDKM** introduces an unsupervised, dual-stream topological framework that extracts, projects, clusters, and harmonizes biomedical disease knowledge from unstructured PubMed abstracts without manual annotation.

<p align="center">
  <img src="results/manuscript/Complete_pipeline_architecture.png" alt="BioDKM Architecture Diagram" width="95%"/>
</p>

### Coordinated Pipeline Stages

1. **Corpus Acquisition & Harmonization**: Standardized extraction and cleaning of 14,064 biomedical abstracts across 8 canonical disease classes.
2. **Dual-Stream Representation**:
   - **Stream A (Lexical)**: High-dimensional sparse TF-IDF ($V = 5,000$ features) capturing explicit clinical terminology.
   - **Stream B (Contextual)**: Dense biomedical transformer embeddings (`dmis-lab/biobert-v1.1`, $d = 768$) capturing latent semantic interactions.
3. **Topological Manifold Learning**: Non-linear UMAP projection ($n\_neighbors=15, min\_dist=0.1, metric=\text{cosine}$) that preserves both local and global manifold geometries while mitigating high-dimensional distance concentration.
4. **Density-Based Thematic Clustering**: HDBSCAN density clustering ($min\_cluster\_size=30, min\_samples=5$) surfacing hierarchical thematic structures and filtering ambient boundary noise.
5. **Harmonization & Clinical Translation**: Quantitative evaluation via UCI NPMI coherence, external disease alignment, MeSH ontology tree depth verification, and comorbidity graph topology.

---

## 🔬 Key Empirical Findings

1. **Density-Based Dominance**: Density-based topological clustering (HDBSCAN) consistently outperforms parametric clustering (K-Means) across all intrinsic validity metrics (Silhouette: **0.4786** vs. 0.3708, DB Index: **0.6034** vs. 0.8426), discovering **116** fine-grained clinical topics.
2. **Lexical Efficiency vs. Contextual Parity**: High-dimensional TF-IDF achieves UCI NPMI semantic coherence statistically indistinguishable from 768-dimensional BioBERT embeddings (**0.1158** vs. **0.1154**, $p = 0.416$), executing $3.5\times$ faster than classical LDA and $5.7\times$ faster than BERTopic.
3. **Topological Manifold Necessity**: Manifold projection ablation mathematically confirms that non-linear UMAP is indispensable ($T = 0.880$ trustworthiness); ambient high-dimensional density clustering suffers severe distance concentration and collapses into an unclustered noise pool.
4. **Comprehensive Reviewer Defense**: Supported by 13 rigorous benchmark investigations, including MeSH ontology tree depth grounding, 10-fold subsampling stability, matched-core noise ablation, empirical power-law scalability ($O(N^{1.12})$), and double-blind word intrusion purity (92.5%).

---

## 📂 Repository Structure

```
BioDKM/
├── data/
│   └── pubmed_dataset.csv             # Corpus: 14,064 records across 8 disease classes
├── notebooks/                         # Interactive Jupyter replication notebooks
│   ├── API.ipynb                      # Step 1: PubMed query retrieval via NCBI E-utilities
│   ├── TF-IDF_disease_mapping.ipynb   # Step 2: Stream A (11-step TF-IDF + UMAP + HDBSCAN)
│   ├── BioBERT_disease_mapping.ipynb  # Step 3: Stream B (11-step BioBERT + UMAP + HDBSCAN)
│   ├── Topic_Coherence.ipynb          # Step 4: NPMI coherence evaluation across models
│   └── Manuscript_Analysis.ipynb      # Step 5: Clinical validation & macro/micro tables
├── kaggle_experiments/                # 16 Self-contained cloud GPU replication packages
│   ├── README.md                      # Detailed guide to cloud reproduction
│   ├── run_core_suite.py              # Suite orchestrator & mathematical isomorphism validator
│   ├── core_tfidf/                    # Stream A cloud runner (Stages 1–7)
│   ├── core_biobert/                  # Stream B cloud runner (BioBERT GPU embedding)
│   ├── core_coherence_manuscript/     # Harmonization runner (Stage 8 clinical engine)
│   ├── exp1_alignment/ ... exp13_word_intrusion/ # 13 Dedicated benchmark packages
├── results/                           # Empirical metrics and generated visual artifacts
│   ├── tfidf/                         # 11 Steps of artifacts for Stream A
│   ├── biobert/                       # 11 Steps of artifacts for Stream B
│   ├── coherence/                     # Combined evaluation metrics and NPMI plots
│   ├── manuscript/                    # Macro/micro tables and comparative figures
│   └── benchmarks/                    # Empirical data from all 13 benchmark experiments
├── requirements.txt                   # Environment dependencies
├── LICENSE                            # MIT License
└── README.md                          # Repository documentation
```

---

## ⚡ Quick Start

### 1. Environment Setup

Clone this repository and create a Python virtual environment:

```bash
git clone https://github.com/MIHMahmudEli/BioDKM.git
cd BioDKM

python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Interactive Notebook Execution

Execute the notebooks sequentially in `notebooks/`:

| Order | Notebook | Description |
|:---:|:---|:---|
| **1** | [`API.ipynb`](notebooks/API.ipynb) | Collect and parse PubMed records via NCBI E-utilities |
| **2** | [`TF-IDF_disease_mapping.ipynb`](notebooks/TF-IDF_disease_mapping.ipynb) | Stream A: 11-step TF-IDF representation, UMAP, and clustering |
| **3** | [`BioBERT_disease_mapping.ipynb`](notebooks/BioBERT_disease_mapping.ipynb) | Stream B: Contextual BioBERT embedding, UMAP, and clustering |
| **4** | [`Topic_Coherence.ipynb`](notebooks/Topic_Coherence.ipynb) | Calculate UCI NPMI coherence across all algorithms |
| **5** | [`Manuscript_Analysis.ipynb`](notebooks/Manuscript_Analysis.ipynb) | Generate Macro clinical categories and Micro comorbidity tables |

---

## ☁️ Cloud GPU Replication Suite (`kaggle_experiments/`)

To ensure 100% independent auditability without requiring local GPU workstations, BioDKM provides 16 self-contained reproduction packages runnable on Kaggle Cloud GPUs.

### Foundational Core Suite (Tripartite Architecture)
- **`core_tfidf`**: Stages 1–7 on sparse lexical features.
- **`core_biobert`**: Stages 1–7 utilizing `dmis-lab/biobert-v1.1` on NVIDIA Tesla T4/P100 GPUs.
- **`core_coherence_manuscript`**: Stage 8 harmonization, UCI NPMI calculation, and clinical synthesis.

To verify cross-stream hyperparameter isomorphism ($n\_neighbors=15, min\_dist=0.1, random\_state=42, min\_cluster\_size=30, min\_samples=5$):

```bash
python kaggle_experiments/run_core_suite.py
```

### Empirical Defense Benchmarks (`exp1` through `exp13`)
Each benchmark module contains its standalone runner and Kaggle kernel metadata:
- `exp1_alignment`: External disease alignment against 8 ground-truth diagnostic queries (ARI, NMI, Purity).
- `exp2_pubmedbert`: In-domain biomedical transformer validation using PubMedBERT.
- `exp3_baselines`: Rigorous comparison against LDA and BERTopic baselines.
- `exp4_ablation`: Dimensionality reduction ablation (Ambient vs. PCA vs. t-SNE vs. UMAP).
- `exp5_sensitivity`: Full hyperparameter grid sweep over $n\_neighbors$ and $min\_cluster\_size$.
- `exp6_stats`: Non-parametric Mann-Whitney U tests and 1,000-iteration bootstrap confidence intervals.
- `exp7_mesh_ontology`: MeSH tree depth semantic hierarchical verification.
- `exp8_disease_network`: Quantitative comorbidity affinity graph and trans-disease bridges.
- `exp9_scibert_sbert`: Multi-transformer comparison across SciBERT and Sentence-MiniLM.
- `exp10_noise_ablation`: Matched-core ablation evaluating density-based noise filtering impact.
- `exp11_subsampling_stability`: 10-fold subsampling stability and sentinel topic replication.
- `exp12_scalability`: Empirical runtime and memory complexity scaling curves ($O(N^{1.12})$).
- `exp13_word_intrusion`: Double-blind clinical word intrusion evaluation (92.5% intruder purity).

For detailed execution parameters, see [`kaggle_experiments/README.md`](kaggle_experiments/README.md).

---

## 📊 Core Benchmark Results

### Quantitative Comparison Across Representations & Algorithms

| Representation | Algorithm | Silhouette Score ↑ | Davies–Bouldin Index ↓ | UCI NPMI Coherence ↑ | Discovered Topics |
|:---|:---|:---:|:---:|:---:|:---:|
| **TF-IDF** | **HDBSCAN** | **0.4786** | **0.6034** | **0.1158** | **116** |
| **BioBERT** | **HDBSCAN** | 0.4225 | 0.7068 | 0.1154 | 80 |
| TF-IDF | K-Means ($K=5$) | 0.3708 | 0.8426 | 0.0780 | 5 |
| BioBERT | K-Means ($K=5$) | 0.4112 | 0.8124 | 0.0823 | 5 |
| TF-IDF | Hierarchical | 0.2791 | 0.9584 | 0.0709 | 5 |
| BioBERT | Hierarchical | 0.3660 | 0.8845 | 0.0598 | 5 |

<p align="center">
  <img src="results/manuscript/Figure1_HDBSCAN_vs_KMeans_Coherence.png" alt="HDBSCAN vs KMeans Coherence Comparison" width="85%"/>
</p>

*Statistical significance: TF-IDF HDBSCAN vs. BioBERT HDBSCAN NPMI coherence: $W = 4328.0, p = 0.416$ (two-sided Mann-Whitney U test, no significant difference), proving that lightweight lexical representations match contextual transformers in semantic coherence at a fraction of computational cost.*

---

## 🔬 Comorbidity Knowledge Discovery

BioDKM constructs a disease comorbidity affinity graph based on topic co-occurrence and trans-disease cluster bridges, identifying shared biomolecular mechanisms across seemingly disparate conditions (e.g., neuro-cardiovascular axes, metabolic-oncologic links).

<p align="center">
  <img src="results/benchmarks/exp8_disease_network/disease_knowledge_network.png" alt="Comorbidity Knowledge Network" width="90%"/>
</p>

---

## 🌐 Data & Pretrained Models

- **PubMed Corpus**: The complete dataset containing 14,064 preprocessed biomedical abstracts across 8 disease classes is publicly hosted on Hugging Face:  
  👉 [`MohsinElis/pubmed-disease-mapping`](https://huggingface.co/datasets/MohsinElis/pubmed-disease-mapping)
- **Domain Contextual Transformer**: Contextual embeddings utilize the official weights of:  
  👉 [`dmis-lab/biobert-v1.1`](https://huggingface.co/dmis-lab/biobert-v1.1)

---

## 📄 Citation

If you find this codebase, benchmark replication suite, or preprocessed datasets useful in your research, please cite:

```bibtex
@article{biodkm2026,
  title={BioDKM: An Unsupervised Topological Framework for Biomedical Disease Knowledge Mapping and Comorbidity Discovery from PubMed Literature},
  author={Mahmud, Mohsin and Prionty, Zarin and Contributors},
  journal={Computers in Biology and Medicine (Under Review)},
  year={2026},
  publisher={Elsevier}
}
```

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
