# Unsupervised Micro-Topic Discovery and Disease Mapping from PubMed Abstracts: A Comparative Evaluation of BioBERT and TF-IDF Representations with K-Means, HDBSCAN, and Hierarchical Clustering

**Authors**: [Author Name 1]¹, [Author Name 2]¹
**Affiliation**: ¹[Department, Institution, City, Country]
**Corresponding Author**: [email@institution.edu]
**Submitted to**: [IEEE Q2 Journal — e.g., *IEEE Journal of Biomedical and Health Informatics* / *IEEE/ACM Transactions on Computational Biology and Bioinformatics*]
**Date**: June 2026

---

## Abstract

The accelerating volume of biomedical literature indexed in PubMed has outpaced the capacity of manual literature synthesis, creating an urgent need for automated, label-free methods that can surface the latent thematic structure of disease research. This paper presents a systematic comparative study of two text-representation strategies — Term Frequency–Inverse Document Frequency (TF-IDF) and BioBERT contextual embeddings — combined with three unsupervised clustering algorithms — K-Means, Hierarchical Agglomerative Clustering (HAC, Ward linkage), and HDBSCAN — for micro-topic discovery and disease mapping over a corpus of 14,064 PubMed abstracts spanning eight disease domains. Both representations are projected to two dimensions via UMAP, clustered, and quantitatively evaluated using three complementary metrics: Silhouette Score, Davies–Bouldin Index (DBI), and Normalized Pointwise Mutual Information (NPMI) topic coherence. Results show that density-based HDBSCAN consistently outperforms fixed-partition algorithms in NPMI coherence in both representation pipelines, achieving 0.1154 (BioBERT) and 0.1158 (TF-IDF) — corresponding to 40.3% and 48.5% relative improvements over their respective K-Means baselines. Crucially, the two representation strategies are shown to be *complementary rather than competing*: BioBERT HDBSCAN surfaces mechanism-level micro-topics such as plasma p-tau biomarkers for Alzheimer's disease (NPMI = 0.3220) and alpha-synuclein aggregation (NPMI = 0.2822), whereas TF-IDF HDBSCAN resolves population-specific clinical sub-domains such as diabetic wound healing (NPMI = 0.3431) and preeclampsia (NPMI = 0.2929). These findings establish a reproducible, scalable framework for unsupervised, label-free knowledge mapping from biomedical literature and offer practical guidance for selecting representation–clustering combinations in clinical text mining pipelines.

**Index Terms**: BioBERT, biomedical text mining, disease mapping, HDBSCAN, K-Means, hierarchical clustering, NPMI coherence, PubMed, topic discovery, UMAP, unsupervised learning.

---

## I. Introduction

The PubMed bibliographic database contains more than 36 million citations and grows by over one million records each year [1]. Across individual disease areas, the growth rate is even more striking: publications on neoplasms, for example, increased at a compound annual rate of 42.41% through 2021 [13]. Reading, much less synthesizing, this volume of literature is no longer feasible for any individual clinician or research team. Automated computational pipelines that can extract, group, and visually organize the latent disease-related knowledge embedded in millions of abstracts are therefore not merely convenient — they constitute essential research infrastructure for translational medicine.

Classical approaches to biomedical text mining have relied on bag-of-words representations such as Term Frequency–Inverse Document Frequency (TF-IDF), in which each document is encoded as a high-dimensional sparse vector of term-frequency statistics [2]. While computationally efficient and easy to interpret, TF-IDF is fundamentally context-free: the term *pressure* in the context of hypertension and the same term in the context of pulmonary arterial disease receive identical numerical encodings. In a domain where contextual meaning determines clinical relevance, this semantic blindness is a critical limitation.

The introduction of transformer-based language models [27] — particularly the domain-adapted variant BioBERT [1], pre-trained on PubMed abstracts and PubMed Central full-text articles — has substantially improved the representational depth available to biomedical NLP. BioBERT generates 768-dimensional contextual embeddings that capture relational dependencies among medical concepts, moving beyond surface co-occurrence. However, powerful embeddings alone do not guarantee high-quality topic discovery. The clustering algorithm used to organize the embedding space is equally consequential. Partition-based algorithms such as K-Means require the number of clusters to be specified in advance and force every document — including off-topic, transitional, or noisy abstracts — into one of the predefined clusters. This forced global assignment can dilute intra-cluster coherence. HDBSCAN (Hierarchical Density-Based Spatial Clustering of Applications with Noise) [5], in contrast, infers cluster count directly from the local density topology of the embedding space and explicitly labels low-density documents as noise, so each resulting cluster represents a genuine dense region of semantically related documents.

In this paper, we ask three questions:

1. *How do TF-IDF and BioBERT representations differ in the granularity and semantic character of the micro-topics they reveal?*
2. *Does density-based clustering (HDBSCAN) systematically outperform fixed-partition algorithms in topic coherence across both representation strategies?*
3. *Are the two representation strategies complementary — i.e., does each surface clinically distinct micro-topics that the other does not?*

To answer these questions, we construct a six-pipeline comparative framework (2 representations × 3 clustering algorithms) over a 14,064-abstract PubMed corpus spanning diabetes mellitus, cancer, cardiovascular disease, neurological disorders, stroke, hypertension, Alzheimer's disease, and Parkinson's disease. Each pipeline is evaluated by three complementary metrics, and a subset of highly coherent micro-topics is examined qualitatively for clinical interpretability.

The contributions of this work are fivefold:

1. A **rigorous six-pipeline comparative framework** (2 representations × 3 clustering algorithms) applied at scale (14,064 abstracts) to the problem of disease-specific knowledge mapping.
2. **Formal evaluation** using three complementary metrics — Silhouette Score, Davies–Bouldin Index, and NPMI topic coherence — that together capture geometric, separation, and semantic quality of the discovered clusters.
3. **Empirical demonstration** that HDBSCAN consistently outperforms K-Means and HAC in NPMI coherence across both representation types, with gains exceeding 40% relative improvement over K-Means baselines.
4. **Qualitative evidence** that BioBERT and TF-IDF HDBSCAN pipelines discover complementary, clinically actionable micro-topics: BioBERT excels at mechanism-level pathway discovery, while TF-IDF excels at population- and treatment-specific sub-domain identification.
5. A **fully reproducible experimental pipeline** (code, hyperparameters, and seed values) released with the manuscript, with applications to literature triage, hypothesis generation, and automated disease taxonomy construction.

The remainder of the paper is organized as follows. Section II reviews related work across four intersecting research areas. Section III describes the dataset. Section IV details the methodology. Section V presents the experimental setup. Section VI reports quantitative and qualitative results. Section VII discusses the implications, limitations, and broader impact. Section VIII concludes and outlines future directions.

---

## II. Related Work

The volume of biomedical publications indexed in PubMed continues to grow at an accelerating rate. PubMed housed over 29 million indexed articles by 2019 [1], and disease-specific fields show even steeper trajectories, with neoplasm-related publications growing at 42.41% annually through 2021 [13]. Manual literature synthesis at this scale is no longer realistic. Although biomedical abstracts encode genuine scientific knowledge, extracting it in an organized, computable form requires tools that go beyond keyword search. Prior research has approached this challenge from four principal directions: (A) biomedical-domain language models, (B) literature mining and disease knowledge discovery, (C) unsupervised clustering and topic modeling, and (D) embedding visualization. Each has produced meaningful results in isolation, but — to the best of our knowledge — these four directions have rarely been integrated into a single, disease-specific knowledge-mapping pipeline. The remainder of this section reviews each direction and identifies the gap that the present study addresses.

### A. Biomedical Language Models for Biomedical NLP

Biomedical text differs fundamentally from general-domain text. The vocabulary is highly specialized, terms carry context-dependent meaning, and the same concept may be expressed in dozens of surface forms across papers. Early biomedical NLP systems relied on Conditional Random Fields (CRF) and Support Vector Machines (SVM), both of which depended on hand-crafted features and degraded rapidly when terms were rare or ambiguous [2]. BiLSTM-CRF networks improved sequence labeling, but capturing the full contextual meaning of a biomedical sentence remained beyond the reach of these architectures [2]. BERT [27] brought a stronger foundation through self-attention over full sequences, yet it was pre-trained only on Wikipedia and BooksCorpus — general text. The domain mismatch between general pre-training data and biomedical target text had a measurable cost on downstream performance.

Lee *et al.* [1] addressed this directly by continuing BERT pre-training on PubMed abstracts and PMC full-text articles, producing BioBERT. Compared to general BERT, BioBERT gained 0.62% F1 on named entity recognition, 2.80% F1 on relation extraction, and 12.24% MRR on question answering, demonstrating that a model understands the text it was trained on, and that biomedical text benefits from biomedical-domain pre-training. Peng *et al.* [3] confirmed this conclusion across a wider task set through the BLUE benchmark, which evaluated models on ten biomedical and clinical NLP corpora: models pre-trained on PubMed and MIMIC-III consistently ranked highest, with the largest gains observed on clinical text. Both studies point to the same conclusion — domain mismatch between pre-training data and target text is not a minor issue but carries a real cost on downstream performance.

Beyond *what* a model is trained on, *how* it is trained also matters. Peng *et al.* [4] applied multi-task learning across several biomedical NLP objectives and reported gains of 2.0% and 1.3% in biomedical and clinical settings over single-task baselines, suggesting that training across related tasks together produces more generalizable representations than single-task training. Alrowili and Vijay-Shanker [5] showed through the BioM-Transformers family that careful design choices — model size, training objective, and corpus selection — can reach state-of-the-art results without increasing computational cost. Together, these studies show that embedding quality depends on how a model is built and trained, not just on the volume of data it sees.

