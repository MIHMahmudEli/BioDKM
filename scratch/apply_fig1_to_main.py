import re
import subprocess

with open('scratch/test_pipeline_main.tex', 'r', encoding='utf-8') as f:
    standalone_code = f.read()

# Extract the tikzpicture block
start = standalone_code.find(r'\begin{tikzpicture}')
end = standalone_code.find(r'\end{tikzpicture}') + len(r'\end{tikzpicture}')
tikz_block = standalone_code[start:end]

fig_latex = r'''\begin{figure*}[!t]
\centering
\resizebox{0.98\textwidth}{!}{%
''' + tikz_block + r'''%
}
\caption{Comprehensive experimental pipeline architecture for unsupervised biomedical disease knowledge mapping. The framework incorporates five distinct feature representations (TF-IDF, BioBERT, PubMedBERT, SciBERT, Sentence-MiniLM), dimensionality reduction ablation (High-Dim, PCA, UMAP), three core clustering paradigms, classical (LDA) and neural (BERTopic) baselines, and a multi-pillar evaluation strategy spanning intrinsic clustering quality, extrinsic semantic coherence, ground-truth disease alignment, MeSH clinical ontology grounding, unsupervised disease comorbidity networking, apples-to-apples noise ablation, 10-fold topological perturbation stability, automated word intrusion purity benchmarks, and empirical asymptotic scalability stress-testing.}
\label{fig:pipeline}
\end{figure*}'''

with open('AJSE_LaTeX/main.tex', 'r', encoding='utf-8') as f:
    main_tex = f.read()

pat = re.compile(r'\\begin\{figure\*\}\[!t\].*?\\label\{fig:pipeline\}\s*\\end\{figure\*\}', re.DOTALL)
if pat.search(main_tex):
    main_tex = pat.sub(lambda m: fig_latex, main_tex)
    with open('AJSE_LaTeX/main.tex', 'w', encoding='utf-8') as f:
        f.write(main_tex)
    print("Updated main.tex with perfected TikZ figure.")
else:
    print("Error: Could not match Figure 1 in main.tex")
