import os
import re
import subprocess
import time

# Parse workers
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
        'worker': workers[6],
        'slug': 'nishat1156/exp7-mesh-ontology',
        'out_dir': 'Q1_Experiments_Results/exp7_mesh_ontology',
        'done': False
    },
    {
        'worker': workers[7],
        'slug': 'afrojahaqueshornaly/exp8-disease-network',
        'out_dir': 'Q1_Experiments_Results/exp8_disease_network',
        'done': False
    },
    {
        'worker': workers[8],
        'slug': 'abdullahalsayfan/exp9-scibert-sbert',
        'out_dir': 'Q1_Experiments_Results/exp9_scibert_sbert',
        'done': False
    }
]

print("=== Monitoring Q1 Defense Experiments on Kaggle Cloud ===")

max_wait = 900  # 15 minutes max
start_time = time.time()

while time.time() - start_time < max_wait:
    all_finished = True
    for t in tasks:
        if t['done']:
            continue
        
        env = os.environ.copy()
        env['KAGGLE_API_TOKEN'] = t['worker']['token']
        
        res = subprocess.run(
            ["python", "-m", "kaggle", "kernels", "status", t['slug']],
            env=env,
            capture_output=True,
            text=True
        )
        status_line = res.stdout.strip()
        print(f"[{time.strftime('%H:%M:%S')}] {t['slug']}: {status_line}")
        
        if "has status \"complete\"" in status_line:
            print(f"--> {t['slug']} COMPLETED! Pulling results to {t['out_dir']}...")
            os.makedirs(t['out_dir'], exist_ok=True)
            pull_res = subprocess.run(
                ["python", "-m", "kaggle", "kernels", "output", t['slug'], "-p", t['out_dir']],
                env=env,
                capture_output=True,
                text=True
            )
            print(pull_res.stdout.strip())
            t['done'] = True
        elif "has status \"error\"" in status_line:
            print(f"--> {t['slug']} FAILED with ERROR!")
            t['done'] = True
        else:
            all_finished = False

    if all_finished:
        print("\nAll defense experiments have concluded!")
        break
    
    time.sleep(20)

print("Monitoring loop finished.")
