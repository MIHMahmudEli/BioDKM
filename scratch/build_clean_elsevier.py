import re

with open('AJSE_LaTeX/main.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# Locate Introduction
intro_idx = text.find(r'\section{Introduction}')
assert intro_idx != -1, "Could not find Introduction"

body = text[intro_idx:]
body = body.replace(r'\IEEEPARstart{T}{he}', 'The')

# Abstract text from AJSE
abs_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', text, re.DOTALL)
assert abs_match, "Could not find abstract"
abstract_text = abs_match.group(1).strip()
# In abstract, replace $3.5\times$ with 3.5$\times$ so it doesn't collide with cas-dc abstract token macro
abstract_text = abstract_text.replace(r'$3.5\times$', r'3.5$\times$')

preamble = r'''\documentclass[a4paper,fleqn]{cas-dc}

\usepackage[numbers]{natbib}
\usepackage{helvet}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,fit,backgrounds,calc,shapes.geometric}

\graphicspath{{figures/}{./figures/}}
% Float placement optimization
\renewcommand{\topfraction}{0.95}
\renewcommand{\bottomfraction}{0.95}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.80}
\renewcommand{\dbltopfraction}{0.95}
\renewcommand{\dblfloatpagefraction}{0.80}
\setcounter{topnumber}{8}
\setcounter{bottomnumber}{8}
\setcounter{totalnumber}{16}
\setcounter{dbltopnumber}{8}
\setlength{\textfloatsep}{6pt plus 2pt minus 2pt}
\setlength{\floatsep}{6pt plus 2pt minus 2pt}
\setlength{\intextsep}{6pt plus 2pt minus 2pt}
\setlength{\dbltextfloatsep}{6pt plus 2pt minus 2pt}
\setlength{\dblfloatsep}{6pt plus 2pt minus 2pt}


% Colour palette for the high-visibility TikZ pipeline figure
\definecolor{cTealBorder}{RGB}{13, 148, 136}
\definecolor{cTealBg}{RGB}{240, 253, 250}
\definecolor{cTealBadge}{RGB}{15, 118, 110}

\definecolor{cSlateBorder}{RGB}{71, 85, 105}
\definecolor{cSlateBg}{RGB}{248, 250, 252}
\definecolor{cSlateBadge}{RGB}{51, 65, 85}

\definecolor{cBlueBorder}{RGB}{37, 99, 235}
\definecolor{cBlueBg}{RGB}{239, 246, 255}
\definecolor{cBlueBadge}{RGB}{29, 78, 216}

\definecolor{cAmberBorder}{RGB}{217, 119, 6}
\definecolor{cAmberBg}{RGB}{255, 251, 235}
\definecolor{cAmberBadge}{RGB}{180, 83, 9}

\definecolor{cGreenBorder}{RGB}{16, 185, 129}
\definecolor{cGreenBg}{RGB}{236, 253, 245}
\definecolor{cGreenBadge}{RGB}{5, 150, 105}

\definecolor{cPurpleBorder}{RGB}{139, 92, 246}
\definecolor{cPurpleBg}{RGB}{245, 243, 255}
\definecolor{cPurpleBadge}{RGB}{109, 40, 217}

\definecolor{cRoseBorder}{RGB}{225, 29, 72}
\definecolor{cRoseBg}{RGB}{255, 241, 242}
\definecolor{cRoseBadge}{RGB}{190, 18, 60}

\definecolor{busSlate}{RGB}{71, 85, 105}
\definecolor{textDark}{RGB}{15, 23, 42}
\definecolor{textSub}{RGB}{51, 65, 85}

\hypersetup{
  colorlinks=true,
  linkcolor=blue!70!black,
  citecolor=blue!70!black,
  urlcolor=blue!70!black
}

\begin{document}
\let\WriteBookmarks\relax
\def\floatpagepagefraction{1}
\def\textpagefraction{.001}

% Short title
\shorttitle{BioDKM: Biomedical Disease Knowledge Mapping}

% Short author
\shortauthors{M. I. Hossain et al.}

% Main title of the paper
\title [mode = title]{BioDKM: An Unsupervised Topological Framework for Biomedical Disease Knowledge Mapping and Comorbidity Discovery from PubMed Literature}

% Authors
\author[1]{Mohsin Ibna Hossain}[orcid=0009-0003-9123-9040]
\ead{23-50194-1@student.aiub.edu}
\credit{Conceptualization, Methodology, Software, Formal analysis, Writing - Original Draft}

\author[1]{Mosharof Hossain Dpio}[orcid=0009-0008-1036-033X]
\ead{mosharofhossin561@gmail.com}
\credit{Data curation, Investigation, Validation, Formal analysis, Writing - Review \& Editing}

\author[1]{Rajarshi Mondal}
\ead{23-50279-1@student.aiub.edu}
\credit{Software, Visualization, Investigation, Validation}

\author[1]{Shadman Shakib}
\ead{23-50200-1@student.aiub.edu}
\credit{Investigation, Validation, Data curation, Resources}

\author[1]{Tohedul Islam}
\cormark[1]
\ead{islamtohedul@aiub.edu}
\credit{Supervision, Project administration, Resources, Writing - Review \& Editing}

\cortext[cor1]{Corresponding author}

\affiliation[1]{organization={Department of Computer Science and Engineering, American International University-Bangladesh (AIUB)},
    addressline={408/1, Kuratoli, Khilkhet}, 
    city={Dhaka},
    postcode={1229}, 
    country={Bangladesh}}

\begin{abstract}
''' + abstract_text + r'''
\end{abstract}

\begin{keywords}
Biomedical text mining \sep Unsupervised clustering \sep BioBERT \sep MeSH ontology grounding \sep Disease comorbidity network \sep TF-IDF \sep HDBSCAN \sep UMAP \sep PubMed abstracts \sep Topic coherence
\end{keywords}

\maketitle

'''

# Add \printcredits right before \begin{thebibliography}
bib_idx = body.find(r'\begin{thebibliography}')
if bib_idx != -1:
    body = body[:bib_idx] + '\\printcredits\n\n' + body[bib_idx:]

full_content = preamble + body

with open('Elsevier_LaTeX/main.tex', 'w', encoding='utf-8') as f:
    f.write(full_content)

print('Clean Elsevier_LaTeX/main.tex written, size:', len(full_content))
