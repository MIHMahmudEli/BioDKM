# Manuscript Tables, Matrices & Empirical Results Data

This directory contains all CSV datasets, evaluation matrices, and empirical metrics supporting the tables, figures, and statistical benchmarks in the IEEE AJSE manuscript.

## Table & Figure Data Mapping

| Manuscript Float | CSV Filename | Description |
|:---|:---|:---|
| **Table 1** | `hyperparameter_sensitivity_results.csv` | Pipeline hyperparameter configuration and tuning results |
| **Table 2, Fig 4, Fig 5** | `combined_evaluation_metrics.csv`<br>`topic_coherence_summary.csv`<br>`topic_coherence_per_topic.csv` | Comprehensive silhouette, DB index, and NPMI topic coherence metrics across all 6 pipeline configurations |
| **Table 3, Fig 7** | `Table1_Macro_KMeans_Clinical_Validation.csv` | Macro-level clinical validation of KMeans clusters ($K=5$) with clinical category assignments |
| **Table 4, Fig 7** | `Table2_Micro_HDBSCAN_Top10.csv` | Micro-level subtopic discovery: top-10 highest-coherence HDBSCAN clusters |
| **Table 5** | `tfidf_step7_topic_keywords_per_cluster.csv`<br>`topic_coherence_per_topic.csv` | TF-IDF micro-level HDBSCAN topic discovery and per-cluster keywords |
| **Table 6, Table 7, Fig 10** | `baseline_topic_models_comparison.csv`<br>`baseline_topics.csv` | Topic modeling benchmarks: classical LDA ($K=5, 20$) and neural BERTopic vs. proposed framework |
| **Table 8, Fig 11** | `external_disease_alignment_metrics.csv` | Ground-truth disease alignment cross-tabulation matrix (ARI, NMI, Purity, F-Measure) |
| **Table 9, Fig 12** | `dim_reduction_ablation_metrics.csv` | Dimensionality reduction ablation (High-Dim, PCA 50D/2D, UMAP 2D) and neighborhood trustworthiness $T(k)$ |
| **Table 10, Fig 13** | `scalability_benchmark_metrics.csv`<br>`scalability_complexity_slopes.csv` | Algorithmic scalability runtime (ms), throughput (docs/s), and empirical power-law complexity slopes |
| **Table 11, Fig 6** | `bootstrap_confidence_intervals.csv`<br>`statistical_significance_results.csv` | Bootstrap 95% confidence intervals (1,000 iterations) and Mann-Whitney U test p-values |
| **Table 12, Fig 14** | `mesh_ontology_alignment_metrics.csv`<br>`mesh_category_distribution.csv`<br>`mesh_tree_depth_comparison.csv` | Quantitative 2024 NLM MeSH clinical ontology hierarchy alignment across tree depths 1 through 8 |
| **Table 13, Fig 15, Fig 16** | `disease_comorbidity_matrix.csv`<br>`multidisciplinary_bridge_clusters.csv` | Unsupervised pairwise disease comorbidity affinity matrix and multidisciplinary cross-disease bridge clusters |
| **Table 14, Fig 17** | `expanded_models_evaluation_metrics.csv`<br>`expanded_models_topics.csv`<br>`pubmedbert_evaluation_metrics.csv`<br>`pubmedbert_topics.csv` | Multi-architecture transformer evaluations: SciBERT, PubMedBERT, and Sentence-MiniLM |
| **Table 15, Fig 18** | `noise_ablation_comparison_metrics.csv`<br>`noise_vs_core_linguistic_profiles.csv`<br>`noise_top_keywords.csv` | Apples-to-apples noise ablation evaluating core clustered density vs. complete-corpus noise inclusion |
| **Table 16, Fig 19** | `subsampling_stability_summary_metrics.csv`<br>`sentinel_topic_replication_rates.csv`<br>`pairwise_fold_stability_matrix.csv` | Topological stability under 10-fold subsampling perturbations and pairwise Jaccard topic replication rates |
| **Section 5.13** | `word_intrusion_model_benchmark.csv`<br>`word_intrusion_sample_trials.csv` | Automated word intrusion purity evaluations and model precision margins |
| **Fig 2** | `biobert_step4_inter_concept_similarity.csv`<br>`tfidf_step4_inter_concept_similarity.csv` | Pairwise inter-concept centroid cosine similarity matrices across clinical query partitions |
| **Pipeline Step Metrics** | `biobert_step8_evaluation_metrics.csv`<br>`tfidf_step8_evaluation_metrics.csv`<br>`biobert_step9_keywords_per_cluster.csv`<br>`tfidf_step9_keywords_per_cluster.csv`<br>`biobert_step10_disease_knowledge_mapping.csv`<br>`tfidf_step10_disease_knowledge_mapping.csv` | Pipeline step evaluation metrics, cluster keyword profiles, and final disease knowledge mapping tables |
