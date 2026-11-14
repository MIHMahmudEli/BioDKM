import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import matplotlib.patheffects as pe

# Set high-quality styling
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['mathtext.fontset'] = 'dejavusans'

# 1. Disease metadata & affinity matrix
diseases = [
    'Cardiovascular Disease',
    'Stroke Cerebrovascular',
    'Hypertension',
    'Diabetes Mellitus',
    'Cancer Neoplasm',
    'Alzheimer Disease',
    'Parkinson Disease',
    'Neurological Disorders'
]

# Read exact affinity matrix
aff_df = pd.read_csv('AJSE_LaTeX/tables/disease_comorbidity_matrix.csv', index_col=0)
print("Loaded affinity matrix:", aff_df.shape)

# Create high-resolution figure (17x9.6 inches for wide double-column layout)
fig = plt.figure(figsize=(17, 9.6), dpi=300, facecolor='#FAFBFD')

# Grid layout: Left = Network Graph (ax_net), Right = Clinical Axes Cards (ax_cards)
gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 0.85], left=0.03, right=0.97, bottom=0.04, top=0.92, wspace=0.12)
ax_net = fig.add_subplot(gs[0, 0])
ax_cards = fig.add_subplot(gs[0, 1])

# Figure Super-Title
fig.suptitle(
    "BioDKM: Unsupervised Biomedical Disease Knowledge Network & Comorbidity Landscape",
    fontsize=16, fontweight='bold', color='#0F172A', y=0.97
)

# -------------------------------------------------------------
# PANEL A: Topological Comorbidity Knowledge Network
# -------------------------------------------------------------
ax_net.set_facecolor('#FAFBFD')
ax_net.set_xlim(-1.58, 1.58)
ax_net.set_ylim(-1.58, 1.48)
ax_net.axis('off')

# Panel header
ax_net.text(-1.52, 1.38, "A", fontsize=18, fontweight='bold', color='#1E293B',
            bbox=dict(boxstyle='square,pad=0.2', fc='#E2E8F0', ec='none'))
ax_net.text(-1.40, 1.38, "Cross-Disease Topological Comorbidity Graph", fontsize=13, fontweight='bold', color='#1E293B', va='center')
ax_net.text(-1.40, 1.28, r"Edge width & color encode empirical comorbidity affinity ($\mathcal{A}_{ij} \geq 0.45$)",
            fontsize=9.5, color='#64748B', va='center')

# Color palette for 8 diseases
disease_colors = {
    'Cardiovascular Disease': '#E11D48',  # Rose / Crimson
    'Stroke Cerebrovascular': '#EA580C',  # Orange
    'Hypertension':           '#D97706',  # Amber
    'Diabetes Mellitus':      '#059669',  # Emerald
    'Cancer Neoplasm':        '#9333EA',  # Purple
    'Alzheimer Disease':      '#2563EB',  # Royal Blue
    'Parkinson Disease':      '#7C3AED',  # Violet
    'Neurological Disorders': '#0D9488'   # Teal
}

doc_counts = {
    'Cancer Neoplasm': 1951,
    'Diabetes Mellitus': 1922,
    'Stroke Cerebrovascular': 1880,
    'Alzheimer Disease': 1753,
    'Hypertension': 1747,
    'Cardiovascular Disease': 1722,
    'Neurological Disorders': 1586,
    'Parkinson Disease': 1504
}

# Arrange 8 nodes on circle of radius R=1.0
R = 1.0
angles = np.linspace(0, 2*np.pi, len(diseases), endpoint=False)
angles = (angles + np.pi/8) % (2*np.pi)

node_pos = {}
for i, d in enumerate(diseases):
    theta = angles[i]
    node_pos[d] = np.array([R * np.cos(theta), R * np.sin(theta)])

# Draw background subtle concentric reference rings
for r_bg in [0.35, 0.70, 1.0]:
    circle = plt.Circle((0, 0), r_bg, color='#E2E8F0', fill=False, lw=0.8, ls=':', zorder=1)
    ax_net.add_patch(circle)

# Draw central hub badge
hub = patches.Circle((0, 0), 0.16, fc='#FFFFFF', ec='#CBD5E1', lw=1.5, zorder=2)
ax_net.add_patch(hub)
ax_net.text(0, 0.03, "BioDKM", fontsize=9, fontweight='bold', color='#1E293B', ha='center', va='center', zorder=3)
ax_net.text(0, -0.05, "Manifold", fontsize=7.5, color='#64748B', ha='center', va='center', zorder=3)

# Extract and sort edges by affinity
edges_list = []
for i in range(len(diseases)):
    for j in range(i + 1, len(diseases)):
        d1, d2 = diseases[i], diseases[j]
        if d1 in aff_df.index and d2 in aff_df.columns:
            aff = float(aff_df.loc[d1, d2])
            if aff >= 0.45:
                edges_list.append((d1, d2, aff))

# Sort so highest affinity edges are drawn on top
edges_list.sort(key=lambda x: x[2])

# Colormap for affinity edges
cmap = plt.cm.magma