Comparative benchmarking has reinforced the centrality of domain adaptation. Vithanage *et al.* [6] evaluated 18 contextual embedding models, including ELMo, BERT, BioBERT, BlueBERT, Clinical BioBERT, and GPT-3, across classification, NER, and question answering tasks drawn from PubMed and clinical EHR data. BioBERT ranked highest on general biomedical text across all task types, making it the most empirically supported choice for embedding PubMed abstracts. Kumar and Basu [2] extended BioBERT with AdaBioBERT, adding an adaptive loss function to improve recognition of rare and contextually sensitive biomedical terms that standard NER models tend to misclassify. Sharaf and Anoop [7] examined the deployment of BioBERT in real clinical systems and observed performance improvements in decision support and information retrieval, alongside practical barriers such as patient-data privacy, training-corpus bias, and the cost of domain-specific adaptation. These concerns do not apply to the present study, which uses only publicly available PubMed abstracts, involves no patient records, and requires no task-specific fine-tuning.

### B. Biomedical Literature Mining and Disease Knowledge Discovery

The automatic extraction of disease knowledge from biomedical literature has a long history. The oldest and most common approach is co-occurrence mining: when a disease term and a gene symbol appear frequently together in the same abstract, the system infers a relationship. Grissa *et al.* [8] built DISEASES 2.0 on this principle — a continuously updated database that mines PubMed for disease–gene links and integrates the results with GWAS evidence and curated sources. When full-text articles were added alongside abstracts, mined associations increased nine-fold, demonstrating the substantial signal carried even by abstract-level text. Co-occurrence mining, however, produces only flat pairwise lists. It cannot reveal how topics in the literature are organized, which research directions dominate, or how disease themes relate at the document level.

Xu *et al.* [9] built something structurally richer with their PubMed knowledge graph (PKG), constructed from 29 million abstracts. BioBERT was used for bio-entity extraction, outperforming prior tools by 0.51% F1, and the graph integrated author networks, funding, and institutional affiliations alongside biological entities. The PKG is a useful resource for studying how biomedical knowledge flows across institutions and disciplines, but its organization centers on entity-level links. The thematic distribution of disease research — which topics are prominent, which are marginal, and how they relate — is not what the system is designed to capture. Diaz Gonzalez *et al.* [10] applied the same logic to germline genetics, using BioBERT to construct SimpleGermKG with 297 genes, 130 diseases, and over 46,000 relational triples, with ontology-based normalization to standardize term variation. As with PKG, the output is organized around fixed entity types, and research themes outside the predefined schema do not appear.

Li *et al.* [11] moved closer to semantic territory with LORE, an unsupervised framework that reads PubMed abstracts as collections of verifiable relational statements and represents gene–disease pairs as embeddings in Euclidean space. Tested across 2,097 diseases, LORE reached 90% mean average precision for pathogenic-gene identification. A 2D UMAP projection of the embedding space further showed that pathogenic disease–gene pairs form a visually distinct region, suggesting that semantic embeddings of biomedical text carry geometric structure with biological meaning. LORE is the closest prior work in aim to the present study, but its output is a ranked gene list. The abstract itself — its research context, disease framing, and scientific narrative — is not the object of analysis.

Supervised extraction methods achieve strong results but require labeled data and predefined schemas. Zhang *et al.* [12] converted syntactically complex biomedical sentences into structured semantic graphs using Abstract Meaning Representation (AMR) and enriched those graphs with external ontological knowledge. On the GENIA 2011 benchmark, this approach gained 1.8% F1 from AMR and 3.0% from knowledge enrichment, with further validation on COVID-19 literature. The system performs well for the entity types and events it was trained to find; anything outside those categories goes undetected, regardless of frequency. Masoumi *et al.* [13] illustrated the same boundary at classification scale: BioBERT classifiers trained on 12,817 PubMed abstracts categorized documents into predefined medical fields with 76–86% micro-F1. The system works within its defined taxonomy and nowhere else.

Chuang *et al.* [14] took a different direction with DiscoverPath, a NER-based retrieval system that builds entity relationship graphs from biomedical abstracts to help researchers navigate cross-disciplinary vocabulary. DiscoverPath solves a real search problem — it helps a researcher find papers they already know to look for. But search and discovery are not the same thing. There are research themes that a researcher does not know to look for; these remain out of reach for retrieval systems anchored to a fixed schema.

### C. Unsupervised Clustering and Topic Modeling in Biomedical Text

When no labeled data are available, unsupervised clustering is the way to find structure in biomedical text. Latent Dirichlet Allocation (LDA) [7] and Non-negative Matrix Factorization (NMF) [9] have been the traditional workhorses. Both treat each document as a bag of words, discarding all information about how terms within a document relate to each other and how word meaning shifts with context [15]. They also discard word order. TF-IDF vectors share the same problem: they count word frequency, not word meaning. Clusters produced this way reflect surface vocabulary overlap, not conceptual organization. In biomedical text, where researchers describing the same biological mechanism often use entirely different terminology depending on the subfield, this is a real and significant limitation.

Contextual embeddings from transformer models changed what was possible. In a PubMed clustering experiment, Davagdorj *et al.* [15] evaluated this by running Gaussian Mixture Models (GMM) against K-Means, DBSCAN, and agglomerative techniques and substituting BioBERT embeddings for TF-IDF vectors. On all three evaluation metrics — Davies–Bouldin score (1.6849), adjusted Rand index (0.4478), and silhouette coefficient (0.3765) — the BioBERT-GMM combination came in first. When the representation carries semantic content, the clusters reflect it. GMM's limitation, however, is that it requires the analyst to fix the number of clusters in advance and assumes each cluster takes an approximately Gaussian shape. Biomedical research themes do not satisfy that assumption: they vary widely in size, overlap in unpredictable ways, and have no reason to be normally distributed.

AbdelAziz *et al.* [16] combined BERT embeddings with topic modeling and hierarchical clustering for extractive summarization of 200 biomedical papers, reaching ROUGE-1 of 0.4838 with expert completeness ratings averaging 4.10. The sequential structure of their approach — embedding, clustering, keyword extraction — resembles the kind of pipeline used for document-level knowledge organization. Summarizing individual documents and mapping themes across a corpus are different problems, and AbdelAziz *et al.* address the former.

Grootendorst [17] introduced BERTopic, the most methodologically relevant prior work in this space. BERTopic generates document embeddings from a transformer model, clusters them with HDBSCAN, and labels each cluster using a class-based TF-IDF (c-TF-IDF) procedure that weights terms by their importance within a cluster rather than across the whole corpus. This is an important design insight: a term like *metformin* may appear in thousands of abstracts, but its elevated frequency within one specific cluster identifies that cluster as diabetes-related far more precisely than any global frequency measure could. BERTopic performs well against LDA and other topic models. Where it falls short for the present purpose is in the embedding stage: BERTopic uses general sentence-transformer models, not biomedical-domain ones. The representational depth that BioBERT gains from PubMed and PMC pre-training is not part of its design.

Munoz-Farre *et al.* [18] offered a useful perspective from clinical data: transformer embeddings combined with time-series clustering stratified UK Biobank participants with type 2 diabetes into distinct patient subgroups with different aetiological and prognostic profiles. The input is structured EHR data rather than text, but the core finding carries across: deep embeddings, when organized through density-based clustering, can surface disease-specific structure without any labeled supervision.

### D. Visualization and Knowledge Mapping of Biomedical Embeddings

High-dimensional embeddings are not interpretable on their own. Dimensionality reduction is needed to make the structure they encode visible and analyzable. Oubenali *et al.* [19] reviewed 30 studies on visualization methods for biomedical word embeddings across PubMed, MedRxiv, and arXiv. UMAP and t-SNE were the most common techniques. The review also noted that no consistent guidelines exist for when to use which method or how to interpret the projections produced. Studies use visualization interchangeably for exploration, evaluation, and presentation, often without clarifying which purpose is being served. In most cases, visualization is applied after conclusions have already been drawn by other means; the ability of the visualization to reveal a structure that was not already known goes mostly unused.

UMAP has specific properties that make it well-suited to this kind of analysis. Grounded in Riemannian geometry and algebraic topology, it preserves both local neighborhood structure and global data topology more faithfully than t-SNE, while scaling efficiently to large datasets [19]. Panesar [20] provided evidence that BioBERT embeddings are particularly well-matched to UMAP projection: contextual representations from BioBERT capture relational knowledge between biomedical concepts more accurately than static models like Word2Vec, especially for functional and mechanistic relationships that describe disease processes. In 2D UMAP projections of these representations, spatial proximity reflects genuine semantic relatedness rather than surface-level co-occurrence.

Li *et al.* [11] showed what this looks like in practice. When disease–gene embeddings were projected using UMAP and colored by ClinVar pathogenicity labels, pathogenic associations formed a geometrically distinct region with a smooth gradient across the embedding space — a structure that simply cannot be seen in a table or a ranked list. Xu *et al.* [9] and Chuang *et al.* [14] both used visualization in their respective systems, primarily to display graph-based entity relationships: one focusing on scholarly connection networks in PubMed, the other on cross-disciplinary terminology navigation. Graph topology and semantic embedding geometry are different things, serving different purposes. Neither system attempts to map how disease research themes are distributed across a document corpus.

### E. Research Gap and Motivation

Across the four areas reviewed above, the pattern is consistent. Biomedical language models produce strong, domain-aware embeddings [1]–[7], yet evaluations have focused almost entirely on supervised tasks. Literature mining builds entity graphs and association databases at an impressive scale [8]–[14]; their outputs, however, are organized around predefined schemas, and the data-driven thematic structure of a disease corpus is simply not what these systems are built to reveal. Clustering and topic modeling have adopted contextual embeddings [15]–[18], but the existing frameworks either impose parametric assumptions that biomedical research themes do not satisfy, use general-purpose embedding models that miss the advantages of biomedical pre-training, or target document summarization rather than corpus-level theme discovery. Visualization tools have been applied to biomedical embedding spaces [11], [19], [20] mostly as a post-hoc display layer rather than as an integrated analytical stage in the discovery process.

