import os
import re
import subprocess
import time

# Parse workers from .env
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

# Map assignments
tasks = [
    {
        'worker': workers[6], # worker 7: nishat1156
        'dir': 'kaggle_experiments/exp7_mesh_ontology',
        'slug': 'nishat1156/exp7-mesh-ontology'
    },
    {
        'worker': workers[7], # worker 8: afrojahaqueshornaly
        'dir': 'kaggle_experiments/exp8_disease_network',
        'slug': 'afrojahaqueshornaly/exp8-disease-network'
    },
    {
        'worker': workers[8], # worker 9: abdullahalsayfan
        'dir': 'kaggle_experiments/exp9_scibert_sbert',
        'slug': 'abdullahalsayfan/exp9-scibert-sbert'
    }
]

print("=== Launching Q1 Defense Experiments to Kaggle Cloud ===")

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

print("\nAll 3 defense kernels dispatched to Kaggle!")
