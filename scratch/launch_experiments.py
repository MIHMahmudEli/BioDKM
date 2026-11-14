import os
import subprocess

workers = [
    {
        'id': 'exp1_alignment',
        'slug': 'nihanshadman/exp1-disease-alignment-benchmark',
        'dir': r'kaggle_experiments\exp1_alignment',
        'token': 'KGAT_07a1611e703a27debfc1e563b9a281ba'
    },
    {
        'id': 'exp2_pubmedbert',
        'slug': 'tasnimjenny/exp2-pubmedbert-benchmark',
        'dir': r'kaggle_experiments\exp2_pubmedbert',
        'token': 'KGAT_74cdeabb5280337f13b4a3b6f77f74dc'
    },
    {
        'id': 'exp3_baselines',
        'slug': 'mdzihan/exp3-baseline-topic-models',
        'dir': r'kaggle_experiments\exp3_baselines',
        'token': 'KGAT_5bd994870190c12169ff718c090ab1d3'
    },
    {
        'id': 'exp4_ablation',
        'slug': 'rssiam/exp4-dim-reduction-ablation',
        'dir': r'kaggle_experiments\exp4_ablation',
        'token': 'KGAT_832fc862524e9fb55dde38024d9251a6'
    },
    {
        'id': 'exp5_sensitivity',
        'slug': 'leyamridha/exp5-hyperparameter-sensitivity',
        'dir': r'kaggle_experiments\exp5_sensitivity',
        'token': 'KGAT_852b6f0480db5783edcee414d44acefd'
    }
]

print("=== Pushing Updated Kernels (Exp 1 - 5) ===")
for w in workers:
    env = os.environ.copy()
    env['KAGGLE_API_TOKEN'] = w['token']
    cmd = ['python', '-m', 'kaggle', 'kernels', 'push', '-p', w['dir']]
    print(f"Pushing {w['id']} ({w['slug']})...")
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"  SUCCESS: {res.stdout.strip()}")
    else:
        print(f"  FAILED: {res.stderr.strip()} (STDOUT: {res.stdout.strip()})")
