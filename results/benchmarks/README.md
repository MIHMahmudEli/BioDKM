# Empirical Benchmark Results & Evaluation Suite

This directory contains empirical results, evaluation metrics, and publication visualizations generated for the BioDKM biomedical topic modeling and disease knowledge mapping framework.

All heavy experiments were executed on cloud GPU/CPU nodes using the Kaggle Cloud Infrastructure and mirrored locally for full reproducibility.

---

## Directory Structure & Experiments Overview

### 1. `exp1_alignment/` — External Ground-Truth Disease Alignment
- **Kernel**: `nihanshadman/exp1-disease-alignment-benchmark`
- **Script**: `kaggle_experiments/exp1_alignment/exp1_alignment.py`
- **Description**: Benchmarks unsupervised clusters against the 8 underlying NCBI disease query categories (`cancer neoplasm`, `diabetes mellitus`, `stroke cerebrovascular`, `Alzheimer disease dementia`, `hypertension blood pressure`, `cardiovascular disease`, `neurological disorders`, `Parkinson disease`).
- **Key Metrics**:
  - `external_disease_alignment_metrics.csv`: ARI, NMI, Homogeneity, Completeness, V-Measure, and Cluster Purity across full corpus and non-noise subsets.
  - `disease_alignment_heatmaps.png`: Cross-tabulation heatmaps illustrating disease distributions across discovered clusters.
- **Key Finding**: TF-IDF HDBSCAN non-noise clusters achieve the highest cluster purity (0.4542) and homogeneity (0.2853), outperforming KMeans (purity 0.2841, homogeneity 0.1022).

---

### 2. `exp2_pubmedbert/` — SOTA Biomedical Representation Benchmark
- **Kernel**: `tasnimjenny/exp2-pubmedbert-benchmark`
- **Script**: `kaggle_experiments/exp2_pubmedbert/exp2_pubmedbert.py`
- **Description**: Evaluates `microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract` (pretrained from scratch on PubMed) against BioBERT and TF-IDF across KMeans, HDBSCAN, and Hierarchical clustering.
- **Key Metrics**:
  - `pubmedbert_evaluation_metrics.csv`: Silhouette, Davies--Bouldin, and NPMI topic coherence.
  - `pubmedbert_topics.csv`: Inferred disease topic labels and top keywords.
  - `pubmedbert_umap_clusters.png`: 2D UMAP projection maps.

---

### 3. `exp3_baselines/` — Classical & Neural Topic Modeling Baselines
- **Kernel**: `mdzihan/exp3-baseline-topic-models`
- **Script**: `kaggle_experiments/exp3_baselines/exp3_baselines.py`
- **Description**: Direct comparison against classical Latent Dirichlet Allocation (LDA $K=5, K=8$) and standard neural BERTopic (`all-MiniLM-L6-v2` + default UMAP + HDBSCAN + c-TF-IDF).
- **Key Metrics**:
  - `baseline_topic_models_comparison.csv`: Topic count, NPMI coherence, topic diversity, and execution runtime (seconds).
  - `baseline_topics.csv`: Extracted top keywords for each baseline model.
  - `baseline_coherence_comparison.png`: NPMI coherence comparison plot.
- **Key Finding**: TF-IDF + HDBSCAN executes in 12.4 seconds ($3.5\times$ faster than LDA, $5.7\times$ faster than BERTopic) with high topic diversity (0.812). BioBERT + HDBSCAN achieves the highest topic diversity (0.845). Standard BERTopic over-fragments into 218 micro-clusters with lower diversity (0.739).

---

### 4. `exp4_ablation/` — Dimensionality Reduction Ablation & Trustworthiness
- **Kernel**: `rssiam/exp4-dim-reduction-ablation`
- **Script**: `kaggle_experiments/exp4_ablation/exp4_ablation.py`
- **Description**: Mathematical ablation comparing Direct High-Dimensional clustering (5,000D TF-IDF, 768D BioBERT), Linear PCA (50D, 2D), and Non-linear UMAP (2D). Evaluates neighborhood preservation using the Trustworthiness metric ($T$).
- **Key Metrics**:
  - `dim_reduction_ablation_metrics.csv`: Dimensionality, discovered cluster count, Silhouette score, and neighborhood Trustworthiness ($T$).
  - `trustworthiness_comparison.png`: Scatter plot of Trustworthiness vs. Silhouette score.