To the best of our knowledge, no existing study has combined BioBERT-based semantic embeddings, UMAP dimensionality reduction, HDBSCAN density clustering, and class-based TF-IDF cluster keyword extraction into a unified, disease-targeted pipeline for unsupervised knowledge discovery from PubMed abstracts. The individual components have each been studied — domain-adapted language models, density-based clustering, cluster-level keyword interpretation, and UMAP-based projection all exist and have been validated in relevant contexts. What has not been done is combining them specifically for the purpose of mapping disease knowledge from biomedical literature without labeled data. That gap is what the present study addresses.

---

## III. Dataset Description

### A. Corpus Construction

The corpus was assembled by querying the NCBI Entrez programming utility (E-utilities) via the Biopython client (`Bio.Entrez`) [8]. Eight disease-domain queries were issued against the PubMed database between January and May 2026, targeting the highest-burden chronic and acute disease areas in global epidemiology: *diabetes mellitus*, *cancer neoplasm*, *cardiovascular disease*, *neurological disorders*, *stroke cerebrovascular*, *hypertension blood pressure*, *Alzheimer disease dementia*, and *Parkinson disease*. For each query, a maximum of 2,000 PubMed Identifiers (PMIDs) were requested and retrieved in batches of 200 records using the history server of the Entrez system, with a 0.4-second inter-batch delay to comply with NCBI's three-requests-per-second rate limit. A global de-duplication step removed PMIDs that overlapped across queries, ensuring that each abstract was retained only once and assigned the disease label of the query under which it was first retrieved.

For each unique PMID, the title and full abstract text were fetched in XML format and parsed. Structured abstracts (those represented as a list of labeled sections such as "Background", "Methods", "Results", "Conclusions") were flattened by joining section strings with single spaces. Records with empty or missing abstracts and records shorter than 50 characters were discarded.

### B. Final Dataset Statistics

The resulting dataset, `pubmed_dataset.csv`, contains **14,065 records** (after preprocessing, the analytic corpus contains **14,064 abstracts**, since one record was filtered out by length). Each record includes four fields: `PMID`, `Title`, `Abstract`, and `Disease` (the originating query label). The disease-domain distribution is shown in **Table I**.

**Table I. Disease-Domain Distribution in the Analytic Corpus (N = 14,064)**

| Disease Domain                  | # Abstracts | % of Corpus |
|---------------------------------|------------:|------------:|
| Cancer / neoplasm               |       1,951 |       13.9% |
| Diabetes mellitus               |       1,922 |       13.7% |
| Stroke / cerebrovascular        |       1,880 |       13.4% |
| Alzheimer disease / dementia    |       1,753 |       12.5% |
| Hypertension / blood pressure   |       1,747 |       12.4% |
| Cardiovascular disease          |       1,722 |       12.2% |
| Neurological disorders          |       1,586 |       11.3% |
| Parkinson disease               |       1,503 |       10.7% |
| **Total**                       |  **14,064** |   **100.0%** |

The eight disease domains are well balanced (range: 10.7%–13.9%), reducing the risk that a clustering algorithm's structure is dominated by a single over-represented topic. The query labels are used *only* for stratified reporting and for sanity-checking the validity of discovered clusters; they are not provided to any clustering or representation-learning algorithm, preserving the unsupervised character of the analysis.

### C. Preprocessing

A uniform preprocessing pipeline was applied to every abstract:

