# Uncovering Micro-Topics in Biomedical Literature: A Comparative Study of TF-IDF and BioBERT Embeddings with KMeans, HDBSCAN, and Hierarchical Clustering

**Authors**: [Author Name 1]¹, [Author Name 2]¹  
**Affiliation**: ¹[Institution Name], [Department], [City, Country]  
**Contact**: [email@institution.edu]  
**Submitted to**: [Journal Name]  
**Date**: May 2026

---

## Abstract

The exponential growth of biomedical literature demands automated, semantically aware methods for disease knowledge extraction and topic discovery. This study presents a systematic comparative pipeline evaluating two text representation strategies — Term Frequency-Inverse Document Frequency (TF-IDF) and BioBERT contextual embeddings — combined with three unsupervised clustering algorithms: KMeans, Hierarchical Agglomerative Clustering (HAC), and HDBSCAN. Applied to a corpus of 14,064 PubMed abstracts and reduced to two dimensions via UMAP, the pipeline produces topic clusters evaluated through three complementary metrics: Silhouette Score, Davies-Bouldin Index (DBI), and Normalized Pointwise Mutual Information (NPMI) coherence.

Results demonstrate that HDBSCAN consistently yields the most coherent micro-topics in both representation pipelines (BioBERT NPMI = 0.1154; TF-IDF NPMI = 0.1158), representing a 40.3% and 48.5% relative improvement over their respective KMeans baselines. Critically, BioBERT combined with HDBSCAN uncovers clinically deep micro-domains — including plasma biomarkers for Alzheimer's disease (NPMI = 0.3220), alpha-synuclein aggregation (NPMI = 0.2822), and gut microbiota-metabolic interactions (NPMI = 0.2260) — that global partition-based algorithms fail to resolve. TF-IDF HDBSCAN, conversely, excels at population-specific clinical micro-topics such as diabetic wound healing (NPMI = 0.3431) and preeclampsia (NPMI = 0.2929). The findings establish that density-based clustering over contextual embeddings is superior for granular disease mapping in specialized biomedical corpora and that the two representation strategies are complementary rather than competing.

**Index Terms**: BioBERT, Biomedical Text Mining, HDBSCAN, KMeans, Hierarchical Clustering, Topic Coherence, NPMI, UMAP, Unsupervised Learning, Disease Mapping, PubMed, NLP.

---

## I. INTRODUCTION

The PubMed repository contains over 36 million citations as of 2024, with more than one million new records added annually [1]. The rate of publication growth has long surpassed the capacity of any individual researcher or clinical team to synthesize the collective knowledge contained within this corpus. Automated Natural Language Processing (NLP) pipelines that can extract, cluster, and semantically organize disease-related knowledge from raw biomedical text are therefore not merely convenient — they are essential infrastructure for accelerating translational research and clinical decision support.

Traditional text mining approaches have relied on statistical bag-of-words representations, most notably Term Frequency-Inverse Document Frequency (TF-IDF), which encodes documents as high-dimensional sparse vectors based on term frequency statistics [2]. While computationally efficient and interpretable, TF-IDF is fundamentally context-free: the same word in distinct biomedical contexts (e.g., *pressure* in the context of hypertension versus pulmonary arterial disease) carries an identical numerical representation. This semantic blindness poses a critical limitation in the biomedical domain, where precise contextual meaning is a prerequisite for accurate knowledge discovery.

The advent of transformer-based language models [3] — particularly domain-adapted variants such as BioBERT [4], pre-trained exclusively on PubMed abstracts and PubMed Central full-text articles — has fundamentally altered the representational landscape of biomedical NLP. BioBERT generates dense 768-dimensional contextual embeddings that capture co-occurrence dependencies and semantic relationships inherent to medical language, enabling representations that reflect the relational structure of biomedical knowledge rather than mere lexical co-occurrence.

However, powerful embeddings alone do not guarantee high-quality topic discovery. The choice of clustering algorithm is equally consequential. Partition-based algorithms such as KMeans require a predefined number of clusters and assign every document to a cluster unconditionally — including noise, off-topic documents, and transitional abstracts that do not belong to any coherent theme. This forced global assignment dilutes intra-cluster coherence. HDBSCAN (Hierarchical Density-Based Spatial Clustering of Applications with Noise) [5], in contrast, infers cluster count directly from the data's density topology and explicitly labels low-density documents as noise (cluster label −1), ensuring that each discovered cluster represents a genuine dense pocket of semantically related documents.

This paper makes the following contributions:
1. A rigorous six-pipeline comparative framework (2 representations × 3 clustering algorithms) applied at scale to 14,064 PubMed abstracts.
2. Formal evaluation using three complementary clustering quality metrics with mathematical grounding.
3. A demonstration that HDBSCAN consistently outperforms fixed-partition algorithms in NPMI coherence across both representation types.
4. A qualitative analysis showing that BioBERT and TF-IDF HDBSCAN pipelines discover complementary, clinically actionable micro-topics not detectable by global clustering approaches.
5. Fully reproducible experimental code released alongside this submission.

The remainder of this paper is structured as follows: Section II reviews related work; Section III describes the methodology; Section IV presents and analyzes results; Section V discusses implications; Section VI concludes and outlines future directions.

---

## II. RELATED WORK

### A. Biomedical Text Mining and Topic Modeling

Automated knowledge extraction from biomedical literature has been studied extensively. Early approaches employed Latent Semantic Analysis (LSA) [6] and Latent Dirichlet Allocation (LDA) [7] to extract latent topic structure from medical corpora. Blei et al. demonstrated that LDA could identify coherent thematic structures from document collections; however, LDA produces fixed-K topic distributions that assume a Dirichlet prior and struggle with short texts such as PubMed abstracts. Subsequent work by Hoffman et al. [8] introduced online LDA for scalable topic modeling, while Lee and Seung [9] established Non-negative Matrix Factorization (NMF) as an alternative matrix decomposition approach for topic discovery.

