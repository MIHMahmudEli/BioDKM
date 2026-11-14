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
    },
    {
        'id': 'exp6_stats',
        'slug': 'sadmanhasanmiraj/exp6-statistical-significance',
        'token': 'KGAT_564e33a38aa3dcaca0a34acf0eb71de6',
        'out_dir': r'Q1_Experiments_Results\exp6_stats'
    }
]

def check_status(w):
    env = os.environ.copy()
    env['KAGGLE_API_TOKEN'] = w['token']
    res = subprocess.run(['python', '-m', 'kaggle', 'kernels', 'status', w['slug']], env=env, capture_output=True, text=True)
    out = res.stdout.strip()
    return out

def download_output(w):
    os.makedirs(w['out_dir'], exist_ok=True)
    env = os.environ.copy()
    env['KAGGLE_API_TOKEN'] = w['token']
    res = subprocess.run(['python', '-m', 'kaggle', 'kernels', 'output', w['slug'], '-p', w['out_dir']], env=env, capture_output=True, text=True)
    return res.stdout.strip()

print("Status check for all 6 experiments:")
for w in workers:
    st = check_status(w)
    print(f"[{w['id']}] {w['slug']} -> {st}")
