import os
import subprocess
import time
import sys

workers = [
    {
        'id': 'exp1_alignment',
        'slug': 'nihanshadman/exp1-disease-alignment-benchmark',
        'token': 'KGAT_07a1611e703a27debfc1e563b9a281ba',
        'out_dir': r'Q1_Experiments_Results\exp1_alignment'
    },
    {
        'id': 'exp2_pubmedbert',
        'slug': 'tasnimjenny/exp2-pubmedbert-benchmark',
        'token': 'KGAT_74cdeabb5280337f13b4a3b6f77f74dc',
        'out_dir': r'Q1_Experiments_Results\exp2_pubmedbert'
    },
    {
        'id': 'exp3_baselines',
        'slug': 'mdzihan/exp3-baseline-topic-models',
        'token': 'KGAT_5bd994870190c12169ff718c090ab1d3',
        'out_dir': r'Q1_Experiments_Results\exp3_baselines'
    },
    {
        'id': 'exp4_ablation',
        'slug': 'rssiam/exp4-dim-reduction-ablation',
        'token': 'KGAT_832fc862524e9fb55dde38024d9251a6',
        'out_dir': r'Q1_Experiments_Results\exp4_ablation'
    },
    {
        'id': 'exp5_sensitivity',
        'slug': 'leyamridha/exp5-hyperparameter-sensitivity',
        'token': 'KGAT_852b6f0480db5783edcee414d44acefd',
        'out_dir': r'Q1_Experiments_Results\exp5_sensitivity'
    }
]

completed = set()

print("Monitoring Kaggle experiments (Exp 1 - 5)...")

for attempt in range(80): # Up to ~40 minutes
    all_done = True
    for w in workers:
        if w['id'] in completed:
            continue
            
        env = os.environ.copy()
        env['KAGGLE_API_TOKEN'] = w['token']
        res = subprocess.run(['python', '-m', 'kaggle', 'kernels', 'status', w['slug']], env=env, capture_output=True, text=True)
        st = res.stdout.strip()
        
        if "COMPLETE" in st:
            print(f"[{w['id']}] COMPLETED! Downloading outputs to {w['out_dir']}...")
            os.makedirs(w['out_dir'], exist_ok=True)
            dl_res = subprocess.run(['python', '-m', 'kaggle', 'kernels', 'output', w['slug'], '-p', w['out_dir']], env=env, capture_output=True, text=True)
            print(f"  Downloaded: {dl_res.stdout.strip()}")
            completed.add(w['id'])
        elif "ERROR" in st or "FAILED" in st:
            print(f"[{w['id']}] FAILED with status: {st}!")
            # Still download log for diagnosis
            os.makedirs(w['out_dir'], exist_ok=True)
            subprocess.run(['python', '-m', 'kaggle', 'kernels', 'output', w['slug'], '-p', w['out_dir']], env=env, capture_output=True, text=True)
            completed.add(w['id'])
        else:
            all_done = False
            print(f"[{w['id']}] Still running... ({st})")
            
    if all_done or len(completed) == len(workers):
        print(f"\nAll experiments completed ({len(completed)}/{len(workers)}).")
        break
        
    time.sleep(30)
