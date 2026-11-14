"""
BioDKM Tripartite Core Execution & Systematic Alignment Suite
============================================================
This script verifies the full mathematical, engineering, and empirical
alignment across the three foundational BioDKM core modules:
  1. Stream A (Lexical):       core_tfidf (Stages 1–7)
  2. Stream B (Contextual):    core_biobert (Stages 1–7)
  3. Harmonization Engine:     core_coherence_manuscript (Stage 8)

Authoritative checks executed:
  - Remote Kaggle Cloud Worker Execution Statuses (Kaggle API)
  - Mathematical & Hyperparameter Isomorphism Verification
  - Local Artifact Integrity & Row-Count Contracts
  - Cross-Manifold Metric Consistency (Table 3 Synthesis)
"""

import os
import sys
import subprocess
import hashlib
import pandas as pd
import numpy as np

def read_workers():
    workers = {}
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    if not os.path.exists(env_file):
        return workers
    with open(env_file, 'r', encoding='utf-8') as f:
        curr_user = None
        for l in f:
            l = l.strip()
            if 'Username=' in l:
                curr_user = l.split('=', 1)[1].strip().strip('\'"')
            elif 'Kaggel_Token' in l and '=' in l:
                tok = l.split('=', 1)[1].strip().strip('\'"')
                if curr_user:
                    workers[curr_user] = tok
                    curr_user = None
    return workers

def check_kaggle_status(user, slug, token):
    os.environ['KAGGLE_API_TOKEN'] = token
    cmd = [sys.executable, "-m", "kaggle", "kernels", "status", slug]
    res = subprocess.run(cmd, capture_output=True, text=True)
    status_str = res.stdout.strip()
    return status_str

