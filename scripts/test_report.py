"""Run pytest and append the actual result to a versioned Markdown report."""
import datetime
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[1]
feature, *targets = sys.argv[1:]
command = [sys.executable, '-m', 'pytest', '-v', *targets]
started = datetime.datetime.now().astimezone().isoformat()
base = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=root, text=True).strip()
env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
t0 = time.monotonic()
result = subprocess.run(command, cwd=root / 'backend', env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', errors='replace')
report = root / 'docs' / 'test-results' / f'{feature}.md'
report.parent.mkdir(parents=True, exist_ok=True)
with report.open('a', encoding='utf-8') as out:
    out.write(f'\n# {feature} 테스트 실행\n\n- 실행 일시: {started}\n- 환경: {platform.platform()}, Python {platform.python_version()}\n- 기준 커밋: {base} + 해당 기능 작업 트리\n- 실행 위치: backend\n- 실행 명령: `python -m pytest -v {" ".join(targets)}`\n- 종료 코드: {result.returncode}\n- 결과: {"PASS" if result.returncode == 0 else "FAIL"}\n- 소요 시간: {time.monotonic()-t0:.2f}초\n\n## 실제 실행 로그 (항목별 결과·집계)\n\n```text\n{result.stdout}\n```\n\n- 실제 카메라·Roboflow 검증은 별도 hardware 테스트 및 시연 기록을 따른다.\n')
print(result.stdout)
print(f'Report: {report}')
sys.exit(result.returncode)
