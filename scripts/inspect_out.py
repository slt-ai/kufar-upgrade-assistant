import json
from pathlib import Path

p = Path('D:/Work/AI/ClaudeCode/research-agent/scripts/_kit_analyzer_out.json')
with open(p, 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Intel top3:')
for c in data['intel']['top3']:
    print(c['rank'], c['motherboard']['title'], '+', c['cpu']['title'], c['kit_price_byn'], c['cpu_perf'], c['quality_score'])

print('\nIntel future_ready:')
for c in data['intel']['future_ready']:
    print(c['rank'], c['motherboard']['title'], '+', c['cpu']['title'], c['kit_price_byn'], c['cpu_perf'], c['quality_score'])

print('\nAMD top3:')
for c in data['amd']['top3']:
    print(c['rank'], c['motherboard']['title'], '+', c['cpu']['title'], c['kit_price_byn'], c['cpu_perf'], c['quality_score'])

print('\nAMD future_ready:')
for c in data['amd']['future_ready']:
    print(c['rank'], c['motherboard']['title'], '+', c['cpu']['title'], c['kit_price_byn'], c['cpu_perf'], c['quality_score'])
