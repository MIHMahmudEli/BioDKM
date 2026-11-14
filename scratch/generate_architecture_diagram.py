import os
import subprocess

tex_code = r'''\documentclass[tikz,border=16pt]{standalone}
\usepackage{xcolor}
\usepackage{amsmath,amssymb}
\usepackage{microtype}
\usetikzlibrary{shapes,arrows.meta,positioning,calc,fit,backgrounds}

% ─── Color Palette (Publication Grade / Academic) ───────────────────────────
\definecolor{headerNavy}{RGB}{15, 23, 42}
\definecolor{cardBorder}{RGB}{203, 213, 225}
\definecolor{busGray}{RGB}{71, 85, 105}
\definecolor{textDark}{RGB}{30, 41, 59}
\definecolor{textMuted}{RGB}{100, 116, 139}

% Stage 1: Acquisition (Teal)
\definecolor{cTealBorder}{RGB}{13, 148, 136}
\definecolor{cTealBg}{RGB}{240, 253, 250}
\definecolor{cTealBadge}{RGB}{15, 118, 110}

% Stage 2: Preprocessing (Slate)
\definecolor{cSlateBorder}{RGB}{71, 85, 105}
\definecolor{cSlateBg}{RGB}{248, 250, 252}
\definecolor{cSlateBadge}{RGB}{51, 65, 85}

% Stage 3: Extraction (Cobalt)
\definecolor{cBlueBorder}{RGB}{37, 99, 235}
\definecolor{cBlueBg}{RGB}{239, 246, 255}
\definecolor{cBlueBadge}{RGB}{29, 78, 216}

% Stage 4: Projection (Amber)
\definecolor{cAmberBorder}{RGB}{217, 119, 6}
\definecolor{cAmberBg}{RGB}{255, 251, 235}
\definecolor{cAmberBadge}{RGB}{180, 83, 9}

% Stage 5: Clustering (Emerald)
\definecolor{cGreenBorder}{RGB}{16, 185, 129}
\definecolor{cGreenBg}{RGB}{236, 253, 245}
\definecolor{cGreenBadge}{RGB}{5, 150, 105}

% Stage 6: Interpretation (Purple)
\definecolor{cPurpleBorder}{RGB}{139, 92, 246}
\definecolor{cPurpleBg}{RGB}{245, 243, 255}
\definecolor{cPurpleBadge}{RGB}{109, 40, 217}

% Stage 7: Validation (Rose)
\definecolor{cRoseBorder}{RGB}{225, 29, 72}
\definecolor{cRoseBg}{RGB}{255, 241, 242}
\definecolor{cRoseBadge}{RGB}{190, 18, 60}

\begin{document}
\begin{tikzpicture}[
  font=\sffamily,
  >=Stealth,
  % Card Base Style
  card/.style={
    draw=#1Border,
    fill=#1Bg,
    line width=0.9pt,
    rounded corners=6pt,
    align=center,
    inner sep=6pt,
    text=textDark
  },
  % Sub-card style (white inner boxes)
  subcard/.style={
    draw=#1Border!75,
    fill=white,
    line width=0.7pt,
    rounded corners=4pt,
    align=center,
    inner sep=5pt,
    text=textDark
  },
  % Centered Stage Badge Style
  badge/.style={
    draw=#1Border!95,
    fill=#1Badge,
    text=white,
    font=\sffamily\bfseries\tiny,
    rounded corners=3pt,
    inner sep=3.5pt,
    anchor=center
  },
  % Orthogonal Bus Styles
  bus/.style={
    line width=1.3pt,
    draw=busGray
  },
  branch/.style={
    -{Stealth[length=4.5pt, width=3.5pt]},
    line width=0.9pt,
    draw=busGray
  },
  junc/.style={
    circle,
    fill=busGray,
    inner sep=0pt,
    minimum size=3.8pt
  }
]

% ─── TITLE BANNER ──────────────────────────────────────────────────────────
\node[draw=headerNavy!80, fill=white, line width=1.1pt, rounded corners=6pt, text width=262mm, align=center, inner sep=6pt] (titleBanner) {
  {\fontsize{13pt}{15pt}\selectfont\textbf{\color{headerNavy}UNSUPERVISED BIOMEDICAL DISEASE KNOWLEDGE MAPPING FRAMEWORK}}\\[2pt]
  {\fontsize{8pt}{10pt}\selectfont\color{textMuted}\textit{Unified Comparative Architecture: Topological Manifold Clustering with Sparse \& Contextual Transformers}}
};

% ─── ROW 1: ACQUISITION & PREPROCESSING ─────────────────────────────────────
\node[card=cTeal, text width=125mm, minimum height=24mm, below=12mm of titleBanner.south west, anchor=north west] (cStage1) {
  \vspace{2mm}\\
  {\fontsize{9pt}{11pt}\selectfont\textbf{NCBI Entrez E-Utilities Data Acquisition Engine}}\\[2pt]
  {\fontsize{7.5pt}{9.5pt}\selectfont Automated retrieval across 8 clinical disease queries ($N = 14{,}065$ abstracts fetched)}\\[2pt]
  {\fontsize{6.8pt}{8.5pt}\selectfont\color{textMuted} Neoplasm (1,951) $\cdot$ Diabetes (1,922) $\cdot$ Stroke (1,880) $\cdot$ Alzheimer's (1,753) $\cdot$ Hypertension (1,747) $\cdot$ CVD (1,722) $\cdot$ Neuro (1,586) $\cdot$ Parkinson's (1,504)}
};
\node[badge=cTeal] at (cStage1.north) {STAGE 1: CORPUS ACQUISITION};

\node[card=cSlate, text width=125mm, minimum height=24mm, below=12mm of titleBanner.south east, anchor=north east] (cStage2) {
  \vspace{2mm}\\
  {\fontsize{9pt}{11pt}\selectfont\textbf{Biomedical Text Standardization \& Cleaning Pipeline}}\\[2pt]
  {\fontsize{7.5pt}{9.5pt}\selectfont Lowercase normalisation $\cdot$ Regex non-alphabetic filtering ($[\text{\textasciicircum a-zA-Z}\backslash\text{s}]$) $\cdot$ NLTK tokenisation}\\[2pt]
  {\fontsize{6.8pt}{8.5pt}\selectfont\color{textMuted} Biomedical stop-word removal $\cdot$ Length thresholding ($\text{len} > 2$) $\cdot$ Strict deduplication $\rightarrow$ \textbf{14{,}064 Verified Documents}}
};
\node[badge=cSlate] at (cStage2.north) {STAGE 2: BIOMEDICAL TEXT PREPROCESSING};

% Connect Stage 1 -> Stage 2
\draw[branch] (cStage1.east) -- (cStage2.west);

% ─── ROW 2: MULTI-REPRESENTATION EXTRACTION ─────────────────────────────────
\coordinate (r2Center) at ($(titleBanner.south) + (0, -76mm)$);

\node[subcard=cBlue, text width=58mm, minimum height=30mm] at ($(r2Center) + (-97.5mm, 0)$) (c3a) {
  {\fontsize{8.5pt}{10.5pt}\selectfont\textbf{3a. Sparse TF-IDF Vectorizer}}\\[2pt]
  {\fontsize{7pt}{8.5pt}\selectfont Term Salience \& Inverse Doc Frequency}\\[2pt]
  {\fontsize{6.5pt}{8pt}\selectfont\color{textMuted} $\text{vocab} = 5{,}000$ (unigram + bigram)\\[1pt] $\text{min\_df} = 5, \text{max\_df} = 0.90$\\[1pt] Output: $\mathbf{X} \in \mathbb{R}^{14{,}064 \times 5{,}000}$ ($\ell_2$-norm)}
};

\node[subcard=cBlue, text width=58mm, minimum height=30mm] at ($(r2Center) + (-32.5mm, 0)$) (c3b) {
  {\fontsize{8.5pt}{10.5pt}\selectfont\textbf{3b. BioBERT v1.1 Encoder}}\\[2pt]
  {\fontsize{7pt}{8.5pt}\selectfont PubMed + PMC Continual Pretraining}\\[2pt]
  {\fontsize{6.5pt}{8pt}\selectfont\color{textMuted} 12-layer, 768-d Contextual BERT\\[1pt] Attention-masked mean pooling\\[1pt] Output: $\mathbf{X} \in \mathbb{R}^{14{,}064 \times 768}$ ($\ell_2$-norm)}
};

\node[subcard=cBlue, text width=58mm, minimum height=30mm] at ($(r2Center) + (32.5mm, 0)$) (c3c) {
  {\fontsize{8.5pt}{10.5pt}\selectfont\textbf{3c. Scientific BERT Encoders}}\\[2pt]
  {\fontsize{7pt}{8.5pt}\selectfont Domain-Specific Scratch / Multi-Domain}\\[2pt]
  {\fontsize{6.5pt}{8pt}\selectfont\color{textMuted} \textbf{PubMedBERT}: 768-d from scratch\\[1pt] \textbf{SciBERT}: 768-d scientific \textit{scivocab}\\[1pt] Attention-masked pooling ($\ell_2$-norm)}
};

\node[subcard=cBlue, text width=58mm, minimum height=30mm] at ($(r2Center) + (97.5mm, 0)$) (c3d) {
  {\fontsize{8.5pt}{10.5pt}\selectfont\textbf{3d. Sentence-Transformer}}\\[2pt]
  {\fontsize{7pt}{8.5pt}\selectfont Contrastive Bi-Encoder Architecture}\\[2pt]
  {\fontsize{6.5pt}{8pt}\selectfont\color{textMuted} \textbf{all-MiniLM-L6-v2}: 384-d dense\\[1pt] 1B+ sentence pair contrastive training\\[1pt] Direct semantic textual similarity}
};

% Enclosing Stage 3 container with generous header space
\begin{scope}[on background layer]
  \node[card=cBlue, inner xsep=6pt, inner ysep=10pt, yshift=3mm, fit=(c3a) (c3d)] (boxStage3) {};
\end{scope}
\node[badge=cBlue] at (boxStage3.north) {STAGE 3: MULTI-REPRESENTATION EXTRACTION};

% ─── ROW 3: DIAGNOSTIC & TOPOLOGICAL REDUCTION ──────────────────────────────
\coordinate (r3Center) at ($(titleBanner.south) + (0, -128mm)$);

\node[card=cAmber, text width=125mm, minimum height=24mm] at ($(r3Center) + (-65.5mm, 0)$) (c4a) {
  \vspace{2mm}\\
  {\fontsize{9pt}{11pt}\selectfont\textbf{Centroid Diagnostic Analysis (Exploratory Separability)}}\\[2pt]
  {\fontsize{7.5pt}{9.5pt}\selectfont $K = 10$ pseudo-class partitioning $\cdot$ Centroid vectors $\boldsymbol{\mu}_c = \frac{1}{|P_c|}\sum_{d \in P_c}\mathbf{E}_d$}\\[2pt]
  {\fontsize{6.8pt}{8.5pt}\selectfont\color{textMuted} Pairwise centroid cosine similarity matrix $\cdot$ Verification of embedding space modularity}
};
\node[badge=cAmber] at (c4a.north) {STAGE 4A: CENTROID DIAGNOSTICS};

\node[card=cAmber, text width=125mm, minimum height=24mm] at ($(r3Center) + (65.5mm, 0)$) (c4b) {
  \vspace{2mm}\\
  {\fontsize{9pt}{11pt}\selectfont\textbf{Topological Manifold Projection \& Dimensionality Ablation}}\\[2pt]
  {\fontsize{7.5pt}{9.5pt}\selectfont UMAP 2D Manifold Approximation: Fuzzy simplicial cross-entropy minimization ($\text{cosine}, k{=}15$)}\\[2pt]
  {\fontsize{6.8pt}{8.5pt}\selectfont\color{textMuted} Full Ablation: High-Dim vs. PCA (50D/2D) vs. UMAP 2D $\cdot$ Trustworthiness preservation score $T(k) = 0.982$}
};
\node[badge=cAmber] at (c4b.north) {STAGE 4B: TOPOLOGICAL MANIFOLD PROJECTION};

% ─── ROW 4: CLUSTERING & BASELINES ──────────────────────────────────────────
\coordinate (r4Center) at ($(titleBanner.south) + (0, -180mm)$);

\node[subcard=cGreen, text width=58mm, minimum height=28mm] at ($(r4Center) + (-97.5mm, 0)$) (c5a) {
  {\fontsize{8.5pt}{10.5pt}\selectfont\textbf{5a. HDBSCAN Density}}\\[2pt]
  {\fontsize{7pt}{8.5pt}\selectfont Hierarchical Density Clustering}\\[2pt]
  {\fontsize{6.5pt}{8pt}\selectfont\color{textMuted} Mutual reachability distance\\[1pt] Minimum spanning tree condensation\\[1pt] \textbf{80--116 Fine-grained Topics + Noise}}
};

\node[subcard=cGreen, text width=58mm, minimum height=28mm] at ($(r4Center) + (-32.5mm, 0)$) (c5b) {
  {\fontsize{8.5pt}{10.5pt}\selectfont\textbf{5b. KMeans Partitioning}}\\[2pt]
  {\fontsize{7pt}{8.5pt}\selectfont Centroid Distance Optimization}\\[2pt]
  {\fontsize{6.5pt}{8pt}\selectfont\color{textMuted} Spherical Voronoi tessellation\\[1pt] Automated Elbow \& Silhouette sweep\\[1pt] \textbf{Optimal $K = 5$ Macro Categories}}
};

\node[subcard=cGreen, text width=58mm, minimum height=28mm] at ($(r4Center) + (32.5mm, 0)$) (c5c) {
  {\fontsize{8.5pt}{10.5pt}\selectfont\textbf{5c. Agglomerative Hier.}}\\[2pt]
  {\fontsize{7pt}{8.5pt}\selectfont Bottom-up Dendrogram Clustering}\\[2pt]
  {\fontsize{6.5pt}{8pt}\selectfont\color{textMuted} Ward minimum variance linkage\\[1pt] Pairwise Euclidean metric\\[1pt] \textbf{Hierarchical Tree Cut ($K = 5$)}}
};

\node[subcard=cGreen, text width=58mm, minimum height=28mm] at ($(r4Center) + (97.5mm, 0)$) (c5d) {
  {\fontsize{8.5pt}{10.5pt}\selectfont\textbf{5d. Literature Baselines}}\\[2pt]
  {\fontsize{7pt}{8.5pt}\selectfont Classical \& Neural Benchmarks}\\[2pt]
  {\fontsize{6.5pt}{8pt}\selectfont\color{textMuted} \textbf{LDA}: Latent Dirichlet Allocation\\[1pt] \textbf{BERTopic}: Transformer + HDBSCAN\\[1pt] Rigorous cross-paradigm benchmark}
};

% Enclosing Stage 5 container with generous header space
\begin{scope}[on background layer]
  \node[card=cGreen, inner xsep=6pt, inner ysep=10pt, yshift=3mm, fit=(c5a) (c5d)] (boxStage5) {};
\end{scope}
\node[badge=cGreen] at (boxStage5.north) {STAGE 5: CLUSTERING \& BASELINES};

% ─── ROW 5: TOPIC INTERPRETATION ───────────────────────────────────────────
\coordinate (r5Center) at ($(titleBanner.south) + (0, -226mm)$);

\node[card=cPurple, text width=258mm, minimum height=22mm] at (r5Center) (cStage6) {
  \vspace{2mm}\\
  {\fontsize{9pt}{11pt}\selectfont\textbf{Topic Semantic Interpretation \& Complete Noise Partition Allocation}}\\[2pt]
  {\fontsize{7.5pt}{9.5pt}\selectfont Class-based TF-IDF ($c\text{-TF-IDF}$): $W_{t,c} = \frac{tf_{t,c}}{tf_c} \cdot \log\left(1 + \frac{A}{tf_t}\right)$ $\cdot$ Automated Title-Case Clinical Label Synthesis}\\[2pt]
  {\fontsize{6.8pt}{8.5pt}\selectfont\color{textMuted} Soft $k$-NN classification protocol for noise boundary papers $\rightarrow$ Guaranteed 100\% complete corpus document assignment}
};
\node[badge=cPurple] at (cStage6.north) {STAGE 6: TOPIC SEMANTIC INTERPRETATION \& NOISE RE-ALLOCATION};

% ─── ROW 6: MULTI-PILLAR EMPIRICAL VALIDATION SUITE ────────────────────────
\coordinate (r6Center) at ($(titleBanner.south) + (0, -274mm)$);

\node[subcard=cRose, text width=38.5mm, minimum height=28mm] at ($(r6Center) + (-108mm, 0)$) (c7a) {
  {\fontsize{8pt}{9.5pt}\selectfont\textbf{7a. Intrinsic Quality}}\\[2pt]
  {\fontsize{6.8pt}{8pt}\selectfont Silhouette (0.4786)\\[1pt] Davies-Bouldin (0.6034)\\[1pt] Calinski-Harabasz\\[1pt] Matched-Core Ablation}
};

\node[subcard=cRose, text width=38.5mm, minimum height=28mm] at ($(r6Center) + (-64.8mm, 0)$) (c7b) {
  {\fontsize{8pt}{9.5pt}\selectfont\textbf{7b. Semantic Purity}}\\[2pt]
  {\fontsize{6.8pt}{8pt}\selectfont NPMI Coherence (0.1158)\\[1pt] Word Intrusion (98.55\%)\\[1pt] Purity Margin (+0.145)\\[1pt] 207 Topics Evaluated}
};

\node[subcard=cRose, text width=38.5mm, minimum height=28mm] at ($(r6Center) + (-21.6mm, 0)$) (c7c) {
  {\fontsize{8pt}{9.5pt}\selectfont\textbf{7c. Disease Alignment}}\\[2pt]
  {\fontsize{6.8pt}{8pt}\selectfont Adjusted Rand Index (ARI)\\[1pt] Normalized MI (NMI)\\[1pt] Cluster Purity\\[1pt] Ground-Truth Matrix}
};

\node[subcard=cRose, text width=38.5mm, minimum height=28mm] at ($(r6Center) + (21.6mm, 0)$) (c7d) {
  {\fontsize{8pt}{9.5pt}\selectfont\textbf{7d. MeSH Grounding}}\\[2pt]
  {\fontsize{6.8pt}{8pt}\selectfont 2024 NLM MeSH Tree\\[1pt] Depths 1--8 Alignment\\[1pt] Granular Depths 4--6\\[1pt] Taxonomic Validation}
};

\node[subcard=cRose, text width=38.5mm, minimum height=28mm] at ($(r6Center) + (64.8mm, 0)$) (c7e) {
  {\fontsize{8pt}{9.5pt}\selectfont\textbf{7e. Comorbidity Net}}\\[2pt]
  {\fontsize{6.8pt}{8pt}\selectfont Unsupervised Cosine Net\\[1pt] Cardiovasc-Stroke 0.812\\[1pt] Alzheimer-Stroke 0.782\\[1pt] Cross-Disease Bridges}
};

\node[subcard=cRose, text width=38.5mm, minimum height=28mm] at ($(r6Center) + (108mm, 0)$) (c7f) {
  {\fontsize{8pt}{9.5pt}\selectfont\textbf{7f. Scalability/Stab.}}\\[2pt]
  {\fontsize{6.8pt}{8pt}\selectfont 10-Fold Perturb. ($0.750$)\\[1pt] Near-Linear ($\alpha = 0.326$)\\[1pt] $16.5\times$ Faster vs BERTopic\\[1pt] 451 docs/sec Throughput}
};

% Enclosing Stage 7 container with generous header space
\begin{scope}[on background layer]
  \node[card=cRose, inner xsep=6pt, inner ysep=11pt, yshift=4mm, fit=(c7a) (c7f)] (boxStage7) {};
\end{scope}
\node[badge=cRose] at (boxStage7.north) {STAGE 7: MULTI-PILLAR EMPIRICAL VALIDATION SUITE};

% ─── ORTHOGONAL BUS ROUTING & INTERCONNECTS ─────────────────────────────────

% Bus 1: Stage 2 -> Stage 3 (Centered trunk entry into Stage 3, internal bus)
\coordinate (bus1Center) at ($(cStage2.south)!0.5!(boxStage3.north)$);

\draw[bus] (cStage2.south) -- (cStage2.south |- bus1Center) -- (titleBanner.center |- bus1Center);
\draw[branch] (titleBanner.center |- bus1Center) -- (boxStage3.north);
\node[junc] at (cStage2.south) {};
\node[junc] at (cStage2.south |- bus1Center) {};
\node[junc] at (titleBanner.center |- bus1Center) {};

% Internal distribution bus inside Stage 3
\coordinate (bus3In) at ($(boxStage3.north)!0.55!(c3b.north)$);
\draw[bus] (boxStage3.north) -- (titleBanner.center |- bus3In);
\draw[bus] (c3a.north |- bus3In) -- (c3d.north |- bus3In);

\node[junc] at (titleBanner.center |- bus3In) {};
\node[junc] at (c3a.north |- bus3In) {};
\node[junc] at (c3b.north |- bus3In) {};
\node[junc] at (c3c.north |- bus3In) {};
\node[junc] at (c3d.north |- bus3In) {};

\draw[branch] (c3a.north |- bus3In) -- (c3a.north);
\draw[branch] (c3b.north |- bus3In) -- (c3b.north);
\draw[branch] (c3c.north |- bus3In) -- (c3c.north);
\draw[branch] (c3d.north |- bus3In) -- (c3d.north);

% Bus 2: Stage 3 -> Stage 4 (Collection -> Distribution to 4a & 4b)
\coordinate (bus2Y) at ($(boxStage3.south)!0.5!(c4a.north)$);

\draw[bus] (c3a.south) -- (c3a.south |- bus2Y);
\draw[bus] (c3b.south) -- (c3b.south |- bus2Y);
\draw[bus] (c3c.south) -- (c3c.south |- bus2Y);
\draw[bus] (c3d.south) -- (c3d.south |- bus2Y);
\draw[bus] (c3a.south |- bus2Y) -- (c3d.south |- bus2Y);

\node[junc] at (c3a.south |- bus2Y) {};
\node[junc] at (c3b.south |- bus2Y) {};
\node[junc] at (c3c.south |- bus2Y) {};
\node[junc] at (c3d.south |- bus2Y) {};
\node[junc] at (c4a.north |- bus2Y) {};
\node[junc] at (c4b.north |- bus2Y) {};

\draw[branch] (c4a.north |- bus2Y) -- (c4a.north);
\draw[branch] (c4b.north |- bus2Y) -- (c4b.north);

% Bus 3: Stage 4 -> Stage 5 (Collection into central trunk, internal bus)
\coordinate (bus3CollectY) at ($(c4a.south)!0.5!(boxStage5.north)$);

\draw[bus] (c4a.south) -- (c4a.south |- bus3CollectY);
\draw[bus] (c4b.south) -- (c4b.south |- bus3CollectY);
\draw[bus] (c4a.south |- bus3CollectY) -- (c4b.south |- bus3CollectY);
\draw[branch] (titleBanner.center |- bus3CollectY) -- (boxStage5.north);

\node[junc] at (c4a.south |- bus3CollectY) {};
\node[junc] at (c4b.south |- bus3CollectY) {};
\node[junc] at (titleBanner.center |- bus3CollectY) {};

% Internal distribution bus inside Stage 5
\coordinate (bus5In) at ($(boxStage5.north)!0.55!(c5b.north)$);
\draw[bus] (boxStage5.north) -- (titleBanner.center |- bus5In);
\draw[bus] (c5a.north |- bus5In) -- (c5d.north |- bus5In);

\node[junc] at (titleBanner.center |- bus5In) {};
\node[junc] at (c5a.north |- bus5In) {};
\node[junc] at (c5b.north |- bus5In) {};
\node[junc] at (c5c.north |- bus5In) {};
\node[junc] at (c5d.north |- bus5In) {};

\draw[branch] (c5a.north |- bus5In) -- (c5a.north);
\draw[branch] (c5b.north |- bus5In) -- (c5b.north);
\draw[branch] (c5c.north |- bus5In) -- (c5c.north);
\draw[branch] (c5d.north |- bus5In) -- (c5d.north);

% Bus 4: Stage 5 -> Stage 6 (Merge into wide card)
\coordinate (bus4Y) at ($(boxStage5.south)!0.5!(cStage6.north)$);

\draw[bus] (c5a.south) -- (c5a.south |- bus4Y);
\draw[bus] (c5b.south) -- (c5b.south |- bus4Y);
\draw[bus] (c5c.south) -- (c5c.south |- bus4Y);
\draw[bus] (c5d.south) -- (c5d.south |- bus4Y);
\draw[bus] (c5a.south |- bus4Y) -- (c5d.south |- bus4Y);

\node[junc] at (c5a.south |- bus4Y) {};
\node[junc] at (c5b.south |- bus4Y) {};
\node[junc] at (c5c.south |- bus4Y) {};
\node[junc] at (c5d.south |- bus4Y) {};
\node[junc] at (titleBanner.center |- bus4Y) {};

\draw[branch] (titleBanner.center |- bus4Y) -- (cStage6.north);

% Bus 5: Stage 6 -> Stage 7 (Central trunk into Stage 7, internal bus)
\draw[branch] (cStage6.south) -- (boxStage7.north);
\node[junc] at (cStage6.south) {};

% Internal distribution bus inside Stage 7
\coordinate (bus7In) at ($(boxStage7.north)!0.55!(c7c.north)$);
\draw[bus] (boxStage7.north) -- (titleBanner.center |- bus7In);
\draw[bus] (c7a.north |- bus7In) -- (c7f.north |- bus7In);

\node[junc] at (titleBanner.center |- bus7In) {};
\node[junc] at (c7a.north |- bus7In) {};
\node[junc] at (c7b.north |- bus7In) {};
\node[junc] at (c7c.north |- bus7In) {};
\node[junc] at (c7d.north |- bus7In) {};
\node[junc] at (c7e.north |- bus7In) {};
\node[junc] at (c7f.north |- bus7In) {};

\draw[branch] (c7a.north |- bus7In) -- (c7a.north);
\draw[branch] (c7b.north |- bus7In) -- (c7b.north);
\draw[branch] (c7c.north |- bus7In) -- (c7c.north);
\draw[branch] (c7d.north |- bus7In) -- (c7d.north);
\draw[branch] (c7e.north |- bus7In) -- (c7e.north);
\draw[branch] (c7f.north |- bus7In) -- (c7f.north);

\end{tikzpicture}
\end{document}
'''

with open('scratch/pipeline_architecture.tex', 'w', encoding='utf-8') as f:
    f.write(tex_code)

print("Generated perfected scratch/pipeline_architecture.tex")