- **Key Finding**: In ambient unreduced space, HDBSCAN fails to detect clusters (0 discovered) due to distance concentration. Linear PCA suffers from severe topological distortion ($T \approx 0.70$) and negative Silhouette. UMAP preserves local neighborhood topology ($T = 0.8825$ for TF-IDF, $0.8429$ for BioBERT), proving non-linear projection is mathematically necessary.

---

### 5. `exp5_sensitivity/` — Hyperparameter Robustness Sweeps
- **Kernel**: `leyamridha/exp5-hyperparameter-sensitivity`
- **Script**: `kaggle_experiments/exp5_sensitivity/exp5_sensitivity.py`
- **Description**: Sweeps HDBSCAN `min_cluster_size` $\in [15, 100]$ and UMAP `n_neighbors` $\in [5, 50]$ across both TF-IDF and BioBERT pipelines.
- **Key Metrics**:
  - `hyperparameter_sensitivity_results.csv`: Cluster count, noise ratio, Silhouette score, Davies--Bouldin index, and NPMI coherence for each setting.
  - `sensitivity_curves.png`: Multi-panel sensitivity curves demonstrating monotonic cluster scaling and stable metric plateaus.
- **Key Finding**: Minimum cluster size provides smooth control over topic granularity (scaling from 244 topics down to 33 topics) while maintaining stable Silhouette ($0.45$--$0.56$) and NPMI ($0.12$--$0.15$).

---

### 6. `exp6_stats/` — Statistical Significance & Bootstrap 95% CIs
- **Kernel**: `sadmanhasanmiraj/exp6-statistical-significance`
- **Script**: `kaggle_experiments/exp6_stats/exp6_stats.py`
- **Description**: Non-parametric Mann--Whitney U and Wilcoxon tests on per-topic coherence distributions, plus 1,000-iteration bootstrapping with replacement.
- **Key Metrics**:
  - `statistical_significance_results.csv`: Pairwise U statistics, W statistics, and exact $p$-values.
  - `bootstrap_confidence_intervals.csv`: Mean NPMI, empirical 95% CI bounds, and standard errors.
  - `coherence_distribution_violin.png`: Violin plots illustrating full topic distributions, medians, quartiles, and high-coherence tails.
- **Key Finding**: Mann--Whitney U test proves TF-IDF vs. BioBERT under HDBSCAN is non-significant ($U = 4322.0, p = 0.416$), confirming statistical equivalence. HDBSCAN significantly outperforms KMeans ($p = 0.0109$) and Hierarchical ($p < 0.001$).

---

### 7. `exp7_mesh_ontology/` — Quantitative MeSH Clinical Ontology Grounding & Tree Depth
- **Kernel**: `nishat1156/exp7-mesh-ontology`
- **Script**: `kaggle_experiments/exp7_mesh_ontology/exp7_mesh_ontology.py`
- **Description**: Quantitatively grounds unsupervised cluster keywords against the National Library of Medicine (NLM) Medical Subject Headings (MeSH 2024) hierarchy across semantic categories and tree depths.
- **Key Metrics**:
  - `mesh_ontology_alignment_metrics.csv`: Mapping rates, matched keyword counts, mean, median, and maximum tree depths.
  - `mesh_category_distribution.csv`: Proportions across Diseases [C], Chemicals/Drugs [D], Anatomy [A], Techniques [E], and Biological Phenomena [G].
  - `mesh_tree_depth_comparison.csv`: Tree depth distributions across configurations.
  - `mesh_ontology_alignment.png`: 3-panel publication visualization (mapping rate, category breakdown, tree depth distribution).
- **Key Finding**: While KMeans clusters concentrate at broad organ-system levels (depths 2–3), HDBSCAN discovers hundreds of terms reaching granular tree depths 4, 5, and 6 (e.g., *Diabetic Foot Ulcer*, *Phosphorylated Tau*, *Alpha-Synuclein Fibrils*), verifying 764 standardized MeSH entities under TF-IDF.

---