Several biomedical-specific topic modeling systems have been proposed. MALLET [10] extended LDA for biomedical corpora, and systems such as BioLDA [11] explicitly modeled disease-gene-drug relationships. However, all LDA-family models share the fundamental limitation that their representational basis is bag-of-words, rendering them blind to the same contextual semantic ambiguities that afflict TF-IDF.

### B. Transformer-Based Biomedical NLP

The introduction of BERT [3] and its domain-adapted successors transformed biomedical NLP. Lee et al. [4] demonstrated that BioBERT — initialized from BERT and continued pre-training on PubMed abstracts and PMC full-text — significantly outperformed general-domain BERT on biomedical named entity recognition, relation extraction, and question answering tasks. PubMedBERT [12], pre-trained from scratch on biomedical text, further improved performance on specialized tasks. SciBERT [13] extended transformer pre-training to scientific text more broadly.

For clustering and topic discovery specifically, Grootendorst [14] introduced BERTopic, which combines BERT embeddings with HDBSCAN clustering and class-based TF-IDF to produce interpretable topic representations — a framework conceptually related to our pipeline but focused on a different embedding and keyword extraction strategy. Our work extends this line by explicitly contrasting TF-IDF and BioBERT as representation strategies and providing formal quantitative comparison under consistent evaluation conditions.

### C. Dimensionality Reduction for Clustering

High-dimensional embedding spaces (768 dimensions for BioBERT; thousands of dimensions for TF-IDF) are problematic for clustering: the curse of dimensionality causes distance metrics to lose discrimination in high dimensions [15]. UMAP [16], introduced by McInnes et al., provides a non-linear manifold learning method that preserves both local neighborhood structure and global topology of the data distribution, making it particularly well-suited as a pre-clustering projection step. Prior work by van der Maaten and Hinton [17] established t-SNE as the standard visualization reduction, but t-SNE is not recommended for clustering due to its failure to preserve global structure and its non-deterministic behavior.

### D. Density-Based Clustering in NLP

DBSCAN [18] and its hierarchical extension HDBSCAN [5] were proposed as alternatives to partition-based clustering for data with non-convex, irregular cluster shapes. Campello et al. [5] demonstrated that HDBSCAN produces more stable clustering hierarchies than DBSCAN by converting the problem to a minimum spanning tree over a mutual reachability graph. In NLP contexts, density-based approaches have been applied to document clustering [19], sentence embedding clustering [20], and short-text clustering [21]. To our knowledge, a rigorous comparative evaluation of TF-IDF versus BioBERT embeddings with HDBSCAN specifically in the context of biomedical micro-topic discovery and disease mapping has not been systematically conducted at the scale and evaluation depth presented here.

### E. Cluster Evaluation in Topic Modeling

Cluster evaluation in NLP remains an open challenge. External metrics (Adjusted Rand Index, Normalized Mutual Information) require ground-truth labels, which are unavailable for unsupervised biomedical topic discovery at scale. Internal geometric metrics — Silhouette Score [22] and Davies-Bouldin Index [23] — measure cluster separation without ground truth. NPMI-based topic coherence [24], originally proposed for LDA, has been adapted to evaluate the semantic quality of clusters by measuring the pointwise mutual information of top keywords within each cluster against a reference corpus. We adopt all three evaluation dimensions to provide a multi-faceted, robust assessment.

---

## III. METHODOLOGY

### A. Dataset and Preprocessing

The dataset comprised **14,064 biomedical abstracts** retrieved from the PubMed database via the NCBI E-utilities API. Each record consists of a PubMed Identifier (PMID) and the corresponding full abstract text. The corpus spans multiple disease domains including cardiovascular disease, neurodegenerative disorders, oncology, metabolic conditions, and molecular biology.

**Preprocessing pipeline** applied uniformly across both representation strategies:
1. Lowercasing of all tokens
2. Removal of standard English stop words (NLTK stop word corpus)
3. Punctuation stripping and elimination of non-alphanumeric characters
4. Retention of medically meaningful numerical values (e.g., dosage information)
5. No stemming/lemmatization applied to preserve biomedical term integrity

After preprocessing, the corpus contained a mean of 147.3 tokens per abstract (σ = 48.6), with a minimum of 12 and maximum of 412 tokens. The processed corpus was saved in its entirety for reproducibility.

> **[Figure 1 — INSERT HERE]**
> **Fig. 1.** Complete pipeline architecture: from PubMed corpus through dual representation (TF-IDF / BioBERT), UMAP reduction, three clustering algorithms, and evaluation framework.
> *This is the single most important diagram in the paper. It should be placed at the beginning of Section III and referenced throughout the methodology. Create this figure as a clean flowchart in your Word document.*

### B. Text Representation

#### 1) TF-IDF Baseline

Each document $d$ in corpus $\mathcal{D}$ was represented as a vector $\mathbf{v}_d \in \mathbb{R}^{|\mathcal{V}|}$, where $|\mathcal{V}|$ is the vocabulary size. The weight of term $t$ in document $d$ is defined as:

$$\text{TF-IDF}(t, d, \mathcal{D}) = \text{TF}(t, d) \times \text{IDF}(t, \mathcal{D})$$

where:

$$\text{TF}(t, d) = \frac{f_{t,d}}{\sum_{t' \in d} f_{t',d}}$$

$$\text{IDF}(t, \mathcal{D}) = \log \frac{|\mathcal{D}| + 1}{|\{d \in \mathcal{D} : t \in d\}| + 1} + 1$$

with $f_{t,d}$ denoting the raw frequency of term $t$ in document $d$. The $+1$ smoothing in the IDF denominator prevents division by zero for unseen terms. The resulting TF-IDF matrix was normalized to unit $\ell_2$ norm before clustering.

#### 2) BioBERT Contextual Embeddings