# Draw curved edges with Bezier curves
for d1, d2, aff in edges_list:
    p1 = node_pos[d1]
    p2 = node_pos[d2]
    
    # Normalized affinity [0.45, 0.85] -> [0.25, 0.90]
    norm_aff = (aff - 0.45) / (0.85 - 0.45)
    norm_aff = np.clip(norm_aff, 0.0, 1.0)
    
    edge_col = cmap(0.20 + 0.75 * norm_aff)
    lw = 1.2 + 7.0 * (norm_aff ** 1.3)
    alpha = 0.45 + 0.45 * norm_aff
    
    # Quadratic Bezier control point pulled toward center (0,0)
    p_mid = (p1 + p2) / 2.0
    dist_chord = np.linalg.norm(p1 - p2)
    ctrl = p_mid * (1.0 - 0.55 * (dist_chord / 2.0))
    
    verts = [p1, ctrl, p2]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    path = Path(verts, codes)
    
    patch = patches.PathPatch(path, facecolor='none', edgecolor=edge_col, lw=lw, alpha=alpha, zorder=2 + int(norm_aff*10))
    ax_net.add_patch(patch)
    
    # Highlight top clinical edges with numeric badge
    if aff >= 0.75:
        t = 0.5
        bx = (1-t)**2 * p1[0] + 2*(1-t)*t * ctrl[0] + t**2 * p2[0]
        by = (1-t)**2 * p1[1] + 2*(1-t)*t * ctrl[1] + t**2 * p2[1]
        
        ax_net.text(
            bx, by, f"{aff:.3f}",
            fontsize=7.5, fontweight='bold', color='#FFFFFF',
            ha='center', va='center', zorder=25,
            bbox=dict(boxstyle='round,pad=0.22', fc=edge_col, ec='#FFFFFF', lw=1.0, alpha=0.95),
            path_effects=[pe.withStroke(linewidth=1.5, foreground='black')]
        )

# Draw Nodes & Labels
for d, p in node_pos.items():
    col = disease_colors[d]
    cnt = doc_counts.get(d, 1700)
    
    # Outer glow
    outer_halo = patches.Circle(p, 0.12, fc=col, alpha=0.22, ec='none', zorder=12)
    ax_net.add_patch(outer_halo)
    
    # Middle white ring
    mid_ring = patches.Circle(p, 0.088, fc='#FFFFFF', ec=col, lw=2.2, zorder=13)
    ax_net.add_patch(mid_ring)
    
    # Inner colored core
    core = patches.Circle(p, 0.065, fc=col, ec='#FFFFFF', lw=1.2, zorder=14)
    ax_net.add_patch(core)
    
    # Text label position: push radially outward
    norm_p = p / np.linalg.norm(p)
    label_p = p + norm_p * 0.18
    
    if abs(norm_p[0]) < 0.25:
        ha = 'center'
    elif norm_p[0] > 0:
        ha = 'left'
    else:
        ha = 'right'
        
    va = 'center' if abs(norm_p[1]) < 0.6 else ('bottom' if norm_p[1] > 0 else 'top')
    
    words = d.split()
    if len(words) == 2:
        title_text = f"{words[0]}\n{words[1]}"
    elif len(words) == 3:
        title_text = f"{words[0]} {words[1]}\n{words[2]}"
    else:
        title_text = d
        
    ax_net.text(
        label_p[0], label_p[1],
        f"{title_text}\n($N={cnt:,}$)",
        fontsize=8.5, fontweight='bold', color='#1E293B',
        ha=ha, va=va, linespacing=0.92, zorder=20,
        bbox=dict(boxstyle='round,pad=0.25', fc='#FFFFFF', ec='#CBD5E1', lw=0.8, alpha=0.92)
    )

# Bottom Legend in Panel A
cbar_ax = ax_net.inset_axes([0.15, 0.02, 0.70, 0.028])
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0.45, vmax=0.85))
cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
cbar.set_label(r'Empirical Comorbidity Affinity $\mathcal{A}_{ij}$ (Cosine Metric in Topological Manifold)', fontsize=8.5, fontweight='bold', color='#334155', labelpad=4)
cbar.ax.tick_params(labelsize=8, color='#64748B')

# -------------------------------------------------------------
# PANEL B: Discovered Multidisciplinary Clinical Axes
# -------------------------------------------------------------
ax_cards.set_facecolor('#FAFBFD')
ax_cards.set_xlim(0, 1)
ax_cards.set_ylim(0, 1)
ax_cards.axis('off')

# Panel header
ax_cards.text(0.0, 0.98, "B", fontsize=18, fontweight='bold', color='#1E293B',
              bbox=dict(boxstyle='square,pad=0.2', fc='#E2E8F0', ec='none'))
ax_cards.text(0.08, 0.98, "Discovered Clinical Pathophysiological Axes", fontsize=13, fontweight='bold', color='#1E293B', va='center')
ax_cards.text(0.08, 0.935, "Cross-disease bridge topics automatically inferred without supervision", fontsize=9.5, color='#64748B', va='center')

