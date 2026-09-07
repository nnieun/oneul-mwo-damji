"""Record actual TypeScript and Vite build results as Markdown."""
import datetime
import os
from pathlib import Path
import shutil
import subprocess
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import time
root=Path(__file__).resolve().parents[1]
node=os.getenv('NODE_BINARY') or shutil.which('node')
if not node:
    raise SystemExit('Node was not found. Set NODE_BINARY or add node to PATH.')
report=root/'docs/test-results/F07-frontend.md'
base=subprocess.check_output(['git','rev-parse','--short','HEAD'],cwd=root,text=True).strip()
failed=False
with report.open('a',encoding='utf-8') as out:
    out.write(f'\n# Frontend verification\n\n- Started: {datetime.datetime.now().astimezone().isoformat()}\n- Base commit: {base} + working tree\n- Runtime: {subprocess.check_output([node,"--version"],text=True).strip()}\n')
    for label,args in [('TypeScript',['node_modules/typescript/bin/tsc','--noEmit']),('Production build',['node_modules/vite/bin/vite.js','build'])]:
        start=time.monotonic()
        result=subprocess.run([node,*args],cwd=root/'frontend',stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace')
        out.write(f'\n## {label}\n\n- Command: `node {" ".join(args)}`\n- Exit code: {result.returncode}\n- Result: {"PASS" if result.returncode==0 else "FAIL"}\n- Duration: {time.monotonic()-start:.2f}s\n\n```text\n{result.stdout}\n```\n')
        print(f'{label}: exit {result.returncode}')
        print(result.stdout)
        failed=failed or result.returncode!=0
sys.exit(1 if failed else 0)
