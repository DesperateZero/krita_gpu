#!/usr/bin/env python3
"""Same checked event arithmetic; D2 has two configs/eight samples each."""
import subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
t=(H/'analyze.py').read_text()
changes={
    "H/'matrix/results.json'":"H/'h2-matrix/results.json'",
    "['raw','off','outer','facts']":"['coarse','h2']",
    "[('raw','off'),('off','outer'),('outer','facts')]":"[('coarse','h2')]",
    "outer=modes['outer'];facts=modes['facts']":"outer=modes['coarse'];facts=modes['h2']",
    "['outer','facts']":"['coarse','h2']",
    "H/'summary.json'":"H/'h2-summary.json'",
    "H/'PROTOCOL.md'":"H/'SUPPLEMENT.md'",
    "H/'run.py'":"H/'generated_h2_runner.py'",
    "fixed 4-process/config descriptive evidence":"fixed 8-process/config descriptive evidence",
    "next(r['stroke_cpu_ms'] for r in processes if r['configuration']==after and r['block']==b)-\n        next(r['stroke_cpu_ms'] for r in processes if r['configuration']==before and r['block']==b)":"statistics.mean(r['stroke_cpu_ms'] for r in processes if r['configuration']==after and r['block']==b)-\n        statistics.mean(r['stroke_cpu_ms'] for r in processes if r['configuration']==before and r['block']==b)",
}
for a,b in changes.items():
    assert a in t,a;t=t.replace(a,b)
target=H/'generated_h2_analyzer.py'
if target.exists():assert target.read_text()==t
else:target.write_text(t)
subprocess.run([sys.executable,str(target)],check=True)
