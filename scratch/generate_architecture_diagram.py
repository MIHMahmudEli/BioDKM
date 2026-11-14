import os
import shutil
import subprocess

tex_code = r"""\documentclass[tikz,border=12pt]{standalone}
\usepackage{xcolor}
\usepackage{amsmath,amssymb}
\usepackage{microtype}
\usetikzlibrary{shapes,arrows.meta,positioning,calc,fit,backgrounds}

% ─── High-Contrast Academic Color Palette ───────────────────────────────────
\definecolor{headerNavy}{RGB}{15, 23, 42}
\definecolor{busSlate}{RGB}{30, 41, 59}        % Slate-800 for maximum line contrast
\definecolor{textDark}{RGB}{15, 23, 42}
\definecolor{textSub}{RGB}{71, 85, 105}

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
  card/.style={draw=#1Border, fill=#1Bg, line width=1.1pt, rounded corners=5pt, align=center, inner sep=4.5pt, text=textDark},
  subcard/.style={draw=#1Border!85, fill=white, line width=0.8pt, rounded corners=3.5pt, align=center, inner sep=3.5pt, text=textDark},
  headerBar/.style={fill=#1Badge, text=white, font=\sffamily\bfseries\fontsize{7.2pt}{8.8pt}\selectfont, rounded corners=2.5pt, inner sep=3pt, minimum height=4.8mm, align=center},
  bus/.style={line width=1.4pt, draw=busSlate},
  branch/.style={-{Stealth[length=5.5pt, width=4.0pt]}, line width=1.1pt, draw=busSlate},
  mainArrow/.style={-{Stealth[length=7.0pt, width=5.2pt]}, line width=1.6pt, draw=busSlate},
  junc/.style={circle, fill=busSlate, inner sep=0pt, minimum size=4.0pt}
]

\coordinate (originX) at (0,0);

% ─── ROW 1: ACQUISITION & PREPROCESSING ─────────────────────────────────────
% Centers at -66mm and +66mm, width 114mm -> Gap between cards is exactly 18mm!
\node[card=cTeal, text width=114mm, minimum height=18mm] (cStage1) at (-66mm, 0) {
  {\color{cTealBadge}\bfseries\fontsize{7.5pt}{9pt}\selectfont STAGE 1: CORPUS ACQUISITION}\\[1.5pt]
  {\color{cTealBorder!50}\rule{110mm}{0.5pt}}\\[2.5pt]
  {\fontsize{8.5pt}{10.2pt}\selectfont\textbf{NCBI Entrez E-Utilities Data Acquisition Engine}}\\[1.5pt]
  {\fontsize{7.0pt}{8.4pt}\selectfont Automated retrieval across 8 clinical queries ($N = 14{,}065$ PubMed abstracts)}\\[1pt]
  {\fontsize{6.2pt}{7.4pt}\selectfont\color{textSub} Neoplasm (1,951) $\cdot$ Diabetes (1,922) $\cdot$ Stroke (1,880) $\cdot$ Alzheimer's (1,753) $\cdot$ Hypertension (1,747) $\cdot$ CVD (1,722) $\cdot$ Neuro (1,586) $\cdot$ Parkinson's (1,504)}
};

\node[card=cSlate, text width=114mm, minimum height=18mm] (cStage2) at (66mm, 0) {
  {\color{cSlateBadge}\bfseries\fontsize{7.5pt}{9pt}\selectfont STAGE 2: BIOMEDICAL TEXT PREPROCESSING}\\[1.5pt]
  {\color{cSlateBorder!50}\rule{110mm}{0.5pt}}\\[2.5pt]
  {\fontsize{8.5pt}{10.2pt}\selectfont\textbf{Biomedical Text Standardization \& Cleaning Pipeline}}\\[1.5pt]
  {\fontsize{7.0pt}{8.4pt}\selectfont Lowercase normalisation $\cdot$ Regex non-alphabetic filtering ($[\text{\textasciicircum a-zA-Z}\backslash\text{s}]$) $\cdot$ NLTK tokenisation}\\[1pt]
  {\fontsize{6.2pt}{7.4pt}\selectfont\color{textSub} Stop-word removal $\cdot$ Length thresholding ($\text{len} > 2$) $\cdot$ Strict deduplication $\rightarrow$ \textbf{14{,}064 Verified Documents}}
};

% 18mm prominent horizontal arrow connecting Stage 1 to Stage 2
\draw[mainArrow] (cStage1.east) -- (cStage2.west);

% ─── ROW 2: MULTI-REPRESENTATION EXTRACTION (14mm vertical gap from Row 1) ──
\coordinate (r2Center) at (0, -43mm);

\node[headerBar=cBlue, text width=248mm] (hStage3) at ($(r2Center) + (0, 15.5mm)$) {STAGE 3: MULTI-REPRESENTATION FEATURE EXTRACTION};

\node[subcard=cBlue, text width=56mm, minimum height=18mm] at ($(r2Center) + (-93mm, -2.5mm)$) (c3a) {
  {\fontsize{8.0pt}{9.5pt}\selectfont\textbf{3a. Sparse TF-IDF Vectorizer}}\\[1.5pt]
  {\fontsize{6.7pt}{8.0pt}\selectfont Term Salience \& Inverse Doc Frequency}\\[1pt]
  {\fontsize{6.0pt}{7.2pt}\selectfont\color{textSub} $\text{vocab} = 5{,}000$ (unigram + bigram) $\cdot$ $\text{min\_df} = 5$\\[0.5pt] Output: $\mathbf{X} \in \mathbb{R}^{14{,}064 \times 5{,}000}$ ($\ell_2$-norm)}
};

\node[subcard=cBlue, text width=56mm, minimum height=18mm] at ($(r2Center) + (-31mm, -2.5mm)$) (c3b) {
  {\fontsize{8.0pt}{9.5pt}\selectfont\textbf{3b. BioBERT v1.1 Encoder}}\\[1.5pt]
  {\fontsize{6.7pt}{8.0pt}\selectfont PubMed + PMC Continual Pretraining}\\[1pt]
  {\fontsize{6.0pt}{7.2pt}\selectfont\color{textSub} 12-layer, 768-d Contextual BERT $\cdot$ Mean pool\\[0.5pt] Output: $\mathbf{X} \in \mathbb{R}^{14{,}064 \times 768}$ ($\ell_2$-norm)}
};

\node[subcard=cBlue, text width=56mm, minimum height=18mm] at ($(r2Center) + (31mm, -2.5mm)$) (c3c) {
  {\fontsize{8.0pt}{9.5pt}\selectfont\textbf{3c. Scientific BERT Encoders}}\\[1.5pt]
  {\fontsize{6.7pt}{8.0pt}\selectfont Scratch \& Multi-Domain Encoders}\\[1pt]
  {\fontsize{6.0pt}{7.2pt}\selectfont\color{textSub} \textbf{PubMedBERT}: 768-d from scratch on PubMed\\[0.5pt] \textbf{SciBERT}: 768-d scientific \textit{scivocab} ($\ell_2$-norm)}
};

\node[subcard=cBlue, text width=56mm, minimum height=18mm] at ($(r2Center) + (93mm, -2.5mm)$) (c3d) {
  {\fontsize{8.0pt}{9.5pt}\selectfont\textbf{3d. Sentence-Transformer}}\\[1.5pt]
  {\fontsize{6.7pt}{8.0pt}\selectfont Contrastive Bi-Encoder Architecture}\\[1pt]
  {\fontsize{6.0pt}{7.2pt}\selectfont\color{textSub} \textbf{all-MiniLM-L6-v2}: 384-d dense embedding\\[0.5pt] 1B+ sentence pair contrastive pretraining}
};

\begin{scope}[on background layer]
  \node[card=cBlue, inner xsep=4.5pt, inner ysep=4.5pt, fit=(hStage3) (c3a) (c3d)] (boxStage3) {};
\end{scope}

% ─── ROW 3: DIAGNOSTIC & TOPOLOGICAL REDUCTION (11.5mm vertical gap from Row 2)
\coordinate (r3Center) at (0, -77mm);

\node[card=cAmber, text width=114mm, minimum height=18mm] at ($(r3Center) + (-66mm, 0)$) (c4a) {
  {\color{cAmberBadge}\bfseries\fontsize{7.5pt}{9pt}\selectfont STAGE 4A: CENTROID DIAGNOSTICS}\\[1.5pt]
  {\color{cAmberBorder!50}\rule{110mm}{0.5pt}}\\[2.5pt]
  {\fontsize{8.5pt}{10.2pt}\selectfont\textbf{Centroid Diagnostic Analysis (Exploratory Separability)}}\\[1.5pt]
  {\fontsize{7.0pt}{8.4pt}\selectfont $K = 10$ pseudo-class partitioning $\cdot$ Centroid vectors $\boldsymbol{\mu}_c = \frac{1}{|P_c|}\sum_{d \in P_c}\mathbf{E}_d$}\\[1pt]
  {\fontsize{6.2pt}{7.4pt}\selectfont\color{textSub} Pairwise centroid cosine similarity matrix $\cdot$ Modularity verification}
};

\node[card=cAmber, text width=114mm, minimum height=18mm] at ($(r3Center) + (66mm, 0)$) (c4b) {
  {\color{cAmberBadge}\bfseries\fontsize{7.5pt}{9pt}\selectfont STAGE 4B: TOPOLOGICAL MANIFOLD PROJECTION}\\[1.5pt]
  {\color{cAmberBorder!50}\rule{110mm}{0.5pt}}\\[2.5pt]
  {\fontsize{8.5pt}{10.2pt}\selectfont\textbf{Topological Manifold Projection \& Dimensionality Ablation}}\\[1.5pt]
  {\fontsize{7.0pt}{8.4pt}\selectfont UMAP 2D Approximation: Fuzzy simplicial cross-entropy ($\text{cosine}, k{=}15$)}\\[1pt]
  {\fontsize{6.2pt}{7.4pt}\selectfont\color{textSub} Full Ablation: High-Dim vs. PCA (50D/2D) vs. UMAP 2D $\cdot$ Trustworthiness $T(k) = 0.982$}
};

% ─── ROW 4: CLUSTERING & BASELINES (14.5mm vertical gap from Row 3) ─────────
\coordinate (r4Center) at (0, -119mm);

\node[headerBar=cGreen, text width=248mm] (hStage5) at ($(r4Center) + (0, 15.5mm)$) {STAGE 5: CLUSTERING \& BASELINES};

\node[subcard=cGreen, text width=56mm, minimum height=18mm] at ($(r4Center) + (-93mm, -2.5mm)$) (c5a) {
  {\fontsize{8.0pt}{9.5pt}\selectfont\textbf{5a. HDBSCAN Density}}\\[1.5pt]
  {\fontsize{6.7pt}{8.0pt}\selectfont Hierarchical Density Clustering}\\[1pt]
  {\fontsize{6.0pt}{7.2pt}\selectfont\color{textSub} Mutual reachability $\cdot$ MST condensation\\[0.5pt] \textbf{80--116 Fine-grained Topics + Noise}}
};

\node[subcard=cGreen, text width=56mm, minimum height=18mm] at ($(r4Center) + (-31mm, -2.5mm)$) (c5b) {
  {\fontsize{8.0pt}{9.5pt}\selectfont\textbf{5b. KMeans Partitioning}}\\[1.5pt]
  {\fontsize{6.7pt}{8.0pt}\selectfont Centroid Distance Optimization}\\[1pt]
  {\fontsize{6.0pt}{7.2pt}\selectfont\color{textSub} Spherical Voronoi tessellation $\cdot$ Elbow sweep\\[0.5pt] \textbf{Optimal $K = 5$ Macro Categories}}
};

\node[subcard=cGreen, text width=56mm, minimum height=18mm] at ($(r4Center) + (31mm, -2.5mm)$) (c5c) {
  {\fontsize{8.0pt}{9.5pt}\selectfont\textbf{5c. Agglomerative Hier.}}\\[1.5pt]
  {\fontsize{6.7pt}{8.0pt}\selectfont Bottom-up Dendrogram Clustering}\\[1pt]
  {\fontsize{6.0pt}{7.2pt}\selectfont\color{textSub} Ward minimum variance $\cdot$ Pairwise Euclidean\\[0.5pt] \textbf{Hierarchical Tree Cut ($K = 5$)}}
};

\node[subcard=cGreen, text width=56mm, minimum height=18mm] at ($(r4Center) + (93mm, -2.5mm)$) (c5d) {
  {\fontsize{8.0pt}{9.5pt}\selectfont\textbf{5d. Literature Baselines}}\\[1.5pt]
  {\fontsize{6.7pt}{8.0pt}\selectfont Classical \& Neural Benchmarks}\\[1pt]
  {\fontsize{6.0pt}{7.2pt}\selectfont\color{textSub} \textbf{LDA}: Latent Dirichlet Allocation (VB)\\[0.5pt] \textbf{BERTopic}: Transformer + HDBSCAN + c-TF-IDF}
};

\begin{scope}[on background layer]
  \node[card=cGreen, inner xsep=4.5pt, inner ysep=4.5pt, fit=(hStage5) (c5a) (c5d)] (boxStage5) {};
\end{scope}

% ─── ROW 5: TOPIC INTERPRETATION (11.5mm vertical gap from Row 4) ──────────
\coordinate (r5Center) at (0, -151.5mm);

\node[card=cPurple, text width=248mm, minimum height=16mm] at (r5Center) (cStage6) {
  {\color{cPurpleBadge}\bfseries\fontsize{7.5pt}{9pt}\selectfont STAGE 6: TOPIC SEMANTIC INTERPRETATION \& NOISE RE-ALLOCATION}\\[1.5pt]
  {\color{cPurpleBorder!50}\rule{244mm}{0.5pt}}\\[2.5pt]
  {\fontsize{8.5pt}{10.2pt}\selectfont\textbf{Topic Semantic Interpretation \& Complete Noise Partition Allocation}}\\[1.5pt]
  {\fontsize{7.0pt}{8.4pt}\selectfont Class-based TF-IDF ($c\text{-TF-IDF}$): $W_{t,c} = \frac{tf_{t,c}}{tf_c} \cdot \log\left(1 + \frac{A}{tf_t}\right)$ $\cdot$ Automated Title-Case Clinical Label Synthesis}\\[1pt]
  {\fontsize{6.2pt}{7.4pt}\selectfont\color{textSub} Soft $k$-NN classification protocol for noise boundary papers $\rightarrow$ Guaranteed 100\% complete corpus document assignment}
};

% ─── ROW 6: MULTI-PILLAR EMPIRICAL VALIDATION SUITE (14mm vertical gap from Row 5)
\coordinate (r6Center) at (0, -193mm);

\node[headerBar=cRose, text width=248mm] (hStage7) at ($(r6Center) + (0, 15.5mm)$) {STAGE 7: MULTI-PILLAR EMPIRICAL VALIDATION SUITE};

\node[subcard=cRose, text width=37mm, minimum height=18mm] at ($(r6Center) + (-104.5mm, -2.5mm)$) (c7a) {
  {\fontsize{7.6pt}{9.0pt}\selectfont\textbf{7a. Intrinsic Quality}}\\[1.5pt]
  {\fontsize{6.1pt}{7.3pt}\selectfont Silhouette (0.4786)\\[0.5pt] Davies-Bouldin (0.6034)\\[0.5pt] Matched-Core Ablation}
};

\node[subcard=cRose, text width=37mm, minimum height=18mm] at ($(r6Center) + (-62.7mm, -2.5mm)$) (c7b) {
  {\fontsize{7.6pt}{9.0pt}\selectfont\textbf{7b. Semantic Purity}}\\[1.5pt]
  {\fontsize{6.1pt}{7.3pt}\selectfont NPMI Coherence (0.1158)\\[0.5pt] Word Intrusion (98.55\%)\\[0.5pt] Purity Margin (+0.145)}
};

\node[subcard=cRose, text width=37mm, minimum height=18mm] at ($(r6Center) + (-20.9mm, -2.5mm)$) (c7c) {
  {\fontsize{7.6pt}{9.0pt}\selectfont\textbf{7c. Disease Alignment}}\\[1.5pt]
  {\fontsize{6.1pt}{7.3pt}\selectfont Adjusted Rand Index (ARI)\\[0.5pt] Normalized MI (NMI)\\[0.5pt] Ground-Truth Matrix}
};

\node[subcard=cRose, text width=37mm, minimum height=18mm] at ($(r6Center) + (20.9mm, -2.5mm)$) (c7d) {
  {\fontsize{7.6pt}{9.0pt}\selectfont\textbf{7d. MeSH Grounding}}\\[1.5pt]
  {\fontsize{6.1pt}{7.3pt}\selectfont 2024 NLM MeSH Tree\\[0.5pt] Depths 1--8 Alignment\\[0.5pt] Granular Depths 4--6}
};

\node[subcard=cRose, text width=37mm, minimum height=18mm] at ($(r6Center) + (62.7mm, -2.5mm)$) (c7e) {
  {\fontsize{7.6pt}{9.0pt}\selectfont\textbf{7e. Comorbidity Net}}\\[1.5pt]
  {\fontsize{6.1pt}{7.3pt}\selectfont Unsupervised Cosine Net\\[0.5pt] Cardiovasc-Stroke 0.812\\[0.5pt] Alzheimer-Stroke 0.782}
};

\node[subcard=cRose, text width=37mm, minimum height=18mm] at ($(r6Center) + (104.5mm, -2.5mm)$) (c7f) {
  {\fontsize{7.6pt}{9.0pt}\selectfont\textbf{7f. Scalability/Stab.}}\\[1.5pt]
  {\fontsize{6.1pt}{7.3pt}\selectfont 10-Fold Perturb. ($0.750$)\\[0.5pt] Near-Linear ($\alpha = 0.326$)\\[0.5pt] 451 docs/s ($16.5\times$ BERTopic)}
};

\begin{scope}[on background layer]
  \node[card=cRose, inner xsep=4.5pt, inner ysep=4.5pt, fit=(hStage7) (c7a) (c7f)] (boxStage7) {};
\end{scope}

% ─── ORTHOGONAL BUS ROUTING & INTERCONNECTS ─────────────────────────────────

% Bus 1: Stage 2 -> Stage 3 (Clean 8mm drop into boxStage3.north, NO junction dot on corner!)
\coordinate (bus1Center) at ($(cStage2.south)!0.42!(boxStage3.north)$);
\draw[bus] (cStage2.south) -- (cStage2.south |- bus1Center) -- (originX |- bus1Center);
\draw[mainArrow] (originX |- bus1Center) -- (boxStage3.north);
\node[junc] at (cStage2.south) {};
\node[junc] at (cStage2.south |- bus1Center) {};

% Internal distribution bus inside Stage 3
\coordinate (bus3In) at ($(hStage3.south)!0.5!(c3b.north)$);
\draw[bus] (originX |- hStage3.south) -- (originX |- bus3In);
\draw[bus] (c3a.north |- bus3In) -- (c3d.north |- bus3In);
\node[junc] at (originX |- bus3In) {};
\node[junc] at (c3a.north |- bus3In) {};
\node[junc] at (c3b.north |- bus3In) {};
\node[junc] at (c3c.north |- bus3In) {};
\node[junc] at (c3d.north |- bus3In) {};
\draw[branch] (c3a.north |- bus3In) -- (c3a.north);
\draw[branch] (c3b.north |- bus3In) -- (c3b.north);
\draw[branch] (c3c.north |- bus3In) -- (c3c.north);
\draw[branch] (c3d.north |- bus3In) -- (c3d.north);

% Bus 2: Stage 3 -> Stage 4 (Clean 7mm drop into c4a and c4b)
\coordinate (bus2Y) at ($(boxStage3.south)!0.42!(c4a.north)$);
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
\draw[mainArrow] (c4a.north |- bus2Y) -- (c4a.north);
\draw[mainArrow] (c4b.north |- bus2Y) -- (c4b.north);

% Bus 3: Stage 4 -> Stage 5 (CRITICAL FIX: Full 9mm drop, prominent arrow shaft & head!)
\coordinate (bus3CollectY) at ($(c4a.south)!0.38!(boxStage5.north)$);
\draw[bus] (c4a.south) -- (c4a.south |- bus3CollectY);
\draw[bus] (c4b.south) -- (c4b.south |- bus3CollectY);
\draw[bus] (c4a.south |- bus3CollectY) -- (c4b.south |- bus3CollectY);
\node[junc] at (c4a.south) {};
\node[junc] at (c4b.south) {};
\node[junc] at (c4a.south |- bus3CollectY) {};
\node[junc] at (c4b.south |- bus3CollectY) {};
\node[junc] at (originX |- bus3CollectY) {};
\draw[mainArrow] (originX |- bus3CollectY) -- (boxStage5.north);

% Internal distribution bus inside Stage 5
\coordinate (bus5In) at ($(hStage5.south)!0.5!(c5b.north)$);
\draw[bus] (originX |- hStage5.south) -- (originX |- bus5In);
\draw[bus] (c5a.north |- bus5In) -- (c5d.north |- bus5In);
\node[junc] at (originX |- bus5In) {};
\node[junc] at (c5a.north |- bus5In) {};
\node[junc] at (c5b.north |- bus5In) {};
\node[junc] at (c5c.north |- bus5In) {};
\node[junc] at (c5d.north |- bus5In) {};
\draw[branch] (c5a.north |- bus5In) -- (c5a.north);
\draw[branch] (c5b.north |- bus5In) -- (c5b.north);
\draw[branch] (c5c.north |- bus5In) -- (c5c.north);
\draw[branch] (c5d.north |- bus5In) -- (c5d.north);

% Bus 4: Stage 5 -> Stage 6 (Clean 7mm drop into cStage6.north)
\coordinate (bus4Y) at ($(boxStage5.south)!0.42!(cStage6.north)$);
\draw[bus] (c5a.south) -- (c5a.south |- bus4Y);
\draw[bus] (c5b.south) -- (c5b.south |- bus4Y);
\draw[bus] (c5c.south) -- (c5c.south |- bus4Y);
\draw[bus] (c5d.south) -- (c5d.south |- bus4Y);
\draw[bus] (c5a.south |- bus4Y) -- (c5d.south |- bus4Y);
\node[junc] at (c5a.south |- bus4Y) {};
\node[junc] at (c5b.south |- bus4Y) {};
\node[junc] at (c5c.south |- bus4Y) {};
\node[junc] at (c5d.south |- bus4Y) {};
\node[junc] at (originX |- bus4Y) {};
\draw[mainArrow] (originX |- bus4Y) -- (cStage6.north);

% Bus 5: Stage 6 -> Stage 7 (CRITICAL FIX: Full 14mm long bold, straight vertical arrow!)
\draw[mainArrow] (cStage6.south) -- (boxStage7.north);

% Internal distribution bus inside Stage 7
\coordinate (bus7In) at ($(hStage7.south)!0.5!(c7c.north)$);
\draw[bus] (originX |- hStage7.south) -- (originX |- bus7In);
\draw[bus] (c7a.north |- bus7In) -- (c7f.north |- bus7In);
\node[junc] at (originX |- bus7In) {};
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
"""

with open('scratch/pipeline_architecture.tex', 'w', encoding='utf-8') as f:
    f.write(tex_code)

print("Generated scratch/pipeline_architecture.tex")