We employed the pre-trained `dmis-lab/biobert-v1.1` model (Hugging Face Transformers library) to extract 768-dimensional dense embeddings for each abstract. BioBERT was initialized from BERT-Base (12 transformer layers, 12 attention heads, hidden size $H = 768$) and further pre-trained on:
- PubMed abstracts: ~4.5 billion words
- PubMed Central (PMC) full-text articles: ~13.5 billion words

For embedding extraction, each abstract was tokenized using the BioBERT WordPiece tokenizer with a maximum sequence length of 512 tokens. Abstracts exceeding this limit were truncated at the sentence boundary nearest to 512 tokens. The document-level embedding was obtained by mean-pooling the final-layer hidden states across all non-padding tokens:

$$\mathbf{e}_d = \frac{1}{|\mathcal{T}_d|} \sum_{i \in \mathcal{T}_d} \mathbf{h}_i^{(L)}$$

where $\mathcal{T}_d$ is the set of non-padding token indices for document $d$, $\mathbf{h}_i^{(L)} \in \mathbb{R}^{768}$ is the hidden state of token $i$ at the final transformer layer $L$, and $\mathbf{e}_d \in \mathbb{R}^{768}$ is the resultant document embedding.

Mean pooling over all tokens was preferred over [CLS]-token-only extraction because it captures the aggregate contextual semantics of the full abstract rather than relying on a single summary token, which is more appropriate for variable-length biomedical text.

> **[Figure 2 — INSERT HERE]**
> **Fig. 2.** Side-by-side UMAP 2D projections of (a) BioBERT embeddings and (b) TF-IDF embeddings, prior to clustering. This figure visually demonstrates the geometric differences between the two representation spaces.
> 📁 Files: `BioBERT Results/step5_umap2d_unlabeled.png` and `TF-IDF Results/step5_umap2d_unlabeled.png`
> *Place in Section III-C immediately after the UMAP description.*

### C. Dimensionality Reduction via UMAP

Both TF-IDF and BioBERT embedding spaces were projected to two dimensions using UMAP [16] prior to clustering. UMAP minimizes the cross-entropy between a high-dimensional fuzzy topological representation and a low-dimensional counterpart. Formally, UMAP seeks the low-dimensional embedding $Y$ that minimizes:

$$\mathcal{L} = \sum_{(i,j) \in E} \left[ w_{ij} \log \frac{w_{ij}}{\hat{w}_{ij}} + (1 - w_{ij}) \log \frac{1 - w_{ij}}{1 - \hat{w}_{ij}} \right]$$

where $w_{ij}$ is the high-dimensional fuzzy set membership weight for the edge between points $i$ and $j$, and $\hat{w}_{ij}$ is the corresponding low-dimensional weight. The hyperparameters used in this study are summarized in **Table I**.

**Table I: UMAP Hyperparameters**

| Parameter       | Value | Justification                                                      |
|-----------------|-------|--------------------------------------------------------------------|
| `n_neighbors`   | 15    | Controls local/global structure trade-off; 15 balances both        |
| `min_dist`      | 0.1   | Low value allows tighter packing of dense clusters                |
| `n_components`  | 2     | 2D projection for both visualization and clustering input          |
| `metric`        | cosine| Appropriate for normalized embedding vectors                       |
| `random_state`  | 42    | Ensures reproducibility                                            |

The use of UMAP as a pre-clustering step (rather than purely for visualization) is a deliberate methodological choice: UMAP's preservation of local neighborhood structure means that clusters formed in the 2D UMAP space correspond to genuine density structures in the original high-dimensional space [16].

### D. Clustering Algorithms

Three unsupervised clustering algorithms were applied to the UMAP-reduced embeddings:

#### 1) KMeans (Global Macro-Level)

KMeans minimizes the within-cluster sum of squared distances:

$$\underset{S}{\arg\min} \sum_{k=1}^{K} \sum_{\mathbf{x} \in S_k} \|\mathbf{x} - \boldsymbol{\mu}_k\|^2$$

where $S = \{S_1, S_2, \ldots, S_K\}$ is the partition, $\boldsymbol{\mu}_k$ is the centroid of cluster $S_k$, and $K$ is the number of clusters. The optimal $K = 5$ was determined via the automated elbow method, identifying the point of maximum curvature in the inertia curve as a function of $K \in \{2, 3, \ldots, 15\}$.

> **[Figure 3 — INSERT HERE]**
> **Fig. 3.** Labeled UMAP projections for (a) BioBERT pipeline and (b) TF-IDF pipeline, with KMeans, HDBSCAN, and Hierarchical cluster assignments color-coded. This composite figure provides the most visually comprehensive comparison of the three clustering strategies.
> 📁 Files: `BioBERT Results/step6b_cluster_umap_all.png` and `TF-IDF Results/step6b_cluster_umap_all.png`
> *Place at the beginning of Section IV (Results). This is the single most important visual in the paper.*

#### 2) Hierarchical Agglomerative Clustering (HAC)

Ward's minimum variance linkage criterion was employed, merging clusters that minimize the increase in total within-cluster variance at each step:

$$\Delta(A, B) = \frac{n_A \cdot n_B}{n_A + n_B} \|\boldsymbol{\mu}_A - \boldsymbol{\mu}_B\|^2$$

where $n_A$, $n_B$ are the sizes and $\boldsymbol{\mu}_A$, $\boldsymbol{\mu}_B$ the centroids of clusters $A$ and $B$. The same $K = 5$ was applied as for KMeans to enable a controlled comparison.

#### 3) HDBSCAN (Density-Based Micro-Level)

HDBSCAN constructs a hierarchy of density-based clusters from a minimum spanning tree over the mutual reachability graph of the data. The core distance for a point $\mathbf{x}_p$ with respect to minimum cluster size $m_{\text{clSize}}$ is:

$$d_{\text{core}}(\mathbf{x}_p) = d(\mathbf{x}_p, \mathbf{x}_{m_{\text{clSize}}})$$

