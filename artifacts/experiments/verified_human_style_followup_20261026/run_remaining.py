"""Run remaining stages with durable UTF-8 logs and real subprocess exit codes."""
from pathlib import Path
import subprocess,sys,time,json,os,hashlib
P=Path(__file__).resolve().parent
with (P/'run.log').open('a',encoding='utf8') as log:
    for stage in ['generate','validate','evaluate','report']:
        if stage=='validate':
            # The laptop has 16GB: serialize large models rather than page them.
            import psutil
            manifest=json.loads((P/'server_process.json').read_text())
            try:
                process=psutil.Process(manifest['pid'])
                if P.name in ' '.join(process.cmdline()):process.terminate();process.wait(timeout=20)
            except psutil.NoSuchProcess:pass
            subprocess.run([sys.executable,'-u',str(P/'annotate_nli.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
            subprocess.run([sys.executable,str(P/'assemble_annotations.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
        if stage=='evaluate':
            frozen={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in P.glob('*.py')}
            (P/'analysis_code_before_results_sha256.json').write_text(json.dumps(frozen,indent=2),encoding='utf8')
        if stage=='report':
            while not (P/'independent_nli_annotations.csv').exists():time.sleep(5)
            subprocess.run([sys.executable,str(P/'assemble_annotations.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
        command=[sys.executable,'-u',str(P/'generate_light.py')] if stage=='generate' else [sys.executable,'-u',str(P/'experiment.py'),'--stage',stage]
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    subprocess.run([sys.executable,str(P/'write_results_digest.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
    subprocess.run([sys.executable,str(P/'integrity.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
    subprocess.run([sys.executable,str(P/'final_audit.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
print('Follow-up stages complete',flush=True)
