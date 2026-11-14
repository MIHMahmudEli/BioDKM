# Kaggle Cloud Reproduction Suite

Each directory in this folder contains a self-contained, standalone reproduction script and Kaggle `kernel-metadata.json` for one of the 6 Q1 empirical benchmarks.

All scripts download the verified dataset directly from Hugging Face:
`https://huggingface.co/datasets/MohsinElis/pubmed-disease-mapping/resolve/main/pubmed_dataset.csv`

---

## Experiment Kernels Roster

| Directory | Experiment Name | Kaggle Kernel Slug | Compute Node |
|---|---|---|---|
| `exp1_alignment/` | Ground-Truth Disease Alignment | `nihanshadman/exp1-disease-alignment-benchmark` | CPU / Standard |
| `exp2_pubmedbert/`| PubMedBERT SOTA Benchmark | `tasnimjenny/exp2-pubmedbert-benchmark` | GPU (Tesla P100 / T4) |
| `exp3_baselines/` | Baselines (LDA & BERTopic) | `mdzihan/exp3-baseline-topic-models` | CPU / Standard |
| `exp4_ablation/`  | Dimensionality Reduction Ablation | `rssiam/exp4-dim-reduction-ablation` | GPU / CPU |
| `exp5_sensitivity/`| Hyperparameter Sensitivity Sweeps | `leyamridha/exp5-hyperparameter-sensitivity` | CPU / Standard |
| `exp6_stats/`     | Statistical Tests & 1,000x Bootstrap | `sadmanhasanmiraj/exp6-statistical-significance` | CPU / Standard |

---

## How to Reproduce via Kaggle CLI

To push and run any experiment on Kaggle:

```powershell
# Set your Kaggle API Token
$env:KAGGLE_API_TOKEN = "<YOUR_KAGGLE_API_TOKEN>"

# Navigate to experiment directory
cd kaggle_experiments\exp1_alignment

# Push and run kernel
python -m kaggle kernels push -p .

# Check execution status
python -m kaggle kernels status nihanshadman/exp1-disease-alignment-benchmark

# Pull results after completion
python -m kaggle kernels output nihanshadman/exp1-disease-alignment-benchmark -p ../../Q1_Experiments_Results/exp1_alignment
```
