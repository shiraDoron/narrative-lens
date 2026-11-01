from pathlib import Path
import subprocess,sys,time
p=Path(__file__).resolve().parent
while not (p/'generator_manifest.json').exists():time.sleep(5)
with (p/'run.log').open('a',encoding='utf8') as log:
    result=subprocess.run([sys.executable,'-u',str(p/'run_remaining.py')],stdout=log,stderr=subprocess.STDOUT)
sys.exit(result.returncode)
