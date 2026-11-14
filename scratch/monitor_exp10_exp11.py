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

targets = [
    {
        'worker': workers[9], # baingalamukintu
        'slug': 'baingalamukintu/exp10-noise-ablation',
        'out_dir': 'Q1_Experiments_Results/exp10_noise_ablation',
        'done': False
    },
    {
        'worker': workers[10], # abhafnan
        'slug': 'abhafnan/exp11-subsampling-stability',
        'out_dir': 'Q1_Experiments_Results/exp11_subsampling_stability',
        'done': False
    }
]

for t in targets:
    os.makedirs(t['out_dir'], exist_ok=True)

print("=== Monitoring Kaggle Kernels Exp 10 and Exp 11 ===", flush=True)

max_wait_cycles = 60 # 60 * 20s = 20 mins max
cycle = 0

while cycle < max_wait_cycles:
    cycle += 1
    all_done = True
    print(f"\n--- Check Cycle {cycle} ({time.strftime('%H:%M:%S')}) ---", flush=True)
    
    for t in targets:
        if t['done']:
            print(f"[{t['slug']}]: Already COMPLETE and downloaded.", flush=True)
            continue
            
        env = os.environ.copy()
        env['KAGGLE_API_TOKEN'] = t['worker']['token']
        
        # Check status
        res = subprocess.run(
            ["python", "-m", "kaggle", "kernels", "status", t['slug']],
            env=env,
            capture_output=True,
            text=True
        )
        status_line = res.stdout.strip()
        print(f"[{t['slug']}]: {status_line}", flush=True)
        
        if "complete" in status_line.lower():
            print(f"[{t['slug']}]: Execution finished! Pulling outputs to {t['out_dir']}...", flush=True)
            down_res = subprocess.run(
                ["python", "-m", "kaggle", "kernels", "output", t['slug'], "-p", t['out_dir']],
                env=env,
                capture_output=True,
                text=True
            )
            print("Download output:", down_res.stdout.strip()[:150], flush=True)
            # Remove duplicate pubmed_dataset.csv if pulled
            dup_csv = os.path.join(t['out_dir'], 'pubmed_dataset.csv')
            if os.path.exists(dup_csv):
                os.remove(dup_csv)
                print(f"Cleaned duplicate {dup_csv}", flush=True)
            t['done'] = True
        elif "error" in status_line.lower():
            print(f"[{t['slug']}]: FAILED with error! Pulling logs...", flush=True)
            down_res = subprocess.run(
                ["python", "-m", "kaggle", "kernels", "output", t['slug'], "-p", t['out_dir']],
                env=env,
                capture_output=True,
                text=True
            )
            print(down_res.stdout.strip()[:150], flush=True)
            t['done'] = True
        else:
            all_done = False
            
    if all_done:
        print("\nAll target experiments completed and outputs pulled successfully!", flush=True)
        break
        
    time.sleep(20)

print("\n=== Monitoring complete. ===", flush=True)