1. Lowercasing of all tokens.
2. Removal of standard English stop words using the NLTK stop-word corpus.
3. Stripping of punctuation and all non-alphanumeric characters.
4. Removal of tokens with length ≤ 2 characters.
5. **No** stemming or lemmatization — to preserve biomedical term integrity (e.g., *Alzheimer's* vs. *Alzheimer*).

After preprocessing, the corpus contained a mean of approximately 147 tokens per abstract (σ ≈ 49), with a minimum of 12 and a maximum of 412 tokens. The processed corpus was serialized as `step2_cleaned_corpus.csv` for full reproducibility. The word-count distributions of the raw and cleaned corpora are shown in `BioBERT Results/step1_raw_length_distribution.png` and `step2_preprocessing_stats.png` (Appendix A, available as supplementary material).

The full dataset, retrieval script, and preprocessing code are released with the manuscript and are available at [GitHub repository URL]. PubMed metadata were retrieved under the NCBI data-access policy; only publicly indexed abstracts were used, with no patient-identifiable information.

---

## IV. Methodology

The proposed pipeline comprises five stages: (1) text representation, (2) dimensionality reduction, (3) clustering, (4) topic-keyword extraction, and (5) automated disease mapping. The complete pipeline is illustrated in Fig. 1.

> **Fig. 1.** *Complete pipeline architecture: from the PubMed corpus through dual representation (TF-IDF / BioBERT), UMAP reduction, three clustering algorithms, automated keyword extraction, and a three-metric evaluation framework. All six pipeline configurations (2 representations × 3 algorithms) are evaluated under identical conditions to enable controlled comparison. Place at the beginning of Section IV.*

### A. Text Representation

Two complementary text-representation strategies are evaluated.

#### 1) TF-IDF (Statistical Baseline)

Each document *d* in corpus 𝒟 is represented as a sparse vector **v**_d ∈ ℝ^|𝒱|, where |𝒱| is the vocabulary size. The weight of term *t* in document *d* is:

$$\text{TF-IDF}(t, d, \mathcal{D}) = \text{TF}(t, d) \times \text{IDF}(t, \mathcal{D})$$

with

$$\text{TF}(t, d) = \frac{f_{t,d}}{\sum_{t' \in d} f_{t',d}}$$

$$\text{IDF}(t, \mathcal{D}) = \log \frac{|\mathcal{D}| + 1}{|\{d \in \mathcal{D} : t \in d\}| + 1} + 1$$

where *f*_{t,d} is the raw count of term *t* in document *d*. The +1 smoothing in the IDF denominator prevents division by zero for terms absent from the corpus. Each document vector is L2-normalized prior to clustering. In our implementation, `TfidfVectorizer` from scikit-learn is used with default parameters except for `min_df = 2`, `max_df = 0.95`, and `stop_words = 'english'`, which yielded a vocabulary of 16,286 terms.

#### 2) BioBERT Contextual Embeddings

We employ the pre-trained `dmis-lab/biobert-v1.1` model [1] from the Hugging Face Transformers library. BioBERT is initialized from BERT-Base (12 transformer layers, 12 attention heads, hidden size *H* = 768) and further pre-trained on approximately 4.5 billion words of PubMed abstracts and 13.5 billion words of PMC full-text articles.

For each abstract, the cleaned text is tokenized using BioBERT's WordPiece tokenizer with `max_length = 128`, batch size 32, and dynamic padding. Abstracts exceeding the 128-token limit are truncated. Document-level embeddings are obtained by **mean-pooling the final-layer hidden states** across all non-padding tokens:

$$\mathbf{e}_d = \frac{1}{|\mathcal{T}_d|} \sum_{i \in \mathcal{T}_d} \mathbf{h}_i^{(L)}$$

where 𝒯_d is the set of non-padding token indices for document *d*, **h**_i^(L) ∈ ℝ^768 is the hidden state of token *i* at the final transformer layer *L*, and **e**_d ∈ ℝ^768 is the document embedding. Mean pooling was preferred over `[CLS]`-token extraction because it captures the aggregate contextual semantics of the full abstract rather than relying on a single summary token, an advantage for variable-length biomedical text. The resulting matrix has shape (14,064, 768) and is L2-normalized prior to dimensionality reduction.

> **Fig. 2.** *Unsupervised 2D UMAP projections of (a) BioBERT embeddings and (b) TF-IDF embeddings, prior to clustering. BioBERT's projection exhibits visibly denser, more sharply defined clusters, consistent with its semantic encoding of biomedical terminology. Source: `BioBERT Results/step5_umap2d_unlabeled.png` and `TF-IDF Results/step5_umap2d_unlabeled.png`. Place at the end of Section IV-A.*

### B. Dimensionality Reduction via UMAP

Both TF-IDF and BioBERT spaces are projected to two dimensions using UMAP [16] prior to clustering. UMAP minimizes the cross-entropy between a high-dimensional fuzzy topological representation and a low-dimensional counterpart:

$$\mathcal{L} = \sum_{(i,j) \in E} \left[ w_{ij} \log \frac{w_{ij}}{\hat{w}_{ij}} + (1 - w_{ij}) \log \frac{1 - w_{ij}}{1 - \hat{w}_{ij}} \right]$$

where *w*_{ij} is the high-dimensional fuzzy set-membership weight for the edge between points *i* and *j*, and *ŵ*_{ij} is the corresponding low-dimensional weight. The hyperparameter choices are summarized in **Table II**.

**Table II. UMAP Hyperparameters**

| Parameter      | Value  | Justification                                                       |
|----------------|--------|---------------------------------------------------------------------|
| `n_neighbors`  | 15     | Controls local/global structure trade-off; 15 balances both         |
| `min_dist`     | 0.1    | Low value allows tighter packing of dense clusters                  |
| `n_components` | 2      | 2D projection for both visualization and clustering input           |
| `metric`       | cosine | Appropriate for L2-normalized embedding vectors                     |
| `random_state` | 42     | Ensures reproducibility                                             |

UMAP is used as a *pre-clustering* step, not merely for visualization. UMAP's preservation of local neighborhood structure means that clusters formed in the 2D UMAP space correspond to genuine density structures in the original high-dimensional space [16]. Identical UMAP parameters are used for the TF-IDF and BioBERT representations to enable controlled comparison.

### C. Clustering Algorithms

Three unsupervised clustering algorithms are applied to the UMAP-reduced embeddings.

#### 1) K-Means (Global, Macro-Level)

K-Means minimizes the within-cluster sum of squared distances:

$$\underset{S}{\arg\min} \sum_{k=1}^{K} \sum_{\mathbf{x} \in S_k} \|\mathbf{x} - \boldsymbol{\mu}_k\|^2$$

where *S* = {*S*₁, *S*₂, …, *S_K*} is the partition, **μ**_k is the centroid of cluster *S_k*, and *K* is the number of clusters. The optimal *K* = 5 is determined automatically by the elbow method over *K* ∈ {2, 3, …, 15}, identified as the point of maximum curvature in the inertia curve (`BioBERT Results/step6a_automated_elbow_method.png`).

#### 2) Hierarchical Agglomerative Clustering (HAC, Ward Linkage)

HAC with Ward's minimum-variance linkage is used. Ward's criterion merges the two clusters that produce the smallest increase in total within-cluster variance:

$$\Delta(A, B) = \frac{n_A \cdot n_B}{n_A + n_B} \|\boldsymbol{\mu}_A - \boldsymbol{\mu}_B\|^2$$

where *n_A*, *n_B* are the cluster sizes and **μ**_A, **μ**_B are the centroids. The same *K* = 5 used for K-Means is applied to enable a controlled comparison.

#### 3) HDBSCAN (Density-Based, Micro-Level)

HDBSCAN [5] constructs a hierarchy of density-based clusters from a minimum-spanning tree over the mutual reachability graph of the data. The core distance for a point **x**_p with respect to minimum cluster size *m_clSize* is:

$$d_{\text{core}}(\mathbf{x}_p) = d(\mathbf{x}_p, \mathbf{x}_{m_{\text{clSize}}})$$

where **x**_{m_clSize} is the *m_clSize*-th nearest neighbor of **x**_p. The mutual-reachability distance is:

$$d_{\text{mreach}}(\mathbf{x}_p, \mathbf{x}_q) = \max\left(d_{\text{core}}(\mathbf{x}_p),\ d_{\text{core}}(\mathbf{x}_q),\ d(\mathbf{x}_p, \mathbf{x}_q)\right)$$

HDBSCAN extracts a flat clustering from the condensed cluster tree by selecting clusters that maximize a stability metric. Points not belonging to any sufficiently stable cluster are labeled as noise (label = −1). The hyperparameters used are summarized in **Table III**.

**Table III. HDBSCAN Hyperparameters**

| Parameter                | Value | Justification                                                          |
|--------------------------|-------|------------------------------------------------------------------------|
| `min_cluster_size`       | 30    | Minimum documents per micro-topic; prevents singleton clusters         |
| `min_samples`            | 5     | Controls noise sensitivity; lower = fewer noise points                 |
| `cluster_selection_method` | `eom` | Excess of Mass: stable, well-calibrated cluster selection            |
| `metric`                 | euclidean | Applied on UMAP 2D space                                          |

HDBSCAN identified **80 micro-clusters** in the BioBERT pipeline and **116 micro-clusters** in the TF-IDF pipeline, automatically adapting its resolution to the local density structure of each embedding space. The substantial difference in cluster count (80 vs. 116) reflects the different geometry of the two embedding spaces: TF-IDF's sparse, high-dimensional representation preserves term co-occurrence directly, producing more numerous but smaller, sharper clusters, while BioBERT's dense semantic space tends to merge related but terminologically distinct documents into broader clusters.

> **Fig. 3.** *Labeled UMAP projections for (a) BioBERT and (b) TF-IDF pipelines, with K-Means, HDBSCAN, and HAC cluster assignments color-coded. This composite figure provides the most visually comprehensive comparison of the three clustering strategies on each representation. HDBSCAN's output (center panel) reveals fine-grained, irregularly shaped micro-clusters that the other two algorithms are structurally incapable of resolving. Source: `BioBERT Results/step6b_cluster_umap_all.png` and `TF-IDF Results/step6b_cluster_umap_all.png`. Place at the beginning of Section VI.*

### D. Topic Keyword Extraction

For each cluster (K-Means, HAC, and HDBSCAN), the top *N_k* keywords are extracted by computing per-cluster TF-IDF scores — treating all documents within a cluster as a single meta-document and ranking terms by their within-cluster TF-IDF weight relative to the full corpus. For K-Means and HAC, *N_k* = 15; for HDBSCAN micro-clusters, *N_k* = 10. Noise-labeled documents (label = −1) are excluded from all keyword extraction and from coherence evaluation.

### E. Automated Disease Knowledge Mapping

For each K-Means cluster, a human-readable clinical label is generated by selecting the top two highest-weighted keywords and concatenating them (e.g., Cluster 4 → "Cognitive, Dementia"). This automated label serves two purposes: (i) it provides a low-effort summary of the cluster's clinical content, and (ii) it offers a transparent, reproducible alternative to manual labeling. The complete mapping is saved as `step10_disease_knowledge_mapping.csv` for both pipelines.

> **Fig. 4.** *UMAP projections with automatically generated clinical labels overlaid on each K-Means cluster centroid for (a) BioBERT and (b) TF-IDF pipelines. Labels are derived from the top two keywords of each cluster. Source: `BioBERT Results/step11_final_mapped_umap_all_algorithms.png` and `TF-IDF Results/step11_final_mapped_umap_all_algorithms.png`. Place at the end of Section IV-E.*

### F. Evaluation Metrics

Three complementary metrics are computed for every pipeline-algorithm combination.

#### 1) Silhouette Score

The Silhouette Score measures how similar a document is to its own cluster compared to other clusters. For document *i*:

$$s(i) = \frac{b(i) - a(i)}{\max\{a(i), b(i)\}}$$

where *a*(*i*) is the mean intra-cluster distance and *b*(*i*) is the mean nearest-cluster distance. The corpus-level score is the mean over all non-noise documents: *S* = (1/*n*) ∑*_i s*(*i*) ∈ [−1, 1]. Higher values indicate better-separated clusters.

#### 2) Davies–Bouldin Index (DBI)

DBI measures average cluster compactness relative to inter-cluster separation:

$$\text{DBI} = \frac{1}{K} \sum_{i=1}^{K} \max_{j \neq i} \left( \frac{\sigma_i + \sigma_j}{d(\boldsymbol{\mu}_i, \boldsymbol{\mu}_j)} \right)$$

where *σ_k* is the mean distance of all documents in cluster *k* to centroid **μ**_k, and *d*(**μ**_i, **μ**_j) is the Euclidean distance between cluster centroids. Lower DBI indicates more compact, well-separated clusters.

#### 3) NPMI Topic Coherence

NPMI coherence [24] measures the semantic co-occurrence quality of the top-*M* keywords {*w*₁, *w*₂, …, *w_M*} for a given cluster. For each word pair (*w_i*, *w_j*):

$$\text{NPMI}(w_i, w_j) = \frac{\log \frac{P(w_i, w_j)}{P(w_i) \cdot P(w_j)}}{-\log P(w_i, w_j)}$$

where *P*(*w_i*, *w_j*) is the joint probability (co-occurrence in the same document) and *P*(*w_i*), *P*(*w_j*) are the marginal probabilities computed over the full corpus 𝒟. The cluster-level coherence is the mean NPMI over all *M(M−1)/2* pairs:

$$\text{Coherence}(C_k) = \frac{2}{M(M-1)} \sum_{i < j} \text{NPMI}(w_i, w_j)$$

In this study, *M* = 10 (top 10 keywords per cluster) is used consistently across all configurations. The pipeline-level coherence is the macro-average over all clusters: $\overline{\text{NPMI}} = (1/K) \sum_k \text{Coherence}(C_k)$. NPMI is implemented from scratch on a binary document–term matrix (`CountVectorizer` with `binary = True`, `min_df = 5`, `max_df = 0.95`), avoiding the dependency on Gensim and ensuring complete reproducibility.

For HDBSCAN, per-topic NPMI scores are also retained to support distribution-level analysis (coherence boxplots, comparison with the K-Means macro-average), since not all 80 or 116 micro-clusters are guaranteed to be semantically coherent.

---

## V. Experimental Setup

### A. Hardware and Software

All experiments were executed on a workstation with an NVIDIA GPU (CUDA-enabled) and a Python 3.14 environment. The complete software stack is listed in **Table IV**.

**Table IV. Software Dependencies**

| Package                | Version    | Role                                              |
|------------------------|------------|---------------------------------------------------|
| `transformers`         | ≥ 4.40     | BioBERT loading and inference                     |
| `torch`                | ≥ 2.4      | GPU-accelerated transformer forward pass          |
| `sentence-transformers` | latest     | BioBERT embedding utilities (used)                |
| `umap-learn`           | 0.5.12     | UMAP dimensionality reduction                     |
| `hdbscan`              | latest     | HDBSCAN density-based clustering                  |
| `scikit-learn`         | 1.8        | K-Means, HAC, Silhouette, DBI, CountVectorizer    |
| `nltk`                 | latest     | Stop-word and tokenization utilities              |
| `pandas` / `numpy`     | latest     | Data wrangling and numerical computation          |
| `matplotlib` / `seaborn` | latest  | Visualization                                     |
| `biopython`            | 1.87       | PubMed E-utilities client                         |

Random seeds (`random_state = 42`) were fixed for UMAP, K-Means, and any other stochastic operation, ensuring bit-exact reproducibility of the results.

### B. BioBERT Embedding Extraction

The `dmis-lab/biobert-v1.1` model was loaded from the Hugging Face model hub, transferred to the available CUDA device, and set to evaluation mode (`model.eval()`). Embeddings were extracted in mini-batches of 32 abstracts under `torch.no_grad()`. The mean-pooling operation followed the standard BERT recipe: the final hidden state was masked by the attention mask, summed, and divided by the number of non-padding tokens. The resulting matrix (14,064 × 768) was L2-normalized and saved as `step3_biobert_sample.csv` (first 100 documents) and used as input to UMAP.

### C. K-Means, HAC, and HDBSCAN Configurations

For K-Means and HAC, the number of clusters *K* = 5 was selected automatically by the elbow method, which examines the within-cluster sum of squares (inertia) for *K* ∈ {2, …, 15} and identifies the point of maximum curvature as the optimal *K*. The elbow curve is shown in `step6a_automated_elbow_method.png` (Appendix A). K-Means was run with `n_init = 20` random restarts to mitigate sensitivity to centroid initialization.

For HDBSCAN, the choice of `min_cluster_size = 30` reflects a deliberate trade-off: a smaller value would produce many small clusters with few documents each, which limits the statistical reliability of the per-cluster coherence estimate; a larger value would force unrelated documents into the same cluster. `min_samples = 5` was selected to control the noise-labeling threshold.

### D. NPMI Coherence Implementation

The NPMI computation was implemented in NumPy/scikit-learn to avoid the Gensim dependency and to ensure full reproducibility. A binary `CountVectorizer` (`min_df = 5`, `max_df = 0.95`, `stop_words = 'english'`) was fitted on the cleaned corpus to obtain a (14,064 × 16,286) document–term matrix. Marginal word frequencies and pairwise joint frequencies were pre-computed as sparse column slices, and NPMI was computed for every word pair of every cluster's top-10 keywords. The full per-topic NPMI table for all 6 pipeline–algorithm combinations (90 topics for BioBERT, 231 for TF-IDF) is available as `Coherence Results/topic_coherence_per_topic.csv`.

### E. Reproducibility Statement

All code, hyperparameters, and random seeds are released with the manuscript at [GitHub repository URL]. The PubMed retrieval script (`API.ipynb`) and the complete preprocessing, embedding, clustering, and evaluation pipelines are version-controlled. The dataset can be re-constructed exactly by running the retrieval script with the documented queries and the date range January 1 – May 1, 2026.

---

## VI. Results

### A. Quantitative Clustering Evaluation

**Table V** reports the three evaluation metrics across all six pipeline–algorithm combinations. Two findings stand out immediately.

**Table V. Clustering Evaluation Metrics Across All Six Pipelines**

| Representation | Algorithm   | # Clusters | Silhouette ↑ | DBI ↓    | NPMI Coherence ↑ |
|----------------|-------------|-----------:|-------------:|---------:|-----------------:|
| BioBERT        | HDBSCAN     | 80         | 0.4225       | **0.7068** | 0.1154         |
| BioBERT        | K-Means     | 5          | 0.4112       | 0.8124   | 0.0823           |
| BioBERT        | HAC (Ward)  | 5          | 0.3660       | 0.8845   | 0.0598           |
| TF-IDF         | HDBSCAN     | 116        | **0.4786**   | **0.6034** | **0.1158**     |
| TF-IDF         | K-Means     | 5          | 0.3708       | 0.8426   | 0.0780           |
| TF-IDF         | HAC (Ward)  | 5          | 0.2791       | 0.9584   | 0.0709           |

*↑ = higher is better; ↓ = lower is better. Bold indicates best value per metric across all pipelines.*

> **Fig. 5.** *Three-panel evaluation metrics comparison: (a) Silhouette Score and (b) Davies–Bouldin Index bar charts across all six pipelines, and (c) NPMI coherence boxplot showing the per-topic distribution for each pipeline–algorithm combination. The boxplot confirms that HDBSCAN's higher mean NPMI is not driven by a single outlier cluster: the inter-quartile range of per-cluster NPMI for HDBSCAN lies entirely above the median NPMI of K-Means in both pipelines. Source: `BioBERT Results/step8_evaluation_metrics.png`, `TF-IDF Results/step8_evaluation_metrics.png`, `Coherence Results/coherence_per_topic_boxplot.png`, and `Coherence Results/coherence_grouped_bar.png`. Place directly below Table V.*

Three observations follow from Table V:

1. **HDBSCAN yields the best NPMI coherence in both pipelines.** BioBERT HDBSCAN reaches NPMI = 0.1154 — a 40.3% relative improvement over BioBERT K-Means (0.0823). TF-IDF HDBSCAN reaches NPMI = 0.1158 — a 48.5% relative improvement over TF-IDF K-Means (0.0780). This finding is robust: it holds whether the representation is contextual (BioBERT) or statistical (TF-IDF).
2. **TF-IDF HDBSCAN achieves the highest Silhouette Score (0.4786) and the lowest DBI (0.6034)** of all six configurations, indicating that the TF-IDF micro-clusters are also the most geometrically compact and best separated. BioBERT HDBSCAN is a close second on both metrics.
3. **HAC is the weakest algorithm on every metric in both pipelines.** BioBERT HAC records the lowest Silhouette among BioBERT pipelines (0.3660) and the highest DBI (0.8845); TF-IDF HAC records the lowest Silhouette of all six pipelines (0.2791) and the highest DBI (0.9584).

### B. Inter-Concept Similarity (Anchor Diagnostics)

A complementary diagnostic was performed before clustering. For each pipeline, the cleaned corpus was reduced to *K* = 10 pseudo-anchors by K-Means, and pairwise cosine similarity between anchor centroids was computed in the original embedding space. For BioBERT, anchor similarities range from 0.70 to 0.99 (mean ≈ 0.97) — every anchor is highly similar to every other anchor. This near-saturation is expected for a 768-dimensional dense embedding space in which documents from different disease domains share substantial semantic content. For TF-IDF, anchor similarities range from 0.25 to 0.67 (mean ≈ 0.44), reflecting the much higher *orthogonality* of sparse, term-specific vectors. The corresponding heatmaps are shown in `BioBERT Results/step4_inter_concept_similarity.png` and `TF-IDF Results/step4_inter_concept_similarity.png` (Appendix A). The diagnostic supports a key methodological choice: the same downstream clustering algorithm behaves very differently on the two representations, and the *differences* in geometric separability are themselves a source of insight.

### C. Macro-Level Analysis: K-Means Clusters (*K* = 5)

K-Means produced five broad thematic partitions for each pipeline. The clinical labels derived from the top-2 keywords of each cluster are reported in **Table VI** (BioBERT) and **Table VII** (TF-IDF).

**Table VI. BioBERT K-Means — Macro-Level Clinical Cluster Summary**

| Cluster | Assigned Clinical Category      | Top-5 Keywords (TF-IDF)                                  | NPMI   |
|--------:|----------------------------------|----------------------------------------------------------|--------|
| 0       | Cardiovascular & Metabolic Risk  | patients, risk, care, studies, hypertension              | 0.0597 |
| 1       | Preclinical Molecular Biology    | disease, cells, cell, expression, therapeutic            | 0.1092 |
| 2       | Oncology & Case Studies          | patients, clinical, case, treatment, patient             | 0.0797 |
| 3       | Clinical Outcomes & Mortality    | patients, risk, stroke, group, ipi                       | 0.1020 |
| 4       | Neurocognitive Disorders         | patients, cognitive, disease, clinical, risk             | 0.0611 |

**Table VII. TF-IDF K-Means — Macro-Level Clinical Cluster Summary**

| Cluster | Assigned Disease Topic          | Top-5 Keywords (TF-IDF)                                  | NPMI   |
|--------:|----------------------------------|----------------------------------------------------------|--------|
| 0       | Neurocognitive / Dementia       | patients, cognitive, dementia, brain, analysis           | 0.0448 |
| 1       | Oncology / Cancer               | patients, cancer, tumor, cells, survival                 | 0.0311 |
| 2       | Hypertension & Cardiovascular   | risk, hypertension, blood, pressure, diabetes            | 0.1248 |
| 3       | Molecular Biology               | disease, therapeutic, cells, expression, protein         | 0.1092 |
| 4       | Stroke & Clinical Outcomes      | patients, stroke, mortality, outcomes, group             | 0.0803 |

The five-cluster partitions from both pipelines converge on the same five broad clinical themes: cardiovascular/metabolic disease, neuroscience/dementia, oncology, molecular mechanisms, and clinical outcomes. This thematic convergence validates the clinical relevance of both representations at the macro level, despite their representational differences. However, the heterogeneity within each macro-cluster (evidenced by the mixed top keywords — e.g., *patients* appears across all five clusters) illustrates the fundamental limitation of global partition-based clustering: clinically distinct sub-populations are merged into a single partition, and the per-cluster NPMI scores are consequently moderate (0.0311 to 0.1248).

> **Fig. 6.** *K-Means macro-level clusters visualized on the UMAP projection for (a) BioBERT and (b) TF-IDF pipelines. The five thematic partitions recover the broad disease domains of the corpus, but the cluster boundaries are coarse and multiple micro-domains are merged. Source: `BioBERT Results/step6b_cluster_umap_all.png` and `TF-IDF Results/step6b_cluster_umap_all.png` (K-Means panels). Place below Tables VI and VII.*

### D. Micro-Level Analysis: HDBSCAN Micro-Topic Discovery

HDBSCAN identified **80 biologically distinct micro-clusters** from the BioBERT pipeline and **116 micro-clusters** from the TF-IDF pipeline. The top 10 micro-topics by NPMI coherence are presented in **Tables VIII and IX**.

**Table VIII. Top 10 BioBERT HDBSCAN Micro-Topics by NPMI Coherence**

| Rank | Cluster | Inferred Micro-Topic                  | Top Keywords                                                                                | NPMI   |
|-----:|--------:|----------------------------------------|---------------------------------------------------------------------------------------------|--------|
| 1    | 43      | Plasma Biomarkers (Alzheimer's)        | ptau, plasma, amyloid, tau, csf, pet, biomarkers, gfap                                      | **0.3220** |
| 2    | 65      | Alpha-Synuclein Aggregation            | syn, synuclein, aggregation, tau, amyloid, fibrils, formation, protein                      | 0.2822 |
| 3    | 46      | Tumor Immunology & Resistance          | cells, tumor, cancer, immune, expression, breast, resistance                                | 0.2465 |
| 4    | 67      | Gut Microbiota & Metabolic Disease     | gut, microbiota, microbial, metabolic, axis, microbiome, evidence, health, review           | 0.2260 |
| 5    | 45      | Cancer Immunotherapy                   | cells, immune, tumor, cell, cancer, clinical, therapeutic, immunotherapy, tumors           | 0.2183 |
| 6    | 71      | Mitochondrial Neurodegeneration        | disease, mitochondrial, therapeutic, protein, neurodegenerative, autophagy, neuroinflammation, synaptic | 0.1980 |
| 7    | 69      | Tau & Amyloid Neurodegeneration        | disease, tau, amyloid, cognitive, therapeutic, neurodegenerative, neurons, pathology        | 0.1961 |
| 8    | 75      | Mitochondrial Signaling (Mouse Model)  | mice, mitochondrial, disease, therapeutic, neuronal, signaling, lipid, neuroinflammation    | 0.1943 |
| 9    | 68      | Hypertension & Kidney Disease          | patients, hypertension, ipi, pressure, blood, sbp, kidney, abpm, risk, associated         | 0.1829 |
| 10   | 74      | Mitochondrial Dysfunction (Review)     | disease, mitochondrial, neurodegenerative, brain, dysfunction, review, synaptic             | 0.1819 |

**Table IX. Top 10 TF-IDF HDBSCAN Micro-Topics by NPMI Coherence**

| Rank | Cluster | Inferred Micro-Topic                  | Top Keywords                                                                                | NPMI   |
|-----:|--------:|----------------------------------------|---------------------------------------------------------------------------------------------|--------|
| 1    | 13      | Diabetic Wound Healing                 | wound, diabetic, healing, patients, foot, dfu, wounds, hydrogel, amputation                | **0.3431** |
| 2    | 7       | Gut Microbiota & Disease               | gut, microbiota, disease, microbial, microbiome, intestinal, axis, metabolites, metabolic   | 0.3255 |
| 3    | 17      | Pregnancy & Preeclampsia               | pregnancy, preeclampsia, maternal, women, outcomes, fetal, blood, pressure, gestational      | 0.2929 |
| 4    | 115     | Antihypertensive Treatment             | mmhg, hypertension, antihypertensive, sbp, systolic, blood, pressure, patients, treatment  | 0.2609 |
| 5    | 23      | Pulmonary Arterial Hypertension        | pulmonary, hypertension, patients, right, pressure, arterial, artery, cteph, heart, bpa    | 0.2480 |
| 6    | 24      | Alpha-Synuclein Aggregation            | syn, synuclein, aggregation, disease, fibrils, saa, amyloid, aggregates, formation, binding| 0.2450 |
| 7    | 79      | Type 2 Diabetes Management             | tdm, diabetes, insulin, patients, glucose, hbac, risk, type, glycemic, study               | 0.2419 |
| 8    | 91      | Cardiac Function & Atrial Disease      | atrial, strain, lvef, left, failure, heart, myocardial, risk, cardiac, patients             | 0.2319 |
| 9    | 25      | Plasma Biomarkers (Neurodegeneration)  | ptau, plasma, gfap, biomarkers, cognitive, nfl, disease, levels, clinical, amyloid         | 0.2313 |
| 10   | 106     | Dementia Caregiving Research           | adrd, caregivers, research, care, caregiver, health, burden, dementia, recruitment          | 0.2226 |

> **Fig. 7.** *Heatmap of top-keyword TF-IDF weights for the top 10 HDBSCAN micro-clusters in the (a) BioBERT and (b) TF-IDF pipelines. Each row is a micro-topic; cell intensity indicates the within-cluster TF-IDF weight. The heatmap makes the high specificity of the micro-topics visually unambiguous. Source: `BioBERT Results/step9_cluster_keywords.png` and `TF-IDF Results/step9_cluster_keywords.png`. Place at the beginning of Section VI-D.*

The relative gain of each HDBSCAN top micro-topic over the corresponding K-Means baseline is striking:

- BioBERT Cluster 43 (plasma Alzheimer's biomarkers): NPMI = 0.3220 — a **291% relative gain** over the BioBERT K-Means mean (0.0823).
- TF-IDF Cluster 13 (diabetic wound healing): NPMI = 0.3431 — a **340% relative gain** over the TF-IDF K-Means mean (0.0780).

Critically, none of these high-coherence micro-topics are resolvable from the K-Means five-cluster partition: "plasma biomarkers for Alzheimer's disease" and "alpha-synuclein aggregation" are both subsumed within K-Means Cluster 4 (Neurocognitive Disorders), obscuring their distinct mechanistic identities.

> **Fig. 8.** *Per-cluster NPMI coherence of the top 10 HDBSCAN micro-topics, plotted against the global K-Means mean (dashed line) for (a) BioBERT and (b) TF-IDF. Every HDBSCAN top-10 micro-topic outperforms the K-Means macro-average, making the case for density-based micro-topic discovery unambiguous. Source: `Manuscript Results/Figure1_HDBSCAN_vs_KMeans_Coherence.png`. Place at the end of Section VI-D.*

### E. Cross-Representation Comparison: BioBERT vs. TF-IDF

While both HDBSCAN pipelines achieve comparable aggregate NPMI scores (0.1154 vs. 0.1158), the *character* of the micro-topics they discover is markedly different in clinically meaningful ways:

- **BioBERT HDBSCAN (80 clusters)** surfaces **mechanistic, pathway-level micro-topics** — mitochondrial dysfunction subtypes (Clusters 71, 75, 74), alpha-synuclein aggregation kinetics (Cluster 65), gut–brain axis metabolic signaling (Cluster 67), and tau/amyloid neurodegenerative mechanisms (Clusters 69, 43). Three of the top-10 micro-topics relate to mitochondrial pathways, which a bag-of-words model fails to consolidate because the relevant terms are contextually linked rather than lexically co-occurring. BioBERT's contextual encoding captures these cross-sentence semantic relationships that TF-IDF cannot.

- **TF-IDF HDBSCAN (116 clusters)** surfaces **clinically labeled, population-specific micro-topics** — diabetic wound healing (Cluster 13), preeclampsia (Cluster 17), antihypertensive management (Cluster 115), pulmonary arterial hypertension (Cluster 23), type 2 diabetes management (Cluster 79), and dementia caregiving (Cluster 106). These sub-domains are defined by highly specialized clinical terminology whose co-occurrence TF-IDF captures precisely.

The Jaccard overlap between the inferred clinical categories of the top-10 BioBERT and top-10 TF-IDF micro-topics is approximately 0.30, confirming that the two pipelines capture substantially complementary rather than redundant information. The most direct overlap is the gut-microbiota / metabolic-disease micro-topic (BioBERT Cluster 67, NPMI = 0.2260; TF-IDF Cluster 7, NPMI = 0.3255) and the alpha-synuclein / protein-aggregation micro-topic (BioBERT Cluster 65, NPMI = 0.2822; TF-IDF Cluster 24, NPMI = 0.2450) — both pipelines independently surface these themes, but with different keyword profiles and different downstream implications.

A practical implication: an **ensemble system** integrating both representation strategies would provide broader disease-mapping coverage than either pipeline alone. BioBERT would be used for mechanism discovery across disease boundaries (e.g., identifying that mitochondrial dysfunction recurs in neurodegeneration, metabolic disease, and cancer); TF-IDF would be used for sub-population and treatment-protocol identification within a single disease area.

### F. Aggregate Statistical Robustness

To confirm that the HDBSCAN NPMI advantage is not driven by outlier clusters, the per-cluster NPMI distribution was examined in detail. The boxplot in `Coherence Results/coherence_per_topic_boxplot.png` (Fig. 5c) shows that, in both pipelines, the *inter-quartile range* of HDBSCAN's per-cluster NPMI lies entirely above the *median* of K-Means and HAC. The per-topic NPMI scores are available for all 6 configurations in `Coherence Results/topic_coherence_per_topic.csv` (90 BioBERT topics and 231 TF-IDF topics in total). The heatmap in `Coherence Results/coherence_heatmap.png` provides a side-by-side view of all six pipeline–algorithm combinations.

---

## VII. Discussion

### A. Why Density-Based Clustering Wins for Biomedical Micro-Topic Discovery

The empirical results consistently support the superiority of HDBSCAN over fixed-partition algorithms for fine-grained biomedical topic discovery. The reason is structural. K-Means forces a partition of the embedding space into *K* Voronoi regions, which for a biomedical corpus covering multiple disease domains at multiple levels of specificity inevitably merges clinically distinct sub-populations. HDBSCAN's noise-aware density hierarchy instead identifies coherent groups of documents that naturally cluster together in the embedding space — groups that represent genuine research sub-fields rather than arbitrary partitions.

The 40%–49% relative improvement in NPMI coherence from K-Means to HDBSCAN is particularly meaningful in a clinical context: each unit increase in NPMI reflects tighter semantic co-occurrence of the cluster's defining terminology, which translates directly into the likelihood that a clinician or researcher reading that cluster's top keywords can correctly identify its biomedical focus without inspecting individual documents. The NPMI scores of the top HDBSCAN micro-topics (0.18–0.34) approach the practical threshold above which a topic is reliably interpretable from its keywords alone, while the K-Means macro-cluster NPMI scores (0.06–0.10) sit in a regime where keyword-level interpretation remains ambiguous.

### B. Complementary Strengths of BioBERT and TF-IDF

A common assumption in the NLP literature is that contextual embeddings uniformly supersede bag-of-words representations. Our results nuance this view. In aggregate NPMI coherence, TF-IDF HDBSCAN (0.1158) marginally outperforms BioBERT HDBSCAN (0.1154) and achieves superior geometric clustering quality (Silhouette 0.4786 vs. 0.4225; DBI 0.6034 vs. 0.7068). This arises because TF-IDF's sparse, high-dimensional representation preserves term co-occurrence directly — when a specialized sub-field (e.g., diabetic wound healing) produces a concentrated cluster of abstracts sharing highly domain-specific terminology, TF-IDF captures this precisely. BioBERT, while producing semantically richer embeddings, compresses diverse semantic signals into a 768-dimensional space that, before UMAP reduction, can group mechanistically similar but terminologically distinct documents, leading to clusters that are harder to separate geometrically.

The practical recommendation is therefore not to choose one representation over the other, but to employ both in parallel, using each pipeline's micro-topics for different clinical knowledge-discovery tasks: BioBERT for mechanism discovery across disease boundaries, TF-IDF for sub-population and treatment-protocol identification.

### C. Limitations of Hierarchical Agglomerative Clustering

HAC with Ward linkage consistently underperformed across all metrics in both pipelines. The Ward criterion optimizes for compact, hyperspherical clusters — an assumption poorly matched to the complex, non-convex density structures of biomedical embedding spaces. The high DBI values (TF-IDF HAC: 0.9584; BioBERT HAC: 0.8845) indicate poor separation between clusters, while the low NPMI (BioBERT HAC: 0.0598) confirms that forced hierarchical merging does not produce semantically coherent topic groups. We recommend against HAC for large-scale biomedical text clustering without additional refinement steps such as post-hoc cluster pruning or density-based boundary correction.

### D. The Role of UMAP as a Pre-Clustering Step

An important methodological choice in this study is the use of UMAP as a *pre-clustering* dimensionality reduction step rather than only for visualization. The local-neighborhood-preservation property of UMAP means that clusters formed in the 2D UMAP space correspond to genuine density structures in the original high-dimensional space [16], [20]. This choice is empirically validated by the strong NPMI coherence scores of HDBSCAN on the UMAP-projected embeddings. Future work could compare the performance of HDBSCAN directly on the 768-dimensional BioBERT space against the UMAP-projected 2D space; the present study's design intentionally uses UMAP for both pipelines to enable controlled comparison.

### E. Clinical Applicability and Limitations

The micro-topics discovered in this study are directly actionable for biomedical research triage. For example:

- **Cluster 43 (BioBERT, NPMI = 0.3220): Plasma Alzheimer's Biomarkers.** The discovery that 52 PubMed abstracts form a dense, highly coherent cluster centered on plasma phospho-tau (p-tau), glial fibrillary acidic protein (GFAP), and amyloid-beta PET markers directly identifies an active research micro-domain within Alzheimer's biomarker science. A researcher entering this sub-field could use this cluster's keyword profile as an efficient literature-retrieval query.

- **Cluster 13 (TF-IDF, NPMI = 0.3431): Diabetic Wound Healing.** This cluster consolidates literature on diabetic foot ulcer (DFU) hydrogel treatments, amputation risk, and wound-microbiome interactions — a translational sub-field that sits across endocrinology and dermatological surgery and would be difficult to capture with a broad MeSH search.

Several limitations of the present study should be acknowledged:

1. **Corpus scope.** The corpus contains 14,064 abstracts — a substantial but not exhaustive sample of PubMed literature. Coverage of additional disease domains would further test the generality of the framework.
2. **Abstracts only.** The use of abstracts limits the contextual depth available to the embedding model, compared to full-text PMC articles. This may restrict the resolution of the most mechanism-heavy micro-topics.
3. **HDBSCAN noise.** A significant proportion of documents (those labeled −1) are excluded from the micro-topic evaluation. These transitional or sparse documents may contain vital interdisciplinary insights that warrant follow-up analysis.
4. **Clinical label assignment.** The top-2-keyword label assignment is automatic and transparent, but less informative than a fully ontology-grounded label (e.g., mapped to MeSH or UMLS). A hybrid label-assignment strategy is a natural next step.
5. **Pooling choice.** The BioBERT document embedding was obtained by mean-pooling the final hidden state. Alternative pooling strategies (e.g., `[CLS]` token, attention-weighted pooling) were not systematically explored.
6. **Single-seed reporting.** Although the analysis uses fixed random seeds for full reproducibility, reporting mean ± std across multiple seeds would strengthen the statistical robustness of the K-Means and HAC results, which depend on initialization.

---

## VIII. Conclusion and Future Work

This study presented a systematic comparative evaluation of six pipeline configurations for biomedical micro-topic discovery and disease mapping, applied to a corpus of 14,064 PubMed abstracts spanning eight disease domains. The empirical results demonstrated that **density-based clustering via HDBSCAN consistently outperforms** traditional partition-based (K-Means) and hierarchical agglomerative (HAC) algorithms in NPMI topic coherence across both TF-IDF and BioBERT representation strategies. The HDBSCAN pipelines achieved relative improvements of 40.3% (BioBERT) and 48.5% (TF-IDF) over their respective K-Means baselines, with individual micro-topics reaching NPMI scores of 0.32–0.34 — high enough to be interpretable from their keyword profiles alone.

A qualitative investigation revealed that the two representation strategies are **complementary rather than competing**. BioBERT HDBSCAN excels at uncovering deep, pathway-level molecular mechanisms — alpha-synuclein aggregation kinetics, mitochondrial signaling subtypes, and gut–brain axis interactions — by capturing cross-sentence semantic relationships that bag-of-words models cannot represent. TF-IDF HDBSCAN is highly effective at identifying population-specific and clinically labeled micro-topics — diabetic wound healing, preeclampsia, antihypertensive management — by leveraging the precise term-co-occurrence signal of specialized sub-literatures. The two pipelines' Jaccard overlap on inferred clinical categories is approximately 0.30, indicating substantial complementarity.

These findings suggest that **density-based clustering over low-dimensional manifold projections, combined with biomedical-domain contextual embeddings, is a robust and generalizable framework** for automated literature synthesis and granular disease mapping. Beyond literature triage, the framework offers a starting point for hypothesis generation: the micro-topics it surfaces (e.g., the recurrent co-occurrence of p-tau, amyloid, and GFAP in BioBERT Cluster 43) point to research intersections that a human reader scanning PubMed search results may not have noticed.

**Future work** will pursue four directions. First, we plan to scale the corpus to full-text PMC articles and to longitudinal datasets, enabling the tracking of micro-topic emergence and evolution over time — for example, the rise of anti-amyloid antibody therapies in Alzheimer's research, or the explosion of long-COVID literature post-2020. Second, we will explore advanced embedding strategies, including alternative pooling methods (e.g., attention-weighted, `[CLS]`, or hierarchical), longer context windows (PubMedBERT, BioGPT, or domain-adapted longformer variants), and contrastive fine-tuning for the unsupervised clustering objective. Third, we will integrate the discovered micro-topics with standardized clinical ontologies — MeSH, ICD-11, SNOMED-CT, and the Unified Medical Language System (UMLS) — to enable automated clinical grounding, document tagging, and cross-corpus interoperability. Fourth, we will investigate semi-supervised or soft-clustering extensions of HDBSCAN that allow transitional noise-labeled documents to be assigned *partial* membership in nearby clusters, providing a more complete mapping of the biomedical literature landscape. Finally, we will release the entire pipeline as an open-source, GPU-enabled web application so that researchers without NLP expertise can apply the framework to their own corpora.

---

## Data and Code Availability

The complete experimental code, preprocessing pipeline, and evaluation scripts are available at [GitHub Repository URL]. The PubMed dataset can be reproduced exactly by running the provided API retrieval script (`API.ipynb`) with the documented queries and date range. Pre-trained BioBERT weights are downloaded automatically from the Hugging Face model hub (`dmis-lab/biobert-v1.1`). No patient-identifiable information was used; all data are from the public PubMed database under the NCBI data-access policy.

---

## Acknowledgments

[To be added at submission. Suggested acknowledgments: funding agency, GPU resource provider, advisor, etc.]

---

## References

[1] J. Lee, W. Yoon, S. Kim, D. Kim, S. Kim, C. H. So, and J. Kang, "BioBERT: a pre-trained biomedical language representation model for biomedical text mining," *Bioinformatics*, vol. 36, no. 4, pp. 1234–1240, Feb. 2020, doi: 10.1093/bioinformatics/btz682.

[2] S. Kumar and T. Basu, "AdaBioBERT: adaptive token sequence learning for biomedical named entity recognition," in *Proc. 24th Workshop Biomed. Lang. Process. (BioNLP 2025)*, Bangkok, Thailand, Aug. 2025, pp. 56–62.

[3] Y. Peng, S. Yan, and Z. Lu, "Transfer learning in biomedical natural language processing: an evaluation of BERT and ELMo on ten benchmarking datasets," in *Proc. BioNLP 2019 Workshop*, Florence, Italy, Aug. 2019, pp. 58–65.

[4] Y. Peng, Q. Chen, and Z. Lu, "An empirical study of multi-task learning on BERT for biomedical text mining," in *Proc. BioNLP 2020 Workshop*, Online, Jul. 2020, pp. 205–214.

[5] S. Alrowili and K. Vijay-Shanker, "BioM-Transformers: building large biomedical language models with BERT, ALBERT and ELECTRA," in *Proc. BioNLP 2021 Workshop*, Online, Jun. 2021, pp. 221–227.

[6] D. Vithanage, P. Yu, L. Wang, and C. Deng, "Contextual word embedding for biomedical knowledge extraction: a rapid review and case study," *J. Healthcare Inform. Res.*, vol. 8, no. 1, pp. 158–179, Jan. 2024, doi: 10.1007/s41666-023-00157-y.

[7] S. Sharaf and V. S. Anoop, "An analysis on large language models in healthcare: a case study of BioBERT," *arXiv:2310.07282 [cs.AI]*, Oct. 2023.

[8] D. Grissa, A. Junge, T. I. Oprea, and L. J. Jensen, "DISEASES 2.0: a weekly updated database of disease–gene associations from text mining and data integration," *Database*, vol. 2022, Art. no. baac019, Mar. 2022, doi: 10.1093/database/baac019.

[9] J. Xu, S. Kim, M. Song, M. Jeong, D. Kim, J. Kang, et al., "Building a PubMed knowledge graph," *Sci. Data*, vol. 7, no. 1, Art. no. 205, Jun. 2020, doi: 10.1038/s41597-020-0543-2.

[10] A. D. Diaz Gonzalez, S. Yue, S. T. Hayes, and K. S. Hughes, "Applying BioBERT to extract germline gene-disease associations for building a knowledge graph from the biomedical literature," in *Proc. 7th Int. Conf. Inf. Syst. Data Mining (ICISDM '23)*, Atlanta, GA, USA, May 2023, 6 pages, doi: 10.1145/3603765.3603771.

[11] P.-H. Li, Y.-Y. Sun, H.-F. Juan, and C.-Y. Chen, "A large language model framework for literature-based disease–gene association prediction," *Briefings Bioinform.*, vol. 26, no. 1, Art. no. bbaf070, Feb. 2025, doi: 10.1093/bib/bbaf070.

[12] Z. Zhang, N. Parulian, H. Ji, A. S. Elsayed, S. Myers, and M. Palmer, "Fine-grained information extraction from biomedical literature based on knowledge-enriched abstract meaning representation," in *Proc. 59th Annu. Meeting Assoc. Comput. Linguist. 11th Int. Joint Conf. Nat. Lang. Process. (ACL-IJCNLP 2021)*, Online, Aug. 2021, pp. 6261–6270.

[13] S. Masoumi, H. Amirkhani, N. Sadeghian, and S. Shahraz, "Natural language processing (NLP) to facilitate abstract review in medical research: the application of BioBERT to exploring the 20-year use of NLP in medical research," *Syst. Rev.*, vol. 13, no. 1, Art. no. 107, 2024, doi: 10.1186/s13643-024-02470-y.

[14] Y.-N. Chuang, G. Wang, C.-Y. Chang, K.-H. Lai, D. Zha, R. Tang, et al., "DiscoverPath: a knowledge refinement and retrieval system for interdisciplinarity on biomedical research," in *Proc. 32nd ACM Int. Conf. Inf. Knowl. Manage. (CIKM '23)*, Birmingham, U.K., Oct. 2023, 5 pages, doi: 10.1145/3583780.3614739.

[15] K. Davagdorj, L. Wang, M. Li, V.-H. Pham, K. H. Ryu, and N. Theera-Umpon, "Discovering thematically coherent biomedical documents using contextualized bidirectional encoder representations from transformers-based clustering," *Int. J. Environ. Res. Public Health*, vol. 19, no. 10, Art. no. 5893, May 2022, doi: 10.3390/ijerph19105893.

[16] L. McInnes, J. Healy, and J. Melville, "UMAP: Uniform Manifold Approximation and Projection for dimension reduction," *arXiv:1802.03426 [stat.ML]*, 2018.

[17] M. Grootendorst, "BERTopic: neural topic modeling with a class-based TF-IDF procedure," *arXiv:2203.05794 [cs.CL]*, Mar. 2022.

[18] A. Munoz-Farre, A. Poulakakis-Daktylidis, D. M. Kothalawala, and A. Rodriguez-Martinez, "Interpreting deep embeddings for disease progression clustering," *arXiv:2307.06060 [stat.ML]*, Jul. 2023.

[19] N. Oubenali, S. Messaoud, A. Filiot, A. Lamer, and P. Andrey, "Visualization of medical concepts represented using word embeddings: a scoping review," *BMC Med. Inform. Decis. Mak.*, vol. 22, no. 1, Art. no. 83, Mar. 2022, doi: 10.1186/s12911-022-01822-9.

[20] S. S. Panesar, "Biomedical knowledge discovery from unstructured text corpora using contextual word embeddings," *Research Square*, preprint, Nov. 2022, doi: 10.21203/rs.3.rs-2286334/v1.

[21] D. M. Blei, A. Y. Ng, and M. I. Jordan, "Latent Dirichlet allocation," *J. Mach. Learn. Res.*, vol. 3, pp. 993–1022, 2003.

[22] R. J. G. B. Campello, D. Moulavi, and J. Sander, "Density-based clustering based on hierarchical density estimates," in *Proc. PAKDD*, Gold Coast, Australia, 2013, pp. 160–172.

[23] P. J. Rousseeuw, "Silhouettes: a graphical aid to interpretation and validation of cluster analysis," *J. Comput. Appl. Math.*, vol. 20, pp. 53–65, 1987.

[24] D. Mimno, H. Wallach, E. Talley, M. Leenders, and A. McCallum, "Optimizing semantic coherence in topic models," in *Proc. EMNLP*, Edinburgh, UK, 2011, pp. 262–272.

[25] D. L. Davies and D. W. Bouldin, "A cluster separation measure," *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. 1, no. 2), pp. 224–227, 1979.

[26] A. Cockayne, *Biopython: freely available Python tools for computational molecular biology and bioinformatics*, *Bioinformatics*, vol. 25, no. 11, pp. 1422–1423, 2009.

[27] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, "BERT: pre-training of deep bidirectional transformers for language understanding," in *Proc. NAACL-HLT*, Minneapolis, MN, USA, Jun. 2019, pp. 4171–4186.

[28] D. D. Lee and H. S. Seung, "Learning the parts of objects by non-negative matrix factorization," *Nature*, vol. 401, pp. 788–791, 1999.

[29] F. Pedregosa *et al.*, "Scikit-learn: machine learning in Python," *J. Mach. Learn. Res.*, vol. 12, pp. 2825–2830, 2011.

[30] A. Paszke *et al.*, "PyTorch: an imperative style, high-performance deep learning library," in *Proc. NeurIPS*, Vancouver, BC, Canada, 2019, pp. 8024–8035.

---

## Appendix A: Supplementary Figures (File Inventory)

For reproducibility and reviewer convenience, the complete set of figures generated by the pipeline is summarized below. All files are released with the manuscript.

| # | File Path                                            | Section | Caption Summary                                           |
|---|------------------------------------------------------|---------|-----------------------------------------------------------|
| A1 | `BioBERT Results/step1_raw_length_distribution.png`  | III.C   | Raw abstract word-count distribution                     |
| A2 | `BioBERT Results/step2_preprocessing_stats.png`      | III.C   | Cleaned abstract token-count distribution                |
| A3 | `BioBERT Results/step3_biobert_correlation.png`      | IV.A    | First-50-dimension correlation heatmap of BioBERT space  |
| A4 | `BioBERT Results/step4_inter_concept_similarity.png` | VI.B   | Inter-anchor cosine similarity heatmap (BioBERT)          |
| A5 | `TF-IDF Results/step4_inter_concept_similarity.png`  | VI.B   | Inter-anchor cosine similarity heatmap (TF-IDF)           |
| A6 | `BioBERT Results/step5_umap2d_unlabeled.png`         | IV.A    | Unsupervised 2D UMAP projection of BioBERT embeddings    |
| A7 | `TF-IDF Results/step5_umap2d_unlabeled.png`          | IV.A    | Unsupervised 2D UMAP projection of TF-IDF embeddings     |
| A8 | `BioBERT Results/step6a_automated_elbow_method.png`  | IV.C    | Elbow curve for K-Means K selection (BioBERT)            |
| A9 | `TF-IDF Results/step6a_automated_elbow_method.png`   | IV.C    | Elbow curve for K-Means K selection (TF-IDF)             |
| A10 | `BioBERT Results/step6b_cluster_umap_all.png`       | IV.C    | K-Means, HDBSCAN, HAC overlay (BioBERT)                  |
| A11 | `TF-IDF Results/step6b_cluster_umap_all.png`        | IV.C    | K-Means, HDBSCAN, HAC overlay (TF-IDF)                   |
| A12 | `BioBERT Results/step7_topic_keywords_grid.png`      | IV.D    | Top keywords per K-Means cluster (BioBERT)               |
| A13 | `TF-IDF Results/step7_topic_keywords_grid.png`       | IV.D    | Top keywords per K-Means cluster (TF-IDF)                |
| A14 | `BioBERT Results/step8_evaluation_metrics.png`      | VI.A    | Silhouette and DBI bar charts (BioBERT)                  |
| A15 | `TF-IDF Results/step8_evaluation_metrics.png`       | VI.A    | Silhouette and DBI bar charts (TF-IDF)                   |
| A16 | `Coherence Results/coherence_per_topic_boxplot.png` | VI.A    | Per-topic NPMI coherence boxplot across all 6 pipelines   |
| A17 | `Coherence Results/coherence_grouped_bar.png`       | VI.A    | Grouped bar chart of mean NPMI across all 6 pipelines    |
| A18 | `Coherence Results/coherence_heatmap.png`           | VI.A    | Heatmap of NPMI coherence across all 6 pipelines         |
| A19 | `Coherence Results/combined_metrics_table.png`      | VI.A    | Combined metrics table (Silhouette, DBI, NPMI)            |
| A20 | `BioBERT Results/step9_cluster_keywords.png`        | VI.D    | Top keywords per HDBSCAN micro-cluster (BioBERT)         |
| A21 | `TF-IDF Results/step9_cluster_keywords.png`         | VI.D    | Top keywords per HDBSCAN micro-cluster (TF-IDF)          |
| A22 | `BioBERT Results/step10_disease_knowledge_mapping.png` | IV.E | K-Means disease label table (BioBERT)                    |
| A23 | `TF-IDF Results/step10_disease_knowledge_mapping.png` | IV.E  | K-Means disease label table (TF-IDF)                     |
| A24 | `BioBERT Results/step11_final_mapped_umap_all_algorithms.png` | IV.E | UMAP with K-Means disease labels (BioBERT)        |
| A25 | `TF-IDF Results/step11_final_mapped_umap_all_algorithms.png` | IV.E | UMAP with K-Means disease labels (TF-IDF)            |
| A26 | `Manuscript Results/Table1_Macro_KMeans.png`         | VI.C    | Publication-ready macro-level K-Means table              |
| A27 | `Manuscript Results/Table2_Micro_HDBSCAN.png`        | VI.D    | Publication-ready top-10 HDBSCAN micro-topics table      |
| A28 | `Manuscript Results/Figure1_HDBSCAN_vs_KMeans_Coherence.png` | VI.D | HDBSCAN top-10 vs. K-Means mean NPMI comparison         |
