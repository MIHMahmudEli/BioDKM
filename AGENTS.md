# AGENTS.md — NLP-Biomedical-Disease-Mapping

Research project: unsupervised disease-mapping from PubMed abstracts comparing TF-IDF vs BioBERT embeddings with KMeans/HDBSCAN/Hierarchical clustering.

## Quick start

```bash
# Activate venv (Python 3.14)
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No CI, no tests, no linting, no formatter, no typechecker. Open `.ipynb` files directly.

## Architecture

- **Notebooks** (run in order within each pipeline):
  - `API.ipynb` — collect PubMed abstracts (uses Biopython/E-utilities)
  - `TF-IDF_disease_mapping.ipynb` — TF-IDF pipeline
  - `BioBERT_disease_mapping.ipynb` — BioBERT pipeline (model: `dmis-lab/biobert-v1.1`)
  - `Topic_Coherence.ipynb` — NPMI coherence comparison
  - `Manuscript_Analysis.ipynb` — publication-ready tables and figures
- **Data**: `pubmed_dataset.csv` (~14K rows, columns: `PMID`, `Title`, `Abstract`)
- **Outputs**: `TF-IDF Results/`, `BioBERT Results/`, `Coherence Results/`, `Manuscript Results/` (auto-created by notebooks)
- **R implementation**: `disease_mapping.R` (parallel pipeline, CRAN packages via `install.packages`)
- **LaTeX manuscript**: `AJSE_LaTeX/main.tex` (IEEEtran, A4, double-blind for AJSE)
- **Compile locally** from repo root: `pdflatex -output-directory=AJSE_LaTeX AJSE_LaTeX\main.tex`
- **Overleaf**: upload `main.tex` to project root with result folders alongside
- **`scratch/`**: utility scripts for notebook manipulation (model ID updates, TF-IDF → BioBERT conversion)

## Key gotchas

- BioBERT model ID was changed from `dmis-lab/biobert-v1.1-pubmed` to `dmis-lab/biobert-v1.1` — do not revert.
- Two pipeline scripts are gitignored (`run_biobert_pipeline.py`, `run_pipeline_step5_9.py`).
- Notebooks handle GPU/CPU fallback automatically (`torch.device('cuda' if torch.cuda.is_available() else 'cpu')`).
- All notebooks save outputs to disk as CSVs/PNGs — check those directories for results, not notebook outputs.
- Journal format: IEEEtran, double-blind (no author names), max 5000 words, ~150-word abstract, 4–12 pages.