cards_data = [
    {
        "title": "Cardio-Oncology Pathophysiological Axis",
        "pair": "Cancer Neoplasm   <--->   Cardiovascular Disease",
        "affinity": "0.8366",
        "topic": "Chemotherapeutic Cardiotoxicity & Shared Metabolic Stress",
        "keywords": ["case", "patient", "diagnosis", "cardiac toxicity", "troponin", "heart failure"],
        "clinical": "Captures the recognized cardiotoxic sequelae of modern antineoplastic therapies (e.g., anthracyclines, HER2 inhibitors) and shared chronic systemic inflammation.",
        "accent": "#9333EA"
    },
    {
        "title": "Cardio-Cerebrovascular Thromboembolic Axis",
        "pair": "Cardiovascular Disease   <--->   Stroke Cerebrovascular",
        "affinity": "0.8116",
        "topic": "Ischemic Infarction, Embolism & Arterial Shear Stress",
        "keywords": ["infarction", "ischemic", "carotid", "stenosis", "plaque", "thromboembolism"],
        "clinical": "Directly reconstructs the hemodynamic continuum where chronic hypertensive shear injury induces atheroma rupture and subsequent cerebral ischemic stroke.",
        "accent": "#EA580C"
    },
    {
        "title": "Vascular Cognitive Impairment & Dementia (VCID) Axis",
        "pair": "Alzheimer Disease   <--->   Stroke & Hypertension",
        "affinity": "0.7822 / 0.7810",
        "topic": "Cerebral Hypoperfusion, Small Vessel Disease & Amyloidosis",
        "keywords": ["microvascular", "hypoperfusion", "white matter", "amyloid beta", "ischemia"],
        "clinical": "Empirically uncovers vascular contributions to dementia, where microvascular rarefaction and ischemic white-matter lesions accelerate amyloid accumulation.",
        "accent": "#2563EB"
    },
    {
        "title": "Neurodegenerative Proteinopathy & Neuroinflammation Axis",
        "pair": "Alzheimer Disease   <--->   Parkinson's & Neurological",
        "affinity": "0.6148 / 0.6439",
        "topic": "Misfolded Protein Aggregates & Microglial Reactivity",
        "keywords": ["alpha-synuclein", "tau tangles", "microglia", "neuroinflammation", "dopamine"],
        "clinical": "Discovers shared degenerative cascades, including dual proteopathies (tau + alpha-synuclein), mitochondrial dysfunction, and neuroinflammatory pathways.",
        "accent": "#7C3AED"
    }
]

card_y_starts = [0.69, 0.46, 0.23, 0.00]
card_height = 0.205
card_w = 0.98

for idx, c in enumerate(cards_data):
    y0 = card_y_starts[idx]
    
    # Outer Card Background
    card_box = patches.FancyBboxPatch(
        (0.01, y0), card_w, card_height,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        fc='#FFFFFF', ec='#E2E8F0', lw=1.2, zorder=3
    )
    ax_cards.add_patch(card_box)
    
    # Left accent vertical stripe
    stripe = patches.FancyBboxPatch(
        (0.01, y0), 0.018, card_height,
        boxstyle="round,pad=0.0,rounding_size=0.01",
        fc=c["accent"], ec='none', zorder=4
    )
    ax_cards.add_patch(stripe)
    
    # Card Header: Title
    ax_cards.text(0.045, y0 + card_height - 0.030, c["title"], fontsize=9.8, fontweight='bold', color='#0F172A', va='center')
    
    # Affinity Badge
    badge_text = r"$\mathcal{A} = " + c['affinity'] + r"$"
    ax_cards.text(
        0.965, y0 + card_height - 0.030, badge_text,
        fontsize=8.5, fontweight='bold', color='#FFFFFF',
        ha='right', va='center',
        bbox=dict(boxstyle='round,pad=0.25', fc=c["accent"], ec='none')
    )
    
    # Connected Diseases
    ax_cards.text(0.045, y0 + card_height - 0.062, c["pair"], fontsize=8.4, fontweight='bold', color='#475569', va='center')
    
    # Thematic Bridge Banner
    topic_str = f"Thematic Bridge: {c['topic']}"
    ax_cards.text(0.045, y0 + card_height - 0.096, topic_str, fontsize=8.2, fontweight='bold', color='#1E293B', va='center')
    
    # Keywords Pill Tags
    kw_str = "Keywords:  " + "  •  ".join(c["keywords"][:5])
    ax_cards.text(0.045, y0 + card_height - 0.130, kw_str, fontsize=7.6, color='#0284C7', fontweight='semibold', va='center')
    
    # Clinical Mechanism sentence
    ax_cards.text(
        0.045, y0 + card_height - 0.165,
        c["clinical"],
        fontsize=7.3, color='#475569', style='italic', va='center',
        wrap=True
    )

# Save figure in both canonical destinations
for p in ['AJSE_LaTeX/figures/disease_knowledge_network.png', 'Q1_Experiments_Results/exp8_disease_network/disease_knowledge_network.png']:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    plt.savefig(p, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    print(f"Saved: {p}")

plt.close()
print("Figure 15 redesign complete!")
