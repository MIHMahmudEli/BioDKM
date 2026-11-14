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

w13 = workers[12] # almasukmim12
slug = 'almasukmim12/exp13-word-intrusion'
path = 'kaggle_experiments/exp13_word_intrusion'
out_dir = 'Q1_Experiments_Results/exp13_word_intrusion'

print(f"=== Pushing Exp 13 Version 3 ({slug}) ===")
env = os.environ.copy()
env['KAGGLE_API_TOKEN'] = w13['token']

res = subprocess.run(
    ["python", "-m", "kaggle", "kernels", "push", "-p", path],
    env=env,
    capture_output=True,
    text=True
)
print(res.stdout.strip())
if res.stderr.strip():
    print("ERR:", res.stderr.strip())

print("\n=== Monitoring Exp 13 ===")
for cycle in range(1, 40):
    time.sleep(15)
    status_res = subprocess.run(
        ["python", "-m", "kaggle", "kernels", "status", slug],
        env=env,
        capture_output=True,
        text=True
    )
    s = status_res.stdout.strip()
    print(f"[{cycle}] {s}", flush=True)
    if "complete" in s.lower():
        print(f"Pulling output to {out_dir}...")
        subprocess.run(
            ["python", "-m", "kaggle", "kernels", "output", slug, "-p", out_dir],
            env=env,
            capture_output=True,
            text=True
        )
        # Flatten if downloaded in subdir
        sub = os.path.join(out_dir, 'exp13_word_intrusion_results')
        if os.path.exists(sub):
            for f in os.listdir(sub):
                os.replace(os.path.join(sub, f), os.path.join(out_dir, f))
            os.rmdir(sub)
        print("Exp 13 finished and downloaded successfully!")
        break
    elif "error" in s.lower():
        print("Exp 13 failed with error, pulling logs...")
        subprocess.run(
            ["python", "-m", "kaggle", "kernels", "output", slug, "-p", out_dir],
            env=env,
            capture_output=True,
            text=True
        )
        break