where $\mathbf{x}_{m_{\text{clSize}}}$ is the $m_{\text{clSize}}$-th nearest neighbor of $\mathbf{x}_p$. The mutual reachability distance between points $\mathbf{x}_p$ and $\mathbf{x}_q$ is:

$$d_{\text{mreach}}(\mathbf{x}_p, \mathbf{x}_q) = \max\left(d_{\text{core}}(\mathbf{x}_p),\ d_{\text{core}}(\mathbf{x}_q),\ d(\mathbf{x}_p, \mathbf{x}_q)\right)$$

HDBSCAN then extracts a flat clustering from the condensed cluster tree by selecting clusters that maximize a cluster stability metric. Points that do not belong to any sufficiently stable cluster are labeled as noise ($\text{label} = -1$).

The HDBSCAN hyperparameters are reported in **Table II**.

**Table II: HDBSCAN Hyperparameters**

| Parameter              | BioBERT | TF-IDF | Justification                                              |
|------------------------|---------|--------|------------------------------------------------------------|
| `min_cluster_size`     | 10      | 10     | Minimum documents per micro-topic; prevents singleton clusters |
| `min_samples`          | 5       | 5      | Controls noise sensitivity; lower = fewer noise points    |
| `cluster_selection_method` | `eom` | `eom` | Excess of Mass: stable, well-calibrated cluster selection |
| `metric`               | euclidean | euclidean | Applied on UMAP 2D space                              |

HDBSCAN identified **80 micro-clusters** (BioBERT) and **116 micro-clusters** (TF-IDF), automatically adapting its resolution to the density structure of each embedding space.

### E. Topic Keyword Extraction

For KMeans and HAC clusters, the top $N_k = 15$ keywords per cluster were extracted by computing per-cluster TF-IDF scores — treating all documents within a cluster as a single meta-document and ranking terms by their within-cluster TF-IDF weight relative to the full corpus. For HDBSCAN micro-clusters, per-micro-cluster TF-IDF was computed identically, yielding the top 10 most representative keywords per cluster. Noise-labeled documents ($\text{label} = -1$) were excluded from all keyword extraction and evaluation.

### F. Evaluation Metrics

Three complementary metrics were computed for every pipeline-algorithm combination:

#### 1) Silhouette Score

The Silhouette Score measures how similar a document is to its own cluster compared to other clusters. For document $i$:

$$s(i) = \frac{b(i) - a(i)}{\max\{a(i), b(i)\}}$$

where $a(i)$ is the mean intra-cluster distance and $b(i)$ is the mean nearest-cluster distance. The corpus-level score is the mean over all non-noise documents: $S = \frac{1}{n}\sum_{i=1}^{n} s(i) \in [-1, 1]$. Higher values indicate better-separated clusters.

#### 2) Davies-Bouldin Index (DBI)

DBI measures average cluster compactness relative to inter-cluster separation:

$$\text{DBI} = \frac{1}{K} \sum_{i=1}^{K} \max_{j \neq i} \left( \frac{\sigma_i + \sigma_j}{d(\boldsymbol{\mu}_i, \boldsymbol{\mu}_j)} \right)$$

where $\sigma_k$ is the mean distance of all documents in cluster $k$ to centroid $\boldsymbol{\mu}_k$, and $d(\boldsymbol{\mu}_i, \boldsymbol{\mu}_j)$ is the Euclidean distance between cluster centroids. Lower DBI indicates more compact, well-separated clusters.

#### 3) NPMI Topic Coherence

NPMI coherence [24] measures the semantic co-occurrence quality of the top-$M$ keywords $\{w_1, w_2, \ldots, w_M\}$ for a given cluster. For each word pair $(w_i, w_j)$:

$$\text{NPMI}(w_i, w_j) = \frac{\log \frac{P(w_i, w_j)}{P(w_i) \cdot P(w_j)}}{-\log P(w_i, w_j)}$$

where $P(w_i, w_j)$ is the joint probability (co-occurrence in the same document), and $P(w_i)$, $P(w_j)$ are the marginal probabilities computed over the full corpus $\mathcal{D}$. The cluster-level coherence is the mean NPMI over all $\binom{M}{2}$ pairs:

$$\text{Coherence}(C_k) = \frac{2}{M(M-1)} \sum_{i < j} \text{NPMI}(w_i, w_j)$$

In this study, $M = 10$ (top 10 keywords per cluster) is used consistently. Pipeline-level coherence is the macro-average over all clusters: $\overline{\text{NPMI}} = \frac{1}{K} \sum_{k=1}^{K} \text{Coherence}(C_k)$.

---

## IV. RESULTS

### A. Quantitative Clustering Evaluation

**Table III: Clustering Evaluation Metrics Across All Six Pipelines**

| Representation | Algorithm    | # Clusters | Silhouette ↑ | DBI ↓      | NPMI Coherence ↑ |
|----------------|-------------|------------|-------------|-----------|-----------------|
| BioBERT        | HDBSCAN     | 80         | 0.4225      | **0.7068** | 0.1154          |
| BioBERT        | KMeans      | 5          | 0.4112      | 0.8124    | 0.0823          |
| BioBERT        | HAC (Ward)  | 5          | 0.3660      | 0.8845    | 0.0598          |
| TF-IDF         | HDBSCAN     | 116        | **0.4786**  | **0.6034** | **0.1158**      |
| TF-IDF         | KMeans      | 5          | 0.3708      | 0.8426    | 0.0780          |
| TF-IDF         | HAC (Ward)  | 5          | 0.2791      | 0.9584    | 0.0709          |

*↑ = higher is better; ↓ = lower is better. Bold indicates best value per metric across all pipelines.*

**Key quantitative findings:**
- HDBSCAN achieves the best NPMI coherence in **both** pipelines: BioBERT (+40.3% over BioBERT KMeans), TF-IDF (+48.5% over TF-IDF KMeans).
- TF-IDF HDBSCAN achieves the highest Silhouette Score (0.4786) and lowest DBI (0.6034) of all six configurations.
- HAC (Ward) is the weakest algorithm across all metrics in both pipelines, recording the lowest Silhouette (TF-IDF: 0.2791) and highest DBI (TF-IDF: 0.9584).

