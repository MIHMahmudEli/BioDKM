import os
import re

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

print(f"Total workers parsed: {len(workers)}")
for i, w in enumerate(workers):
    wid = w.get('id', f'worker_{i+1}')
    u = w['username']
    tok_pre = w['token'][:8]
    print(f"{wid}: username={u}, token_prefix={tok_pre}...")
