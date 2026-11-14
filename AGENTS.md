# AGENTS.md — BioDKM: Biomedical Disease Knowledge Mapping

Research project: **BioDKM** — An Unsupervised Topological Framework for Biomedical Disease Knowledge Mapping and Comorbidity Discovery from PubMed Literature (Elsevier CAS double-column format).

## Quick start

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No CI, no tests, no linting, no formatter, no typechecker. Open `.ipynb` files directly.

## Data

- `data/pubmed_dataset.csv` — ~27 MB, 14,065 rows, columns: `PMID`, `Title`, `Abstract`
- Collected from 8 disease queries via NCBI E-utilities (diabetes, cancer, cardiovascular, neurological, stroke, hypertension, Alzheimer's, Parkinson)
- Disease distribution: 1,504–1,951 records per disease

## Pipeline (execute notebooks in order)

### Python (5 notebooks)

| Step | Notebook | Purpose |
|---|---|---|
| 1 | `notebooks/API.ipynb` | Collect PubMed abstracts (Biopython/E-utilities) |
| 2 | `notebooks/TF-IDF_disease_mapping.ipynb` | 11-step: preprocessing → TF-IDF → UMAP → KMeans/HDBSCAN/Hierarchical → disease topic mapping |
| 3 | `notebooks/BioBERT_disease_mapping.ipynb` | Same 11 steps, replaces TF-IDF with `dmis-lab/biobert-v1.1` 768-dim embeddings |
| 4 | `notebooks/Topic_Coherence.ipynb` | NPMI coherence comparison across all 6 configurations (2 pipelines × 3 algorithms) |
| 5 | `notebooks/Manuscript_Analysis.ipynb` | Publication-ready tables: macro (KMeans clinical labels) and micro (HDBSCAN top-10 topics) |

### R implementation

- `disease_mapping.R` — TF-IDF only, fixed K=8, parallel pipeline using CRAN packages (tm, uwot, dbscan, cluster, factoextra, tidytext, ggplot2)

## Key results

| Configuration | Silhouette | DB Index | NPMI Coherence | Topics |
|---|---|---|---|---|
| **TF-IDF HDBSCAN** | **0.4786** | 0.6034 | **0.1158** | 116 |
| **BioBERT HDBSCAN** | 0.4225 | 0.7068 | 0.1154 | 80 |
| TF-IDF KMeans (K=5) | 0.3708 | 0.8426 | 0.0780 | 5 |
| BioBERT KMeans (K=5) | 0.4112 | 0.8124 | 0.0823 | 5 |
| TF-IDF Hierarchical | 0.2791 | 0.9584 | 0.0709 | 5 |
| BioBERT Hierarchical | 0.3660 | 0.8845 | 0.0598 | 5 |

HDBSCAN produces many more fine-grained topics with higher coherence. TF-IDF and BioBERT are effectively tied on NPMI.

### Manuscript Analysis — Clinical Validation

- **Macro (KMeans)**: 5 manually-labeled clinical categories (Cardiovascular & Metabolic Risk, Preclinical Molecular Biology, Oncology & Case Studies, Clinical Outcomes & Mortality, Neurocognitive Disorders)
- **Micro (HDBSCAN)**: Top-10 highest-coherence subtopics (e.g., Ptau Plasma 0.322, Syn Disease 0.282, Gut Microbiota 0.226)

## Output directories

All experimental outputs are organized under `results/`:

| Directory | Contents |
|---|---|
| `results/tfidf/` | 11 CSVs + 11 PNGs (every pipeline step for sparse TF-IDF) |
| `results/biobert/` | 11 CSVs + 11 PNGs (every pipeline step for contextual BioBERT) |
| `results/coherence/` | 3 CSVs + 4 PNGs (combined metrics, per-topic coherence) |
| `results/manuscript/` | 2 CSVs + 4 PNGs (macro/micro tables, pipeline architecture, comparison figure) |
| `results/benchmarks/` | 13 subdirectories containing empirical CSV metrics and PNG plots for benchmark evaluations |
| `kaggle_experiments/` | 16 self-contained reproduction packages (3 core + 13 benchmarks) for cloud execution on Kaggle |

## LaTeX manuscript

- **Title**: *BioDKM: An Unsupervised Topological Framework for Biomedical Disease Knowledge Mapping and Comorbidity Discovery from PubMed Literature*
- **File**: `Elsevier_LaTeX/main.tex`
- **Output PDF**: `Elsevier_LaTeX/main.pdf` (compiled, 23 pages)
- **Journal**: Elsevier CAS double-column (`cas-dc` format)
- **Status**: Publication-grade manuscript with 40 verified 2023–2026 references (100% top-tier: Elsevier, Springer Nature, IEEE, Oxford, Frontiers, MDPI, SAGE with verified DOIs), expanded TikZ architecture diagram, 19 figures, and 16 comprehensive tables.
- **Figures Directory**: `Elsevier_LaTeX/figures/` (self-contained directory containing all manuscript figures + vector/raster architecture diagrams).
- **Tables & Data Directory**: `Elsevier_LaTeX/tables/` (self-contained directory containing all manuscript table CSVs, evaluation matrices, and empirical metrics for full replication; mirrored at `Elsevier_LaTeX/data/`).

### Manuscript sections

1. Title & Abstract (180 words, 5 representations, UMAP, HDBSCAN, baselines, MeSH grounding, disease network, noise ablation, stability, scalability, word intrusion)
2. Introduction (6 RQs, domain context, limitations of prior work, 5 major contributions)
3. Related Work (5 subsections, comprehensive contextualization)
4. Methodology (8 coordinated stages, TikZ diagram, formal mathematical formulations including MeSH tree depth, comorbidity affinity, matched-core noise ablation, 10-fold subsampling stability, word intrusion protocol, and empirical power-law scalability)
5. Results (13 empirical subsections including baselines, ablation, disease alignment, hyperparameter sweeps, statistical tests, MeSH ontology grounding, comorbidity network, expanded transformer benchmark, apples-to-apples noise ablation, 10-fold subsampling stability, algorithmic scalability, and word intrusion purity)
6. Discussion (comprehensive synthesis across all 13 experiments, clinical translation, limitations, energy considerations, defense of noise filtering, and topological manifold stability)
7. Conclusion (crisp summary of principles and future outlook)
8. References (40 verified 2023–2026 entries with valid DOIs from Elsevier, Springer Nature, IEEE, Oxford, Frontiers, MDPI, and SAGE)

### Compile

```powershell
pdflatex -interaction=nonstopmode -output-directory=Elsevier_LaTeX Elsevier_LaTeX\main.tex
```

Or upload `Elsevier_LaTeX/` contents to Overleaf.

## Key gotchas

- BioBERT model ID was changed from `dmis-lab/biobert-v1.1-pubmed` to `dmis-lab/biobert-v1.1` — do not revert.
- Two pipeline scripts are gitignored (`run_biobert_pipeline.py`, `run_pipeline_step5_9.py`).
- Notebooks handle GPU/CPU fallback automatically (`torch.device('cuda' if torch.cuda.is_available() else 'cpu')`).
- All notebooks save outputs to disk as CSVs/PNGs — check those directories for results, not notebook outputs.
- Journal format: Elsevier CAS double-column format (`Elsevier_LaTeX/main.tex` -> `Elsevier_LaTeX/main.pdf`), with full author metadata.
