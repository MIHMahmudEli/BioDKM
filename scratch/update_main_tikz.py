import re

with open('AJSE_LaTeX/main.tex', 'r', encoding='utf-8') as f:
    content = f.read()

new_tikz = r'''\begin{figure*}[!t]
\centering
\resizebox{0.98\textwidth}{!}{%
\begin{tikzpicture}[
  font=\sffamily,
  >=Stealth,
  card/.style={draw=#1Border, fill=#1Bg, line width=0.85pt, rounded corners=4.5pt, align=center, inner sep=4.5pt, text=textDark},
  subcard/.style={draw=#1Border!75, fill=white, line width=0.65pt, rounded corners=3.5pt, align=center, inner sep=3.8pt, text=textDark},
  badge/.style={draw=#1Border!95, fill=#1Badge, text=white, font=\sffamily\bfseries\fontsize{5.5pt}{6.5pt}\selectfont, rounded corners=2.5pt, inner sep=2.5pt, anchor=center},
  bus/.style={line width=1.1pt, draw=busSlate},
  branch/.style={-{Stealth[length=3.8pt, width=2.8pt]}, line width=0.8pt, draw=busSlate},
  junc/.style={circle, fill=busSlate, inner sep=0pt, minimum size=3.4pt}
]

% ─── ROW 1: ACQUISITION & PREPROCESSING ─────────────────────────────────────
\node[card=cTeal, text width=120mm, minimum height=18mm] (cStage1) at (-63mm, 0) {
  \vspace{1.5mm}\\
  {\fontsize{8.5pt}{10pt}\selectfont\textbf{NCBI Entrez E-Utilities Data Acquisition Engine}}\\[1.5pt]
  {\fontsize{6.8pt}{8.2pt}\selectfont Automated retrieval across 8 clinical queries ($N = 14{,}065$ PubMed abstracts)}\\[1pt]
  {\fontsize{6pt}{7.2pt}\selectfont\color{textSub} Neoplasm (1,951) $\cdot$ Diabetes (1,922) $\cdot$ Stroke (1,880) $\cdot$ Alzheimer's (1,753) $\cdot$ Hypertension (1,747) $\cdot$ CVD (1,722) $\cdot$ Neuro (1,586) $\cdot$ Parkinson's (1,504)}
};
\node[badge=cTeal] at (cStage1.north) {STAGE 1: CORPUS ACQUISITION};

\node[card=cSlate, text width=120mm, minimum height=18mm] (cStage2) at (63mm, 0) {
  \vspace{1.5mm}\\
  {\fontsize{8.5pt}{10pt}\selectfont\textbf{Biomedical Text Standardization \& Cleaning Pipeline}}\\[1.5pt]
  {\fontsize{6.8pt}{8.2pt}\selectfont Lowercase normalisation $\cdot$ Regex non-alphabetic filtering ($[\text{\textasciicircum a-zA-Z}\backslash\text{s}]$) $\cdot$ NLTK tokenisation}\\[1pt]
  {\fontsize{6pt}{7.2pt}\selectfont\color{textSub} Stop-word removal $\cdot$ Length thresholding ($\text{len} > 2$) $\cdot$ Strict deduplication $\rightarrow$ \textbf{14{,}064 Verified Documents}}
};
\node[badge=cSlate] at (cStage2.north) {STAGE 2: BIOMEDICAL TEXT PREPROCESSING};

\draw[branch] (cStage1.east) -- (cStage2.west);

% ─── ROW 2: MULTI-REPRESENTATION EXTRACTION ─────────────────────────────────
\coordinate (r2Center) at (0, -25.5mm);

\node[subcard=cBlue, text width=56mm, minimum height=22mm] at ($(r2Center) + (-93mm, 0)$) (c3a) {
  {\fontsize{7.8pt}{9.2pt}\selectfont\textbf{3a. Sparse TF-IDF Vectorizer}}\\[1.5pt]
  {\fontsize{6.5pt}{7.8pt}\selectfont Term Salience \& Inverse Doc Frequency}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont\color{textSub} $\text{vocab} = 5{,}000$ (unigram + bigram) $\cdot$ $\text{min\_df} = 5$\\[0.5pt] Output: $\mathbf{X} \in \mathbb{R}^{14{,}064 \times 5{,}000}$ ($\ell_2$-norm)}
};

\node[subcard=cBlue, text width=56mm, minimum height=22mm] at ($(r2Center) + (-31mm, 0)$) (c3b) {
  {\fontsize{7.8pt}{9.2pt}\selectfont\textbf{3b. BioBERT v1.1 Encoder}}\\[1.5pt]
  {\fontsize{6.5pt}{7.8pt}\selectfont PubMed + PMC Continual Pretraining}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont\color{textSub} 12-layer, 768-d Contextual BERT $\cdot$ Mean pool\\[0.5pt] Output: $\mathbf{X} \in \mathbb{R}^{14{,}064 \times 768}$ ($\ell_2$-norm)}
};

\node[subcard=cBlue, text width=56mm, minimum height=22mm] at ($(r2Center) + (31mm, 0)$) (c3c) {
  {\fontsize{7.8pt}{9.2pt}\selectfont\textbf{3c. Scientific BERT Encoders}}\\[1.5pt]
  {\fontsize{6.5pt}{7.8pt}\selectfont Scratch \& Multi-Domain Encoders}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont\color{textSub} \textbf{PubMedBERT}: 768-d from scratch on PubMed\\[0.5pt] \textbf{SciBERT}: 768-d scientific \textit{scivocab} ($\ell_2$-norm)}
};

\node[subcard=cBlue, text width=56mm, minimum height=22mm] at ($(r2Center) + (93mm, 0)$) (c3d) {
  {\fontsize{7.8pt}{9.2pt}\selectfont\textbf{3d. Sentence-Transformer}}\\[1.5pt]
  {\fontsize{6.5pt}{7.8pt}\selectfont Contrastive Bi-Encoder Architecture}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont\color{textSub} \textbf{all-MiniLM-L6-v2}: 384-d dense embedding\\[0.5pt] 1B+ sentence pair contrastive pretraining}
};

\begin{scope}[on background layer]
  \node[card=cBlue, inner xsep=4.5pt, inner ysep=7.5pt, yshift=2.2mm, fit=(c3a) (c3d)] (boxStage3) {};
\end{scope}
\node[badge=cBlue] at (boxStage3.north) {STAGE 3: MULTI-REPRESENTATION FEATURE EXTRACTION};

% ─── ROW 3: DIAGNOSTIC & TOPOLOGICAL REDUCTION ──────────────────────────────
\coordinate (r3Center) at (0, -49mm);

\node[card=cAmber, text width=120mm, minimum height=17mm] at ($(r3Center) + (-63mm, 0)$) (c4a) {
  \vspace{1.5mm}\\
  {\fontsize{8.5pt}{10pt}\selectfont\textbf{Centroid Diagnostic Analysis (Exploratory Separability)}}\\[1.5pt]
  {\fontsize{6.8pt}{8.2pt}\selectfont $K = 10$ pseudo-class partitioning $\cdot$ Centroid vectors $\boldsymbol{\mu}_c = \frac{1}{|P_c|}\sum_{d \in P_c}\mathbf{E}_d$}\\[1pt]
  {\fontsize{6pt}{7.2pt}\selectfont\color{textSub} Pairwise centroid cosine similarity matrix $\cdot$ Verification of embedding space modularity}
};
\node[badge=cAmber] at (c4a.north) {STAGE 4A: CENTROID DIAGNOSTICS};

\node[card=cAmber, text width=120mm, minimum height=17mm] at ($(r3Center) + (63mm, 0)$) (c4b) {
  \vspace{1.5mm}\\
  {\fontsize{8.5pt}{10pt}\selectfont\textbf{Topological Manifold Projection \& Dimensionality Ablation}}\\[1.5pt]
  {\fontsize{6.8pt}{8.2pt}\selectfont UMAP 2D Manifold Approximation: Fuzzy simplicial cross-entropy minimization ($\text{cosine}, k{=}15$)}\\[1pt]
  {\fontsize{6pt}{7.2pt}\selectfont\color{textSub} Full Ablation: High-Dim vs. PCA (50D/2D) vs. UMAP 2D $\cdot$ Trustworthiness preservation score $T(k) = 0.982$}
};
\node[badge=cAmber] at (c4b.north) {STAGE 4B: TOPOLOGICAL MANIFOLD PROJECTION};

% ─── ROW 4: CLUSTERING & BASELINES ──────────────────────────────────────────
\coordinate (r4Center) at (0, -71.5mm);

\node[subcard=cGreen, text width=56mm, minimum height=20mm] at ($(r4Center) + (-93mm, 0)$) (c5a) {
  {\fontsize{7.8pt}{9.2pt}\selectfont\textbf{5a. HDBSCAN Density}}\\[1.5pt]
  {\fontsize{6.5pt}{7.8pt}\selectfont Hierarchical Density Clustering}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont\color{textSub} Mutual reachability $\cdot$ MST condensation\\[0.5pt] \textbf{80--116 Fine-grained Topics + Noise}}
};

\node[subcard=cGreen, text width=56mm, minimum height=20mm] at ($(r4Center) + (-31mm, 0)$) (c5b) {
  {\fontsize{7.8pt}{9.2pt}\selectfont\textbf{5b. KMeans Partitioning}}\\[1.5pt]
  {\fontsize{6.5pt}{7.8pt}\selectfont Centroid Distance Optimization}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont\color{textSub} Spherical Voronoi tessellation $\cdot$ Elbow sweep\\[0.5pt] \textbf{Optimal $K = 5$ Macro Categories}}
};

\node[subcard=cGreen, text width=56mm, minimum height=20mm] at ($(r4Center) + (31mm, 0)$) (c5c) {
  {\fontsize{7.8pt}{9.2pt}\selectfont\textbf{5c. Agglomerative Hier.}}\\[1.5pt]
  {\fontsize{6.5pt}{7.8pt}\selectfont Bottom-up Dendrogram Clustering}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont\color{textSub} Ward minimum variance $\cdot$ Pairwise Euclidean\\[0.5pt] \textbf{Hierarchical Tree Cut ($K = 5$)}}
};

\node[subcard=cGreen, text width=56mm, minimum height=20mm] at ($(r4Center) + (93mm, 0)$) (c5d) {
  {\fontsize{7.8pt}{9.2pt}\selectfont\textbf{5d. Literature Baselines}}\\[1.5pt]
  {\fontsize{6.5pt}{7.8pt}\selectfont Classical \& Neural Benchmarks}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont\color{textSub} \textbf{LDA}: Latent Dirichlet Allocation (VB)\\[0.5pt] \textbf{BERTopic}: Transformer + HDBSCAN + c-TF-IDF}
};

\begin{scope}[on background layer]
  \node[card=cGreen, inner xsep=4.5pt, inner ysep=7.5pt, yshift=2.2mm, fit=(c5a) (c5d)] (boxStage5) {};
\end{scope}
\node[badge=cGreen] at (boxStage5.north) {STAGE 5: CLUSTERING \& BASELINES};

% ─── ROW 5: TOPIC INTERPRETATION ───────────────────────────────────────────
\coordinate (r5Center) at (0, -92.5mm);

\node[card=cPurple, text width=248mm, minimum height=15.5mm] at (r5Center) (cStage6) {
  \vspace{1.5mm}\\
  {\fontsize{8.5pt}{10pt}\selectfont\textbf{Topic Semantic Interpretation \& Complete Noise Partition Allocation}}\\[1.5pt]
  {\fontsize{6.8pt}{8.2pt}\selectfont Class-based TF-IDF ($c\text{-TF-IDF}$): $W_{t,c} = \frac{tf_{t,c}}{tf_c} \cdot \log\left(1 + \frac{A}{tf_t}\right)$ $\cdot$ Automated Title-Case Clinical Label Synthesis}\\[1pt]
  {\fontsize{6pt}{7.2pt}\selectfont\color{textSub} Soft $k$-NN classification protocol for noise boundary papers $\rightarrow$ Guaranteed 100\% complete corpus document assignment}
};
\node[badge=cPurple] at (cStage6.north) {STAGE 6: TOPIC SEMANTIC INTERPRETATION \& NOISE RE-ALLOCATION};

% ─── ROW 6: MULTI-PILLAR EMPIRICAL VALIDATION SUITE ────────────────────────
\coordinate (r6Center) at (0, -114.5mm);

\node[subcard=cRose, text width=37mm, minimum height=20mm] at ($(r6Center) + (-104.5mm, 0)$) (c7a) {
  {\fontsize{7.5pt}{8.8pt}\selectfont\textbf{7a. Intrinsic Quality}}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont Silhouette (0.4786)\\[0.5pt] Davies-Bouldin (0.6034)\\[0.5pt] Matched-Core Ablation}
};

\node[subcard=cRose, text width=37mm, minimum height=20mm] at ($(r6Center) + (-62.7mm, 0)$) (c7b) {
  {\fontsize{7.5pt}{8.8pt}\selectfont\textbf{7b. Semantic Purity}}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont NPMI Coherence (0.1158)\\[0.5pt] Word Intrusion (98.55\%)\\[0.5pt] Purity Margin (+0.145)}
};

\node[subcard=cRose, text width=37mm, minimum height=20mm] at ($(r6Center) + (-20.9mm, 0)$) (c7c) {
  {\fontsize{7.5pt}{8.8pt}\selectfont\textbf{7c. Disease Alignment}}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont Adjusted Rand Index (ARI)\\[0.5pt] Normalized MI (NMI)\\[0.5pt] Ground-Truth Matrix}
};

\node[subcard=cRose, text width=37mm, minimum height=20mm] at ($(r6Center) + (20.9mm, 0)$) (c7d) {
  {\fontsize{7.5pt}{8.8pt}\selectfont\textbf{7d. MeSH Grounding}}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont 2024 NLM MeSH Tree\\[0.5pt] Depths 1--8 Alignment\\[0.5pt] Granular Depths 4--6}
};

\node[subcard=cRose, text width=37mm, minimum height=20mm] at ($(r6Center) + (62.7mm, 0)$) (c7e) {
  {\fontsize{7.5pt}{8.8pt}\selectfont\textbf{7e. Comorbidity Net}}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont Unsupervised Cosine Net\\[0.5pt] Cardiovasc-Stroke 0.812\\[0.5pt] Alzheimer-Stroke 0.782}
};

\node[subcard=cRose, text width=37mm, minimum height=20mm] at ($(r6Center) + (104.5mm, 0)$) (c7f) {
  {\fontsize{7.5pt}{8.8pt}\selectfont\textbf{7f. Scalability/Stab.}}\\[1pt]
  {\fontsize{5.8pt}{7pt}\selectfont 10-Fold Perturb. ($0.750$)\\[0.5pt] Near-Linear ($\alpha = 0.326$)\\[0.5pt] 451 docs/s ($16.5\times$ BERTopic)}
};

\begin{scope}[on background layer]
  \node[card=cRose, inner xsep=4.5pt, inner ysep=7.5pt, yshift=2.2mm, fit=(c7a) (c7f)] (boxStage7) {};
\end{scope}
\node[badge=cRose] at (boxStage7.north) {STAGE 7: MULTI-PILLAR EMPIRICAL VALIDATION SUITE};

% ─── ORTHOGONAL BUS ROUTING & INTERCONNECTS ─────────────────────────────────

% Bus 1: Stage 2 -> Stage 3
\coordinate (bus1Center) at ($(cStage2.south)!0.48!(boxStage3.north)$);
\draw[bus] (cStage2.south) -- (cStage2.south |- bus1Center) -- (0, bus1Center);
\draw[branch] (0, bus1Center) -- (boxStage3.north);
\node[junc] at (cStage2.south) {};
\node[junc] at (cStage2.south |- bus1Center) {};
\node[junc] at (0, bus1Center) {};

\coordinate (bus3In) at ($(boxStage3.north)!0.5!(c3b.north)$);
\draw[bus] (boxStage3.north) -- (0, bus3In);
\draw[bus] (c3a.north |- bus3In) -- (c3d.north |- bus3In);
\node[junc] at (0, bus3In) {};
\node[junc] at (c3a.north |- bus3In) {};
\node[junc] at (c3b.north |- bus3In) {};
\node[junc] at (c3c.north |- bus3In) {};
\node[junc] at (c3d.north |- bus3In) {};
\draw[branch] (c3a.north |- bus3In) -- (c3a.north);
\draw[branch] (c3b.north |- bus3In) -- (c3b.north);
\draw[branch] (c3c.north |- bus3In) -- (c3c.north);
\draw[branch] (c3d.north |- bus3In) -- (c3d.north);

% Bus 2: Stage 3 -> Stage 4
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

% Bus 3: Stage 4 -> Stage 5
\coordinate (bus3CollectY) at ($(c4a.south)!0.48!(boxStage5.north)$);
\draw[bus] (c4a.south) -- (c4a.south |- bus3CollectY);
\draw[bus] (c4b.south) -- (c4b.south |- bus3CollectY);
\draw[bus] (c4a.south |- bus3CollectY) -- (c4b.south |- bus3CollectY);
\draw[branch] (0, bus3CollectY) -- (boxStage5.north);
\node[junc] at (c4a.south |- bus3CollectY) {};
\node[junc] at (c4b.south |- bus3CollectY) {};
\node[junc] at (0, bus3CollectY) {};

\coordinate (bus5In) at ($(boxStage5.north)!0.5!(c5b.north)$);
\draw[bus] (boxStage5.north) -- (0, bus5In);
\draw[bus] (c5a.north |- bus5In) -- (c5d.north |- bus5In);
\node[junc] at (0, bus5In) {};
\node[junc] at (c5a.north |- bus5In) {};
\node[junc] at (c5b.north |- bus5In) {};
\node[junc] at (c5c.north |- bus5In) {};
\node[junc] at (c5d.north |- bus5In) {};
\draw[branch] (c5a.north |- bus5In) -- (c5a.north);
\draw[branch] (c5b.north |- bus5In) -- (c5b.north);
\draw[branch] (c5c.north |- bus5In) -- (c5c.north);
\draw[branch] (c5d.north |- bus5In) -- (c5d.north);

% Bus 4: Stage 5 -> Stage 6
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
\node[junc] at (0, bus4Y) {};
\draw[branch] (0, bus4Y) -- (cStage6.north);

% Bus 5: Stage 6 -> Stage 7
\draw[branch] (cStage6.south) -- (boxStage7.north);
\node[junc] at (cStage6.south) {};

\coordinate (bus7In) at ($(boxStage7.north)!0.5!(c7c.north)$);
\draw[bus] (boxStage7.north) -- (0, bus7In);
\draw[bus] (c7a.north |- bus7In) -- (c7f.north |- bus7In);
\node[junc] at (0, bus7In) {};
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

\end{tikzpicture}%
}
\caption{Comprehensive experimental pipeline architecture for unsupervised biomedical disease knowledge mapping. The framework incorporates five distinct feature representations (TF-IDF, BioBERT, PubMedBERT, SciBERT, Sentence-MiniLM), dimensionality reduction ablation (High-Dim, PCA, UMAP), three core clustering paradigms, classical (LDA) and neural (BERTopic) baselines, and a multi-pillar evaluation strategy spanning intrinsic clustering quality, extrinsic semantic coherence, ground-truth disease alignment, MeSH clinical ontology grounding, unsupervised disease comorbidity networking, apples-to-apples noise ablation, 10-fold topological perturbation stability, automated word intrusion purity benchmarks, and empirical asymptotic scalability stress-testing.}
\label{fig:pipeline}
\end{figure*}'''

# Pattern to replace Figure 1
pat = re.compile(r'\\begin\{figure\*\}\[!t\].*?\\label\{fig:pipeline\}\s*\\end\{figure\*\}', re.DOTALL)
if pat.search(content):
    content = pat.sub(lambda m: new_tikz, content)
    with open('AJSE_LaTeX/main.tex', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced Figure 1 in AJSE_LaTeX/main.tex successfully.")
else:
    print("Error: Could not find Figure 1 pattern in main.tex")
