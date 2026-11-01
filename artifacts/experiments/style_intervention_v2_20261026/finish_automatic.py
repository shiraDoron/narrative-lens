"""Finish screening/reporting after the already-running generator safely stops.

Input: this directory's generation audit event. Outputs: validation, review pack,
Hebrew guide and artifact audit. This runner NEVER calls evaluate or fills human
review fields. Launch after study.py --stage generate has started.
"""
from pathlib import Path
import json, subprocess, sys, time

OUT=Path(__file__).resolve().parent


def main():
    """Wait for generation completion, then run dependent stages sequentially."""
    while True:
        events=OUT/'audit_trail.jsonl'
        records=[json.loads(line) for line in events.read_text(encoding='utf8').splitlines()] if events.exists() else []
        if any(record['stage']=='generate' for record in records):break
        time.sleep(10)
    for stage in ['validate','package','report']:
        print('Starting '+stage,flush=True)
        subprocess.run([sys.executable,'-u',str(OUT/'study.py'),'--stage',stage],check=True)
    subprocess.run([sys.executable,'-u',str(OUT/'audit.py')],check=True)
    print('Automatic work complete. Real human review is pending; no new model fitting performed.',flush=True)


if __name__=='__main__':main()
