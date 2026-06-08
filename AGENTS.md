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

## LaTeX manuscript

- **File**: `AJSE_LaTeX/main.tex`
- **Journal**: AJSE (Arabian Journal for Science and Engineering), IEEEtran format
- **Specs**: A4, double-blind, max 5000 words, ~150-word abstract, 4–12 pages
- **Status**: Template created from IEEE Word template, Related Work section + 20 references integrated

### Manuscript sections (to fill)

1. Title & Abstract (placeholder)
2. Related Work (done — 5 subsections, 20 refs)
3. Methodology (TBD)
4. Results (TBD)
5. Discussion (TBD)
6. Conclusion (TBD)
7. References (20 entries, ready)

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

## Key gotchas

- BioBERT model ID was changed from `dmis-lab/biobert-v1.1-pubmed` to `dmis-lab/biobert-v1.1` — do not revert.
- Two pipeline scripts are gitignored (`run_biobert_pipeline.py`, `run_pipeline_step5_9.py`).
- Notebooks handle GPU/CPU fallback automatically (`torch.device('cuda' if torch.cuda.is_available() else 'cpu')`).
- All notebooks save outputs to disk as CSVs/PNGs — check those directories for results, not notebook outputs.
- Journal format: IEEEtran, double-blind (no author names), max 5000 words, ~150-word abstract, 4–12 pages.
- The `.doc` template (`AJSE Template 2020-OTH.doc`) is the official IEEE Word template (Feb 2017) — use the LaTeX version for submission.