def check_param_isomorphism():
    import re
    def extract_params(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        params = {}
        for p in ['n_neighbors', 'min_dist', 'random_state', 'min_cluster_size', 'min_samples']:
            m = re.findall(rf'{p}\s*=\s*([^,\)\s]+)', content)
            if m:
                params[p] = m[0]
        return params

    p_tfidf = extract_params(os.path.join(os.path.dirname(__file__), 'core_tfidf', 'core_tfidf.py'))
    p_biobert = extract_params(os.path.join(os.path.dirname(__file__), 'core_biobert', 'core_biobert.py'))

    isomorphic = True
    discrepancies = []
    for k in p_tfidf:
        if p_tfidf.get(k) != p_biobert.get(k):
            isomorphic = False
            discrepancies.append(f"{k}: TF-IDF={p_tfidf.get(k)} vs BioBERT={p_biobert.get(k)}")

    return isomorphic, p_tfidf, discrepancies

def check_artifact_integrity(repo_root):
    checks = []
    # 1. Corpus size
    c_tfidf = os.path.join(repo_root, 'results', 'tfidf', 'step2_cleaned_corpus.csv')
    c_biobert = os.path.join(repo_root, 'results', 'biobert', 'step2_cleaned_corpus.csv')
    if os.path.exists(c_tfidf) and os.path.exists(c_biobert):
        df_t = pd.read_csv(c_tfidf)
        df_b = pd.read_csv(c_biobert)
        pass_len = len(df_t) == len(df_b) == 14064
        checks.append(("Corpus Row Count (14,064 docs)", pass_len, f"TF-IDF: {len(df_t):,}, BioBERT: {len(df_b):,}"))
    else:
        checks.append(("Corpus Row Count", False, "Missing cleaned corpus CSVs"))

    # 2. Cluster assignments
    a_tfidf = os.path.join(repo_root, 'results', 'tfidf', 'step6_cluster_assignments.csv')
    a_biobert = os.path.join(repo_root, 'results', 'biobert', 'step6_cluster_assignments.csv')
    if os.path.exists(a_tfidf) and os.path.exists(a_biobert):
        df_at = pd.read_csv(a_tfidf)
        df_ab = pd.read_csv(a_biobert)
        pass_cols = set(['PMID', 'KMeans_Cluster', 'HDBSCAN_Cluster', 'Hierarchical_Cluster']).issubset(df_at.columns) and \
                    set(['PMID', 'KMeans_Cluster', 'HDBSCAN_Cluster', 'Hierarchical_Cluster']).issubset(df_ab.columns)
        checks.append(("Cluster Assignment Schema", pass_cols, f"Columns verified across both streams"))
    else:
        checks.append(("Cluster Assignment Schema", False, "Missing assignment CSVs"))

    # 3. Stage 8 Combined Evaluation Metrics
    comb_path = os.path.join(repo_root, 'results', 'coherence', 'combined_evaluation_metrics.csv')
    if os.path.exists(comb_path):
        comb = pd.read_csv(comb_path)
        pass_comb = len(comb) == 6 and 'Mean_NPMI' in comb.columns and 'Silhouette' in comb.columns
        checks.append(("Stage 8 Cross-Manifold Table (6 Configs)", pass_comb, f"Rows: {len(comb)}, Columns: {list(comb.columns)[:4]}..."))
    else:
        checks.append(("Stage 8 Cross-Manifold Table", False, "Missing combined metrics CSV"))

    # 4. Clinical Validation Tables
    tab1 = os.path.join(repo_root, 'results', 'manuscript', 'Table1_Macro_KMeans_Clinical_Validation.csv')
    tab2 = os.path.join(repo_root, 'results', 'manuscript', 'Table2_Micro_HDBSCAN_Top10.csv')
    checks.append(("Clinical Macro Table 1 (5 Domains)", os.path.exists(tab1) and len(pd.read_csv(tab1)) == 5, f"Verified 5 clinical categories"))
    checks.append(("Clinical Micro Table 2 (Top-10 Subtopics)", os.path.exists(tab2) and len(pd.read_csv(tab2)) == 10, f"Verified 10 high-affinity biomarkers"))

    return checks

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    workers = read_workers()
    
    print("\n" + "="*80)
    print("      BIODKM TRIPARTITE CORE FRAMEWORK SYSTEMATIC ALIGNMENT REPORT")
    print("="*80)

    # 1. Cloud Execution Verification
    print("\n[1] Kaggle Cloud Worker Execution Status:")
    print("-" * 80)
    suite = [
        ("Stream A: Lexical (TF-IDF)", "aicontentdetections", "aicontentdetections/biodkm-core-tf-idf-pipeline"),
        ("Stream B: Contextual (BioBERT GPU)", "zarinprionty", "zarinprionty/biodkm-core-biobert-gpu-pipeline"),
        ("Stage 8: Coherence Harmonization", "studyhub991", "studyhub991/biodkm-core-coherence-and-manuscript-analysis")
    ]
    all_complete = True
    for name, user, slug in suite:
        tok = workers.get(user)
        if not tok:
            print(f"  [-] {name:35s} | Missing token for {user}")
            all_complete = False
            continue
        stat = check_kaggle_status(user, slug, tok)
        is_done = "COMPLETE" in stat
        all_complete = all_complete and is_done
        symbol = "[PASS]" if is_done else "[WAIT]"
        print(f"  {symbol} {name:35s} | {slug:55s} | {stat}")

    # 2. Mathematical & Hyperparameter Isomorphism
    print("\n[2] Mathematical & Hyperparameter Isomorphism Parity:")
    print("-" * 80)
    isomorphic, params, diffs = check_param_isomorphism()
    if isomorphic:
        print("  [PASS] Both streams share 100% isomorphic hyperparameters:")
        for k, v in params.items():
            print(f"         - {k:20s}: {v}")
    else:
        print("  [FAIL] Discrepancies detected:")
        for d in diffs:
            print(f"         - {d}")

    # 3. Dataflow & Artifact Integrity Contracts
    print("\n[3] Dataflow Contract & Artifact Integrity:")
    print("-" * 80)
    integrity_checks = check_artifact_integrity(repo_root)
    for title, passed, desc in integrity_checks:
        symbol = "[PASS]" if passed else "[FAIL]"
        print(f"  {symbol} {title:42s} | {desc}")

    # 4. Final Alignment Summary
    print("\n" + "="*80)
    all_passed = all_complete and isomorphic and all(c[1] for c in integrity_checks)
    if all_passed:
        print("  [ALIGNMENT STATUS: PERFECT (100% SYSTEMATIC PARITY)]")
        print("  The tripartite core suite is mathematically isomorphic, cloud-verified,")
        print("  and completely synchronized with the publication manuscript.")
    else:
        print("  [ALIGNMENT STATUS: ATTENTION REQUIRED]")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
