# AGENTS.md — NLP-Biomedical-Disease-Mapping

Research project: unsupervised disease-mapping from PubMed abstracts comparing TF-IDF vs BioBERT embeddings with KMeans/HDBSCAN/Hierarchical clustering.

## Quick start

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No CI, no tests, no linting, no formatter, no typechecker. Open `.ipynb` files directly.

## Data

- `pubmed_dataset.csv` — ~27 MB, 14,065 rows, columns: `PMID`, `Title`, `Abstract`
- Collected from 8 disease queries via NCBI E-utilities (diabetes, cancer, cardiovascular, neurological, stroke, hypertension, Alzheimer's, Parkinson)
- Disease distribution: 1,504–1,951 records per disease

## Pipeline (execute notebooks in order)

### Python (5 notebooks)

| Step | Notebook | Purpose |
|---|---|---|
| 1 | `API.ipynb` | Collect PubMed abstracts (Biopython/E-utilities) |
| 2 | `TF-IDF_disease_mapping.ipynb` | 11-step: preprocessing → TF-IDF → UMAP → KMeans/HDBSCAN/Hierarchical → disease topic mapping |
| 3 | `BioBERT_disease_mapping.ipynb` | Same 11 steps, replaces TF-IDF with `dmis-lab/biobert-v1.1` 768-dim embeddings |
| 4 | `Topic_Coherence.ipynb` | NPMI coherence comparison across all 6 configurations (2 pipelines × 3 algorithms) |
| 5 | `Manuscript_Analysis.ipynb` | Publication-ready tables: macro (KMeans clinical labels) and micro (HDBSCAN top-10 topics) |

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

| Directory | Contents |
|---|---|
| `TF-IDF_Results/` | 11 CSVs + 11 PNGs (every pipeline step) |
| `BioBERT_Results/` | 11 CSVs + 11 PNGs (same structure) |
| `Coherence_Results/` | 3 CSVs + 4 PNGs (combined metrics, per-topic coherence) |
| `Manuscript_Results/` | 2 CSVs + 4 PNGs (macro/micro tables, pipeline architecture, comparison figure) |
| `Q1_Experiments_Results/` | 9 subdirectories containing all empirical CSV metrics and PNG plots for Q1 benchmarks |
| `kaggle_experiments/` | 9 self-contained reproduction scripts and metadata for cloud execution on Kaggle |

## LaTeX manuscript

- **File**: `AJSE_LaTeX/main.tex`
- **Output PDF**: `AJSE_LaTeX/main.pdf` (compiled, 19 pages)
- **Journal**: AJSE (Arabian Journal for Science and Engineering), IEEEtran format
- **Specs**: A4, double-blind, max 20 pages, ~180-word abstract (currently 19 pages, strictly under 20-page ceiling)
- **Status**: Publication-grade manuscript with 40 IEEE references, expanded TikZ architecture diagram, 17 figures, and 13 comprehensive tables.

### Manuscript sections

1. Title & Abstract (180 words, 5 representations, UMAP, HDBSCAN, baselines, MeSH grounding, disease network)
2. Introduction (6 RQs, domain context, limitations of prior work, 4 major contributions)
3. Related Work (5 subsections, comprehensive contextualization)
4. Methodology (8 coordinated stages, TikZ diagram, formal mathematical formulations including MeSH tree depth and comorbidity affinity)
5. Results (11 empirical subsections including baselines, ablation, disease alignment, hyperparameter sweeps, statistical tests, MeSH ontology grounding, comorbidity network, and expanded transformer benchmark)
6. Discussion (comprehensive synthesis across all 9 experiments, clinical translation, limitations, energy considerations)
7. Conclusion (crisp summary of principles and future outlook)
8. References (40 complete IEEE entries)

### Layout fixes applied

- Removed `float`/`caption` packages (incompatible with IEEEtran)
- Changed `[H]` → `[t]` on all floats
- Figure width: `\textwidth` → `\columnwidth`
- Wide table: converted to `table*` (double-column) with `\small`
- Long URL: changed to `\href` with short label
- `\textsuperscript` → `$^{n}$` math mode
- Added `\raggedbottom`, `\interdisplaylinepenalty`, `flushend`, `stfloats`
- IEEE `\appendices` environment

### Compile

```powershell
pdflatex -output-directory=AJSE_LaTeX AJSE_LaTeX\main.tex
```

Or upload `main.tex` + figure CSVs/PNGs to Overleaf project root.

## Scratch utilities

| Script | Purpose |
|---|---|
| `scratch/update_model_id.py` | Replace BioBERT model ID in notebook JSON |
| `scratch/convert_to_biobert.py` | Convert TF-IDF notebook → BioBERT notebook (replace imports, step 3, paths) |
| `scratch/upload_to_hf.py` | Host `pubmed_dataset.csv` directly on Hugging Face Hub |
| `scratch/verify_workers.py` | Test and authenticate Kaggle API tokens from `.env` |
| `scratch/launch_experiments.py` | Dispatch and push all experiment kernels to Kaggle cloud |
| `scratch/monitor_and_download.py` | Poll kernel runtimes and pull output CSVs/PNGs locally |
| `scratch/wait_and_pull.py` | Automatic monitoring loop for kernel outputs |

## Key gotchas

- BioBERT model ID was changed from `dmis-lab/biobert-v1.1-pubmed` to `dmis-lab/biobert-v1.1` — do not revert.
- Two pipeline scripts are gitignored (`run_biobert_pipeline.py`, `run_pipeline_step5_9.py`).
- Notebooks handle GPU/CPU fallback automatically (`torch.device('cuda' if torch.cuda.is_available() else 'cpu')`).
- All notebooks save outputs to disk as CSVs/PNGs — check those directories for results, not notebook outputs.
- Journal format: IEEEtran, double-blind (no author names), ~150-word abstract, max 20 pages.
- The `.doc` template (`AJSE Template 2020-OTH.doc`) is the official IEEE Word template (Feb 2017) — use the LaTeX version for submission.