### 8. `exp8_disease_network/` — Unsupervised Cross-Disease Comorbidity & Thematic Bridge Network
- **Kernel**: `afrojahaqueshornaly/exp8-disease-network`
- **Script**: `kaggle_experiments/exp8_disease_network/exp8_disease_network.py`
- **Description**: Reconstructs an 8x8 pairwise disease comorbidity matrix and circular knowledge network using cosine similarity of normalized cluster-occupancy distributions, isolating multidisciplinary bridge clusters.
- **Key Metrics**:
  - `disease_comorbidity_matrix.csv`: 8x8 pairwise cosine affinity matrix across disease classes.
  - `multidisciplinary_bridge_clusters.csv`: Discovered bridge clusters, joint occupancy products, extracted keywords, and clinical interpretations.
  - `disease_knowledge_network.png`: High-resolution circular network graph showing disease nodes, edge thickness weighted by affinity, and bridge cluster annotations.
  - `disease_comorbidity_chord_heatmap.png`: Clustered comorbidity affinity heatmap with hierarchical dendrogram.
- **Key Finding**: Automatically reconstructs major clinical disease axes without pair-level supervision: Cardiovascular--Stroke (0.812), Alzheimer's--Stroke (0.782), Alzheimer's--Hypertension (0.781), Cancer--Cardiovascular (0.837), and Alzheimer's--Parkinson's (0.615).

---

### 9. `exp9_scibert_sbert/` — Multi-Architecture Scientific & Sentence-Transformer Benchmark
- **Kernel**: `abdullahalsayfan/exp9-scibert-sbert`
- **Script**: `kaggle_experiments/exp9_scibert_sbert/exp9_scibert_sbert.py`
- **Description**: Evaluates multi-domain scientific model `allenai/scibert_scivocab_uncased` and dense sentence bi-encoder `sentence-transformers/all-MiniLM-L6-v2` across KMeans and HDBSCAN.
- **Key Metrics**:
  - `expanded_models_evaluation_metrics.csv`: Topic count, Silhouette score, Davies--Bouldin index, NPMI coherence, and topic diversity.
  - `expanded_models_topics.csv`: Extracted cluster topics and keywords.
  - `expanded_models_comparison.png`: 3-panel comparative performance plot.
- **Key Finding**: Sentence-MiniLM with HDBSCAN achieves an exceptional NPMI coherence of 0.1270 across 95 topics with DB 0.6171 and Silhouette 0.4041. SciBERT HDBSCAN achieves NPMI 0.0956 (50 topics), outperforming SciBERT KMeans (0.0663) by 44.2%, corroborating that the density-based advantage is architecture-invariant.

---

### 10. `exp10_noise_ablation/` — Apples-to-Apples Noise Infiltration & Soft Outlier Assignment
- **Kernel**: `baingalamukintu/exp10-noise-ablation`
- **Script**: `kaggle_experiments/exp10_noise_ablation/exp10_noise_ablation.py`
- **Description**: Directly refutes the potential reviewer criticism that HDBSCAN's performance advantage is an artifact of discarding 30% noise. Compares HDBSCAN against KMeans ($K=123$ and $K=5$) and Hierarchical clustering on the identical matched core subset ($N=9{,}822$, 69.8% coverage), and benchmarks 100% full-corpus coverage using soft $k$-NN neighbor projection ($N=14{,}064$).
- **Key Metrics**:
  - `noise_ablation_comparison_metrics.csv`: Coverage %, document count, cluster count, Silhouette score, Davies--Bouldin index, and mean NPMI coherence.
  - `noise_vs_core_linguistic_profiles.csv`: Document lengths, disease distribution entropy, and clinical nature of core versus noise.
  - `noise_top_keywords.csv`: Top 20 terms dominating the noise boundary partition.
  - `noise_ablation_evaluation.png`: 3-panel publication figure comparing metrics across scopes, coherence distributions, and linguistic entropy.
- **Key Finding**: HDBSCAN maintains superior cluster compactness on the matched core subset ($\text{DB} = 0.5892$ vs. 0.8494 for KMeans and 1.0714 for Hierarchical). Under 100% full-corpus soft assignment, HDBSCAN achieves $\text{DB} = 0.8286$ and $\text{NPMI} = 0.0931$, outperforming full-corpus KMeans ($\text{DB} = 0.8659, \text{NPMI} = 0.0711$) and Hierarchical ($\text{DB} = 0.9464, \text{NPMI} = 0.0646$). Noise documents are proven to be genuine multi-disease clinical reviews ($H = 2.978$ bits) rather than corrupt text.

---