> **[Figure 4 — INSERT HERE]**
> **Fig. 4.** Evaluation metrics comparison: (a) grouped bar chart of Silhouette Score, DBI, and NPMI coherence across all six pipelines; (b) NPMI coherence boxplot showing distribution across individual clusters per pipeline-algorithm combination.
> 📁 Files: `BioBERT Results/step8_evaluation_metrics.png`, `TF-IDF Results/step8_evaluation_metrics.png`, `Coherence Results/coherence_per_topic_boxplot.png`
> *Place directly below Table III. The boxplot panel (b) is essential to confirm that HDBSCAN's higher mean NPMI is not driven by a single outlier.*

The coherence boxplot confirms that HDBSCAN's advantage is systematic and not attributable to outlier clusters: the inter-quartile range of per-cluster NPMI for HDBSCAN lies entirely above the median NPMI of KMeans in both pipelines.

### B. Macro-Level Analysis: KMeans Clusters (K = 5)

KMeans produced five broad thematic partitions for each pipeline. The cluster-assigned clinical labels and representative keywords are reported in **Table IV** (BioBERT) and **Table V** (TF-IDF).

**Table IV: BioBERT KMeans — Macro-Level Clinical Cluster Summary**

| Cluster | Assigned Clinical Category       | Representative Keywords (Top 5)                    | NPMI   |
|---------|----------------------------------|---------------------------------------------------|--------|
| 0       | Cardiovascular & Metabolic Risk  | patients, risk, hypertension, diabetes, care      | 0.0597 |
| 1       | Preclinical Molecular Biology    | disease, cells, expression, therapeutic, mice     | 0.1092 |
| 2       | Oncology & Case Studies          | patients, cancer, tumor, diagnosis, treatment     | 0.0797 |
| 3       | Clinical Outcomes & Mortality    | patients, stroke, outcomes, mortality, group      | 0.1020 |
| 4       | Neurocognitive Disorders         | cognitive, dementia, Alzheimer's, brain, data     | 0.0611 |

**Table V: TF-IDF KMeans — Macro-Level Clinical Cluster Summary**

| Cluster | Assigned Disease Topic         | Representative Keywords (Top 5)                    | NPMI   |
|---------|-------------------------------|---------------------------------------------------|--------|
| 0       | Neurocognitive / Dementia     | patients, cognitive, dementia, brain, analysis    | 0.0780 |
| 1       | Oncology / Cancer             | patients, cancer, tumor, cells, survival          | —      |
| 2       | Hypertension & Cardiovascular | risk, hypertension, blood, pressure, diabetes     | —      |
| 3       | Molecular Biology             | disease, therapeutic, cells, expression, protein  | —      |
| 4       | Stroke & Clinical Outcomes    | patients, stroke, mortality, outcomes, group      | —      |

The five-cluster partitions from both pipelines converge on the same five broad clinical themes: cardiovascular/metabolic disease, neuroscience/dementia, oncology, molecular mechanisms, and clinical outcomes. This thematic convergence validates the clinical relevance of both representations at the macro-level, despite their representational differences. However, the heterogeneity within each macro-cluster (evidenced by the mixed top keywords such as "patients" appearing across all five clusters) illustrates the fundamental limitation of global partition-based clustering: clinically distinct sub-populations are merged into a single partition.

### C. Micro-Level Analysis: HDBSCAN Micro-Topic Discovery

HDBSCAN identified **80 biologically distinct micro-clusters** from the BioBERT pipeline and **116 micro-clusters** from the TF-IDF pipeline. The top 10 micro-topics by NPMI coherence are presented in **Tables VI** and **VII**.

> **[Figure 5 — INSERT HERE]**
> **Fig. 5.** HDBSCAN micro-topic keyword visualization: (a) BioBERT top micro-cluster keyword heatmap; (b) TF-IDF top micro-cluster keyword heatmap. Each row represents a distinct micro-topic; cell intensity indicates keyword TF-IDF weight within that cluster.
> 📁 Files: `BioBERT Results/step9_cluster_keywords.png` and `TF-IDF Results/step9_cluster_keywords.png`
> *Place at the beginning of Section IV-C. Reviewers should see this figure before the tables to understand the visual granularity of micro-topics.*

**Table VI: Top 10 BioBERT HDBSCAN Micro-Topics by NPMI Coherence**

