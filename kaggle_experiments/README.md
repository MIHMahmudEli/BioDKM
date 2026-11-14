# Kaggle Cloud Reproduction Suite for BioDKM

This directory contains 16 self-contained, standalone reproduction modules and Kaggle `kernel-metadata.json` definitions for the entire BioDKM framework and its empirical evaluation suite.

All experiments stream the verified corpus directly from Hugging Face:
`https://huggingface.co/datasets/MohsinElis/pubmed-disease-mapping/resolve/main/pubmed_dataset.csv`

---

## Architectural Mapping & Kernel Roster

The suite is mapped directly to the 8 coordinated stages of the BioDKM architecture:

### 1. Core End-to-End Pipelines (Stages 1–8)

| Directory | Pipeline Component | Kaggle Kernel Slug | Architectural Stage | Hardware Target |
|---|---|---|---|---|
| `core_tfidf/` | Sparse Lexical Pipeline (11 Steps) | `aicontentdetections/biodkm-core-tf-idf-pipeline` | Stages 1–7 (TF-IDF Stream) | CPU / Standard |
| `core_biobert/` | Contextual Transformer Pipeline (11 Steps) | `zarinprionty/biodkm-core-biobert-gpu-pipeline` | Stages 1–7 (BioBERT Stream) | GPU (Tesla P100 / T4) |
| `core_coherence_manuscript/` | NPMI Topic Coherence & Clinical Validation | `studyhub991/biodkm-core-coherence-and-manuscript-analysis` | Stage 8 (Quantitative Validation) | Standard / GPU |

---

### 2. Empirical Benchmark Suite (Stage 8 Extended Validation)

| Directory | Experiment Name | Kaggle Kernel Slug | Architectural Stage / Focus | Hardware Target |
|---|---|---|---|---|
| `exp1_alignment/` | External Disease Alignment | `nihanshadman/exp1-disease-alignment-benchmark` | Stage 7 Concept Alignment | CPU / Standard |
| `exp2_pubmedbert/` | PubMedBERT Representation Benchmark | `tasnimjenny/exp2-pubmedbert-benchmark` | Stage 2 Domain Adaptation | GPU (Tesla P100 / T4) |
| `exp3_baselines/` | Baselines (LDA, NMF, GSDMM, BERTopic) | `mdzihan/exp3-baseline-topic-models` | Stage 5 & 8 Baseline Comparison | CPU / Standard |
| `exp4_ablation/` | Dimensionality Reduction Ablation | `rssiam/exp4-dim-reduction-ablation` | Stage 4 Manifold Ablation | Standard |
| `exp5_sensitivity/` | Hyperparameter Sensitivity Sweeps | `leyamridha/exp5-hyperparameter-sensitivity` | Stage 4 & 5 Parameter Robustness | CPU / Standard |
| `exp6_stats/` | Statistical Tests & 1,000x Bootstrap | `sadmanhasanmiraj/exp6-statistical-significance` | Stage 8 Significance Testing | CPU / Standard |
| `exp7_mesh_ontology/`| MeSH Clinical Ontology Grounding | `nishat1156/exp7-mesh-ontology` | Stage 7 Semantic Grounding | CPU / Standard |
| `exp8_disease_network/`| Comorbidity Knowledge Network | `afrojahaqueshornaly/exp8-disease-network` | Stage 7 Graph Topology & Bridges | CPU / Standard |
| `exp9_scibert_sbert/` | Expanded Transformer Models (SciBERT, SBERT) | `abdullahalsayfan/exp9-scibert-sbert` | Stage 2 Representation Generalization | GPU (Tesla P100 / T4) |
| `exp10_noise_ablation/`| HDBSCAN Density Noise Filtering Ablation | `baingalamukintu/exp10-noise-ablation` | Stage 5 Matched-Core Evaluation | CPU / Standard |
| `exp11_subsampling_stability/`| 10-Fold Subsampling Perturbation | `abhafnan/exp11-subsampling-stability` | Stage 5 & 8 Topological Stability | CPU / Standard |
| `exp12_scalability/` | Algorithmic Scalability & Complexity ($O$) | `mihjihad/exp12-scalability-benchmark` | Stage 4 & 5 Runtime Scaling | CPU / Standard |
| `exp13_word_intrusion/`| Word Intrusion Purity Protocol | `almasukmim12/exp13-word-intrusion` | Stage 8 Semantic Defensibility | Standard |

---

## Reproduction Workflow via Kaggle CLI

Execute any pipeline or benchmark on Kaggle cloud resources using the authenticated API token:

```powershell
# 1. Set Kaggle Authentication Token
$env:KAGGLE_API_TOKEN = "<TOKEN_FROM_ENV>"

# 2. Push experiment to Kaggle
python -m kaggle kernels push -p kaggle_experiments/core_biobert

# 3. Monitor kernel execution status
python -m kaggle kernels status zarinprionty/biodkm-core-biobert-gpu-pipeline

# 4. Pull empirical artifacts (CSVs and 300 DPI figures) upon completion
python -m kaggle kernels output zarinprionty/biodkm-core-biobert-gpu-pipeline -p results/biobert
```