### 11. `exp11_subsampling_stability/` — 10-Fold Subsampling Perturbation & Topological Manifold Stability
- **Kernel**: `abhafnan/exp11-subsampling-stability`
- **Script**: `kaggle_experiments/exp11_subsampling_stability/exp11_subsampling_stability.py`
- **Description**: Evaluates empirical reproducibility across 10 independent random 80% subsamples ($N=11{,}251$ per fold) across 10 random seeds ($S \in \{42, 101, 202, 303, 404, 505, 606, 707, 808, 909\}$). Evaluates pairwise ARI/AMI partition stability across all $\binom{10}{2} = 45$ combinations and tracks replication rates of key clinical sentinel topics.
- **Key Metrics**:
  - `subsampling_stability_summary_metrics.csv`: Fold-by-fold topic count, core/noise proportions, Silhouette, Davies--Bouldin, and NPMI.
  - `pairwise_fold_stability_matrix.csv`: Pairwise ARI and AMI on common documents and core documents for all 45 combinations.
  - `sentinel_topic_replication_rates.csv`: Cross-fold discovery rates and keyword Jaccard overlap for 6 clinical sentinel topics.
  - `cluster_subsampling_stability.png`: 3-panel publication figure showing fold-by-fold metric stability, pairwise AMI matrix, and sentinel topic replication.
- **Key Finding**: Manifold stability across independent 80% subsamples is extraordinarily high: Mean Core Adjusted Mutual Information is $\mathbf{0.7498 \pm 0.0110}$ (tight range 0.7294 to 0.7801). Cluster count remains steady at $100.9 \pm 6.1$, Silhouette at $0.4988 \pm 0.0219$, and NPMI at $0.1132 \pm 0.0053$. Five out of six clinical sentinel biomarker topics achieve a $\mathbf{100\%}$ replication rate across all 10 folds.

---

### 12. `exp12_scalability/` — Algorithmic Scalability & Asymptotic Computational Complexity
- **Kernel**: `mihjihad/exp12-scalability-benchmark`
- **Script**: `kaggle_experiments/exp12_scalability/exp12_scalability.py`
- **Description**: Benchmarks empirical execution latency, peak memory consumption, and document processing throughput across corpus scales ($N \in [1{,}000, 2{,}500, 5{,}000, 7{,}500, 10{,}000, 14{,}064, 20{,}000]$) to establish asymptotic power-law complexity exponents ($\log_{10} T \propto \alpha \log_{10} N$).
- **Key Metrics**:
  - `scalability_benchmark_metrics.csv`: Full breakdown of feature extraction, UMAP projection, and clustering time across scales.
  - `scalability_complexity_slopes.csv`: Fitted log-log regression slope $\alpha$, intercept, empirical complexity class, and throughput.
  - `scalability_complexity_evaluation.png`: 3-panel publication figure showing latency scaling, throughput curves, and stage runtime breakdown.
- **Key Finding**: UMAP+HDBSCAN scales with a sub-linear/near-linear empirical slope of $\alpha = 0.326$, avoiding the quadratic $O(N^2)$ distance explosion. TF-IDF + HDBSCAN achieves a sustained processing throughput of **451.4 documents per second**, operating **$16.5\times$ faster than BERTopic** (27.4 docs/s) and **$21.2\times$ faster than BioBERT** (21.3 docs/s).

---

### 13. `exp13_word_intrusion/` — Quantitative Automated Word Intrusion & Topic Purity Benchmark
- **Kernel**: `almasukmim12/exp13-word-intrusion`
- **Script**: `kaggle_experiments/exp13_word_intrusion/exp13_word_intrusion.py`
- **Description**: Implements the classic Chang et al. (NeurIPS) Word Intrusion cognitive test across all models. For every topic, injects an intruder word from a distant topic and evaluates whether an objective semantic judge detects the outlier based on global term co-occurrence similarity.
- **Key Metrics**:
  - `word_intrusion_model_benchmark.csv`: Evaluated topic count, intruder detection accuracy (%), mean topic purity score, and mean intrusion separation margin.
  - `word_intrusion_sample_trials.csv`: Sample trials recording authentic keywords, injected intruder, predicted intruder, hit status, and margin.
  - `word_intrusion_evaluation.png`: 3-panel publication figure displaying detection accuracy, topic purity, and separation margins.
- **Key Finding**: TF-IDF + HDBSCAN achieves **98.55% Intruder Detection Accuracy** across 207 fine-grained topics with a high separation margin of 0.1453, matching deep neural BERTopic (98.55%) and BioBERT (97.50%). This proves that discovered density topics have sharp semantic boundaries without lexical bleed or cross-topic contamination.


