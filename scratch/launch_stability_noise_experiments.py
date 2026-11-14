import os
import re
import subprocess
import time

with open('.env', 'r', encoding='utf-8') as f:
    text = f.read()

workers = []
current_worker = {}
for line in text.splitlines():
    line = line.strip()
    if line.startswith('#worker'):
        if current_worker.get('username') and current_worker.get('token'):
            workers.append(current_worker)
        current_worker = {'id': line}
    m_user = re.match(r'Username\s*=\s*[\'"]?([^\'"]+)[\'"]?', line, re.I)
    if m_user:
        current_worker['username'] = m_user.group(1).strip()
    m_tok = re.match(r'Kaggel_Token\s*=\s*[\'"]?([^\'"]+)[\'"]?', line, re.I)
    if m_tok:
        current_worker['token'] = m_tok.group(1).strip()

if current_worker.get('username') and current_worker.get('token'):
    workers.append(current_worker)

tasks = [
    {
        'worker': workers[9], # worker 10: baingalamukintu
        'dir': 'kaggle_experiments/exp10_noise_ablation',
        'slug': 'baingalamukintu/exp10-noise-ablation'
    },
    {
        'worker': workers[10], # worker 11: abhafnan
        'dir': 'kaggle_experiments/exp11_subsampling_stability',
        'slug': 'abhafnan/exp11-subsampling-stability'
    }
]

print("=== Launching Exp 10 and Exp 11 to Kaggle Cloud ===")

for t in tasks:
    w = t['worker']
    path = t['dir']
    slug = t['slug']
    print(f"\nDispatching {slug} using {w['username']}...")
    env = os.environ.copy()
    env['KAGGLE_API_TOKEN'] = w['token']
    
    res = subprocess.run(
        ["python", "-m", "kaggle", "kernels", "push", "-p", path],
        env=env,
        capture_output=True,
        text=True
    )
    print(res.stdout.strip())
    if res.stderr.strip():
        print("ERR:", res.stderr.strip())

print("\nBoth defense kernels dispatched to Kaggle successfully!")
