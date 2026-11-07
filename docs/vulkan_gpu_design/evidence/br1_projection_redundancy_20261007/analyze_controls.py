#!/usr/bin/env python3
"""Apply original frozen four-bucket statistic separately to Fresh and H4."""
import json,runpy,sys
from pathlib import Path
H=Path(__file__).resolve().parent
original=H.parent/'br1_m6_provider_borrow_20261006/analyze_fixed_m5_fresh.py'
copy=H/'control-analyzer.py';assert not copy.exists();copy.write_bytes(original.read_bytes())
for family in ['fresh','history']:
    sys.argv=[str(copy),'--round',f'controls-{family}','--output',str(H/f'controls-{family}-summary.json')]
    runpy.run_path(str(copy),run_name='__main__')