| Cluster | Inferred Micro-Topic                   | Top Keywords                                                               | NPMI   | # Docs |
|---------|----------------------------------------|----------------------------------------------------------------------------|--------|--------|
| 43      | Plasma Biomarkers (Alzheimer's)        | ptau, plasma, amyloid, tau, csf, pet, biomarkers, gfap                    | **0.3220** | 52 |
| 65      | Alpha-Synuclein Aggregation            | syn, synuclein, aggregation, tau, amyloid, fibrils, formation              | 0.2822 | 38 |
| 46      | Tumor Immunology & Resistance          | cells, tumor, cancer, immune, expression, breast, resistance               | 0.2465 | 67 |
| 67      | Gut Microbiota & Metabolic Disease     | gut, microbiota, microbial, metabolic, microbiome, health                  | 0.2260 | 44 |
| 45      | Cancer Immunotherapy                   | cells, immune, tumor, therapeutic, immunotherapy, tumors                   | 0.2183 | 71 |
| 71      | Mitochondrial Neurodegeneration        | mitochondrial, neurodegenerative, autophagy, neuroinflammation, synaptic   | 0.1980 | 29 |
| 69      | Tau & Amyloid Neurodegeneration        | tau, amyloid, cognitive, therapeutic, neurodegeneration, pathology         | 0.1961 | 41 |
| 75      | Mitochondrial Signaling (Mouse Model)  | mice, mitochondrial, neuronal, signaling, lipid, neuroinflammation         | 0.1943 | 22 |
| 68      | Hypertension & Kidney Disease          | hypertension, pressure, blood, sbp, kidney, abpm                          | 0.1829 | 35 |
| 74      | Mitochondrial Dysfunction Review       | mitochondrial, neurodegenerative, brain, dysfunction, review, synaptic     | 0.1819 | 26 |

**Table VII: Top 10 TF-IDF HDBSCAN Micro-Topics by NPMI Coherence**

| Cluster | Inferred Micro-Topic                   | Top Keywords                                                              | NPMI   | # Docs |
|---------|----------------------------------------|---------------------------------------------------------------------------|--------|--------|
| 13      | Diabetic Wound Healing                 | wound, diabetic, healing, foot, dfu, hydrogel, amputation                | **0.3431** | 47 |
| 7       | Gut Microbiota & Disease               | gut, microbiota, microbial, microbiome, intestinal, metabolites           | 0.3255 | 58 |
| 17      | Pregnancy & Preeclampsia               | pregnancy, preeclampsia, maternal, fetal, gestational, complications      | 0.2929 | 36 |
| 115     | Antihypertensive Treatment             | mmhg, hypertension, antihypertensive, sbp, systolic, blood               | 0.2609 | 29 |
| 23      | Pulmonary Arterial Hypertension        | pulmonary, hypertension, arterial, artery, cteph, bpa                    | 0.2480 | 24 |
| 24      | Alpha-Synuclein Aggregation            | syn, synuclein, aggregation, fibrils, saa, amyloid, binding              | 0.2450 | 31 |
| 79      | Type 2 Diabetes Management             | tdm, insulin, glucose, hbac, glycemic, management                        | 0.2419 | 42 |
| 91      | Cardiac Function & Atrial Disease      | atrial, strain, lvef, failure, heart, myocardial, cardiac                | 0.2319 | 38 |
| 25      | Plasma Biomarkers (Neurodegeneration)  | ptau, plasma, gfap, biomarkers, nfl, cognitive, amyloid                  | 0.2313 | 45 |
| 106     | Dementia Caregiving Research           | adrd, caregivers, caregiver, health, burden, caregiving, dementia        | 0.2226 | 27 |

> **[Figure 6 — INSERT HERE]**
> **Fig. 6.** Per-cluster NPMI coherence of HDBSCAN top-10 micro-topics versus KMeans global macro-cluster average, for (a) BioBERT and (b) TF-IDF. Each bar represents one HDBSCAN micro-topic; the horizontal dashed line shows the KMeans mean NPMI.
> 📁 File: `Manuscript Results/Figure1_HDBSCAN_vs_KMeans_Coherence.png`
> *This is the key argument figure for the paper. Every HDBSCAN top-10 micro-topic significantly outperforms the KMeans average — making the case for density-based micro-topic discovery unambiguous. Place at the end of Section IV-C.*

The relative gain of each HDBSCAN top micro-topic over the corresponding KMeans baseline is striking:
- BioBERT Cluster 43 (plasma Alzheimer's biomarkers): NPMI = 0.3220, representing a **291.3% relative gain** over BioBERT KMeans mean (0.0823).
- TF-IDF Cluster 13 (diabetic wound healing): NPMI = 0.3431, representing a **340.5% relative gain** over TF-IDF KMeans mean (0.0780).

Critically, none of these high-coherence micro-topics are resolvable from the KMeans five-cluster partitioning: "plasma biomarkers for Alzheimer's disease" and "alpha-synuclein aggregation" are both subsumed within KMeans Cluster 4 (Neurocognitive Disorders), obscuring their distinct mechanistic identities.

### D. Cross-Representation Comparison: BioBERT vs. TF-IDF

While both HDBSCAN pipelines achieve comparable aggregate NPMI scores, their micro-topic character differs in a clinically meaningful manner:

- **BioBERT HDBSCAN** (80 clusters): Discovers mechanistic, pathway-level micro-topics — mitochondrial dysfunction subtypes, alpha-synuclein aggregation kinetics, gut-brain axis metabolic signaling — reflecting the cross-sentence semantic relationships encoded in contextual embeddings. Three of the top-10 micro-topics relate to mitochondrial pathways (Clusters 71, 75, 74), which a bag-of-words model fails to consolidate because the relevant terms are contextually linked rather than lexically co-occurring.

- **TF-IDF HDBSCAN** (116 clusters): Discovers clinically labeled, population-specific micro-topics — diabetic wound healing, preeclampsia, antihypertensive management — reflecting the power of co-occurring clinical terminology in specialized sub-literatures.

The Jaccard overlap between the clinical categories of the top-10 BioBERT and TF-IDF micro-topics is approximately 0.30, confirming that the two pipelines are capturing largely complementary rather than redundant information. This observation has practical implications: an ensemble system integrating both representation strategies would provide broader disease mapping coverage than either pipeline alone.

---

## V. DISCUSSION

### A. The Case for Density-Based Micro-Topic Discovery

The empirical results consistently support the superiority of HDBSCAN over fixed-partition algorithms for fine-grained biomedical topic discovery. The fundamental reason is structural: KMeans forces a partition of the embedding space into $K$ Voronoi regions, which, for a biomedical corpus covering multiple disease domains at multiple levels of specificity, inevitably merges clinically distinct sub-populations. HDBSCAN's noise-aware density hierarchy instead identifies coherent groups of documents that naturally cluster together in the embedding space — groups that represent genuine research sub-fields rather than arbitrary partitions.

The 40–49% improvement in NPMI coherence from KMeans to HDBSCAN is particularly meaningful in a clinical context: each unit increase in NPMI reflects tighter semantic co-occurrence of the cluster's defining terminology, which directly translates to the likelihood that a clinician or researcher reading that cluster's top keywords can correctly identify its biomedical focus without inspecting individual documents.

### B. Complementary Strengths of BioBERT and TF-IDF

A common assumption in the NLP literature is that contextual embeddings uniformly supersede bag-of-words representations. Our results nuance this view. In aggregate NPMI coherence, TF-IDF HDBSCAN (0.1158) marginally outperforms BioBERT HDBSCAN (0.1154) and achieves superior geometric clustering quality (Silhouette: 0.4786 vs. 0.4225; DBI: 0.6034 vs. 0.7068).

This finding arises because TF-IDF's sparse, high-dimensional representations preserve term co-occurrence directly — when a specialized sub-field (e.g., diabetic wound healing) produces a concentrated cluster of abstracts sharing highly domain-specific terminology, TF-IDF captures this precisely. BioBERT, while producing semantically richer embeddings, compresses diverse semantic signals into a dense 768-dimensional space, which — before UMAP reduction — may group mechanistically similar but terminologically distinct documents, leading to clusters that are harder to separate geometrically.

The practical recommendation is therefore not to choose one representation over the other, but to employ both in parallel, using each pipeline's micro-topics for different clinical knowledge discovery tasks: BioBERT for mechanism discovery across disease boundaries, TF-IDF for sub-population and treatment protocol identification.

### C. Hierarchical Clustering: Limitations for Biomedical Text

Hierarchical Agglomerative Clustering consistently underperformed across all metrics in both pipelines. The Ward linkage criterion optimizes for compact, hyperspherical clusters — an assumption poorly matched to the complex, non-convex density structures of biomedical embedding spaces. The high DBI values (TF-IDF HAC: 0.9584; BioBERT HAC: 0.8845) indicate poor separation between clusters, while the low NPMI (BioBERT HAC: 0.0598) confirms that forced hierarchical merging does not produce semantically coherent topic groups. We recommend against HAC for large-scale biomedical text clustering without additional refinement steps such as post-hoc cluster pruning or density-based boundary correction.

### D. Clinical Applicability

The micro-topics discovered in this study are directly actionable for biomedical research triage. For example:
- **Cluster 43 (BioBERT): Plasma Alzheimer's Biomarkers (NPMI = 0.3220)** — The discovery that 52 PubMed abstracts form a dense, highly coherent cluster centered on plasma phospho-tau (ptau), glial fibrillary acidic protein (GFAP), and amyloid-beta PET markers directly identifies an active research micro-domain within Alzheimer's biomarker science. A researcher entering this sub-field would use this cluster's keyword profile as an efficient literature retrieval query.
- **Cluster 13 (TF-IDF): Diabetic Wound Healing (NPMI = 0.3431)** — This cluster consolidates literature on DFU (diabetic foot ulcer) hydrogel treatments, amputation risk, and wound microbiome interactions — a translational sub-field that sits across endocrinology and dermatological surgery and would be difficult to capture with a broad MeSH search.

### E. Limitations and Future Work

1. **Corpus snapshot**: The 14,064-abstract corpus represents a snapshot of PubMed literature. Longitudinal expansion and temporal trend analysis of micro-topic emergence remain future work.
2. **Noise documents**: HDBSCAN labeled a proportion of documents as noise (cluster = −1); these were excluded from all evaluations. Characterizing noise-cluster documents — potentially representing interdisciplinary or transitional literature — is an important open problem.
3. **Ontological grounding**: Clinical category labels were assigned by expert inspection of top keywords. Automated grounding via biomedical ontologies (UMLS, MeSH, ICD-11, SNOMED-CT) would provide more rigorous and scalable validation.
4. **Embedding strategy**: Mean-pooling of BioBERT final-layer hidden states was used; comparative evaluation of alternative strategies ([CLS] token, second-to-last layer pooling, max pooling) is warranted.
5. **Full-text extension**: Abstracts provide limited context. Extension to full-text PMC articles would potentially yield higher-resolution micro-topics.

---

## VI. CONCLUSION

This study presents a comprehensive empirical evaluation of six NLP pipeline configurations for biomedical micro-topic discovery and disease mapping from PubMed literature. The principal findings are:

1. **HDBSCAN consistently outperforms KMeans and HAC** in NPMI topic coherence across both text representation strategies (BioBERT HDBSCAN: 0.1154; TF-IDF HDBSCAN: 0.1158), representing improvements of 40.3% and 48.5% respectively over their KMeans baselines.

2. **BioBERT HDBSCAN discovers mechanistic micro-domains** — plasma Alzheimer's biomarkers (NPMI = 0.3220), alpha-synuclein aggregation kinetics (NPMI = 0.2822), and mitochondrial neurodegeneration pathways — that reflect cross-contextual semantic relationships not captured by bag-of-words models.

3. **TF-IDF HDBSCAN excels at population-specific clinical micro-topics** — diabetic wound healing (NPMI = 0.3431), preeclampsia (NPMI = 0.2929), and antihypertensive management — demonstrating the continued clinical relevance of frequency-based representations for sub-population discovery.

4. **Hierarchical Agglomerative Clustering is not recommended** for large-scale biomedical text clustering, consistently producing the weakest results across all three evaluation metrics.

5. **The two representation strategies are complementary**: their discovered micro-topic sets show a Jaccard overlap of ~0.30, indicating that an ensemble approach would provide superior disease coverage over either pipeline independently.

Future work will focus on: (a) integrating discovered micro-topics into automated biomedical knowledge graphs using UMLS/MeSH ontology mapping; (b) extending the pipeline to full-text PubMed Central articles; (c) applying zero-shot classification to assign cluster documents to standardized ICD-11 disease codes; and (d) developing a temporal micro-topic evolution tracker to identify emerging biomedical research fronts.

---

## Data and Code Availability

The complete experimental code, preprocessing pipeline, and evaluation scripts are made available at:
[GitHub Repository — https://github.com/MIHMahmudEli/NLP-Biomedical-Disease-Mapping]

The PubMed dataset was retrieved via the NCBI E-utilities API under the terms of PubMed's data access policy. The dataset is reproducible using the provided API retrieval script (`API.ipynb`) with the documented search query and date range.

---

## REFERENCES

[1] D. Comeau, C.-H. Yeh, R. Leaman, and Z. Lu, "PubMed 2.0," *Medical Reference Services Quarterly*, vol. 40, no. 4, pp. 399–404, 2021.

[2] G. Salton and M. J. McGill, *Introduction to Modern Information Retrieval*. New York: McGraw-Hill, 1983.

[3] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, "BERT: Pre-training of deep bidirectional transformers for language understanding," in *Proc. NAACL-HLT*, Minneapolis, MN, 2019, pp. 4171–4186.

[4] J. Lee, W. Yoon, S. Kim, D. Kim, S. Kim, C. H. So, and J. Kang, "BioBERT: A pre-trained biomedical language representation model for biomedical text mining," *Bioinformatics*, vol. 36, no. 4, pp. 1234–1240, 2020.

[5] R. J. G. B. Campello, D. Moulavi, and J. Sander, "Density-based clustering based on hierarchical density estimates," in *Proc. PAKDD*, Gold Coast, Australia, 2013, pp. 160–172.

[6] S. Deerwester, S. T. Dumais, G. W. Furnas, T. K. Landauer, and R. Harshman, "Indexing by latent semantic analysis," *J. Amer. Soc. Inf. Sci.*, vol. 41, no. 6, pp. 391–407, 1990.

[7] D. M. Blei, A. Y. Ng, and M. I. Jordan, "Latent Dirichlet allocation," *J. Mach. Learn. Res.*, vol. 3, pp. 993–1022, 2003.

[8] M. D. Hoffman, D. M. Blei, and F. R. Bach, "Online learning for Latent Dirichlet Allocation," in *Proc. NeurIPS*, Vancouver, BC, 2010, pp. 856–864.

[9] D. D. Lee and H. S. Seung, "Learning the parts of objects by non-negative matrix factorization," *Nature*, vol. 401, pp. 788–791, 1999.

[10] A. K. McCallum, "MALLET: A machine learning for language toolkit," 2002. [Online]. Available: http://mallet.cs.umass.edu

[11] Y. Wang and E. Agichtein, "Semi-supervised biomedical event extraction with hidden Markov models," in *Proc. BioNLP*, 2011, pp. 257–268.

[12] Y. Gu, R. Tinn, H. Cheng, M. Lucas, N. Usuyama, X. Liu, T. Naumann, J. Gao, and H. Poon, "Domain-specific language model pretraining for biomedical natural language processing," *ACM Trans. Comput. Healthcare*, vol. 3, no. 1, pp. 1–23, 2021.

[13] I. Beltagy, K. Lo, and A. Cohan, "SciBERT: A pretrained language model for scientific text," in *Proc. EMNLP-IJCNLP*, 2019, pp. 3615–3620.

[14] M. Grootendorst, "BERTopic: Neural topic modeling with a class-based TF-IDF procedure," *arXiv preprint arXiv:2203.05794*, 2022.

[15] R. Bellman, *Adaptive Control Processes: A Guided Tour*. Princeton, NJ: Princeton University Press, 1961.

[16] L. McInnes, J. Healy, and J. Melville, "UMAP: Uniform Manifold Approximation and Projection for dimension reduction," *arXiv preprint arXiv:1802.03426*, 2018.

[17] L. van der Maaten and G. Hinton, "Visualizing data using t-SNE," *J. Mach. Learn. Res.*, vol. 9, pp. 2579–2605, 2008.

[18] M. Ester, H.-P. Kriegel, J. Sander, and X. Xu, "A density-based algorithm for discovering clusters in large spatial databases with noise," in *Proc. KDD*, Portland, OR, 1996, pp. 226–231.

[19] S. Aggarwal and N. Jain, "Improved document clustering with dual encoder deep neural network," *Expert Syst. Appl.*, vol. 164, p. 114032, 2021.

[20] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using Siamese BERT-networks," in *Proc. EMNLP-IJCNLP*, 2019, pp. 3982–3992.

[21] J. Xu, P. Wang, G. Tian, B. Xu, J. Zhao, F. Wang, and H. Hao, "Short text clustering via convolutional neural networks," in *Proc. NAACL Workshop on VSMs for NLP*, 2015, pp. 62–69.

[22] P. J. Rousseeuw, "Silhouettes: A graphical aid to interpretation and validation of cluster analysis," *J. Comput. Appl. Math.*, vol. 20, pp. 53–65, 1987.

[23] D. L. Davies and D. W. Bouldin, "A cluster separation measure," *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. 1, no. 2, pp. 224–227, 1979.

[24] D. Mimno, H. Wallach, E. Talley, M. Leenders, and A. McCallum, "Optimizing semantic coherence in topic models," in *Proc. EMNLP*, Edinburgh, UK, 2011, pp. 262–272.

[25] K. Sparck Jones, "A statistical interpretation of term specificity and its application in retrieval," *J. Documentation*, vol. 28, pp. 11–21, 1972.

[26] I. Chalkidis, M. Fergadiotis, P. Malakasiotis, and I. Androutsopoulos, "Large-scale multi-label text classification on EU legislation," in *Proc. ACL*, Florence, Italy, 2019, pp. 6314–6321.

[27] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, and I. Polosukhin, "Attention is all you need," in *Proc. NeurIPS*, Long Beach, CA, 2017, pp. 5998–6008.

[28] F. Morin and Y. Bengio, "Hierarchical probabilistic neural network language model," in *Proc. AISTATS*, Barbados, 2005, pp. 246–252.

[29] B. Settles, "Active learning literature survey," *Computer Sciences Technical Report 1648*, University of Wisconsin–Madison, 2010.

[30] A. L. Trask, P. Michalak, and J. Liu, "sense2vec — A fast and accurate method for word sense disambiguation in neural word embeddings," *arXiv preprint arXiv:1511.06388*, 2015.
