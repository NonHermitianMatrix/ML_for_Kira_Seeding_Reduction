"""Summarize non-overlapping diagnostic log intervals and existing native timers."""
from pathlib import Path
import json,gzip,collections,statistics,hashlib
root=Path(__file__).resolve().parents[2]
p=Path(__file__).resolve().parent
assert json.loads((p/'completed.json').read_text())['count']==12
groups=collections.defaultdict(list);records=[]
for f in sorted(p.glob('equation_test_*_events.json')):
 events=json.loads(f.read_text());name=f.name.replace('_events.json','')
 r=json.load(gzip.open(p/(name+'.json.gz'),'rt'));assert r['success'] and r['reference_checked']
 def first(text):return next(x['elapsed'] for x in events if x['line'].startswith(text))
 def last(text):return next(x['elapsed'] for x in reversed(events) if x['line'].startswith(text))
 a=first('***** Select equations recursively');b=first('***** Bring system in triangular')
 c=first('***** Run the back substitution');d=first('Kira committed results');e=last('process_exit')
 vals={'total':r['complete_seconds'],'family_and_initial_setup':a,'equation_preparation':b-a,'triangular_with_transfer':c-b,'back_substitution_with_commit':d-c,'export_and_exit':e-d,'outside_wrapper':r['complete_seconds']-e}
 assert abs(sum(v for k,v in vals.items() if k!='total')-vals['total'])<1e-8
 vals['setup_and_equation_fraction']=b/vals['total']
 groups[r['case']].append(vals)
 records.append({'case':r['case'],'file':str(f.relative_to(root)),'seconds':vals,'worker_host':r['worker_host'],'success':True,'peak_scratch_bytes':r['peak_scratch_bytes'],'peak_rss_bytes':r['peak_rss_bytes']})
summary={'scope':'diagnostic profile of current native baseline, frozen models unchanged','runs':len(records),'all_exact':True,'timing_note':'Includes timestamp-wrapper and logging costs. Nonoverlapping native output intervals are broader than internal function timers. Fresh node timings do not replace published benchmark times or imply speedup. Separately computed medians need not add exactly.','groups':{case:{'repetitions':len(rows),'median_seconds':{k:statistics.median(r[k] for r in rows) for k in rows[0]}} for case,rows in groups.items()},'records':records}
summary['source_sha256']={str(x.relative_to(root)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [p/'s00_timestamp.py',p/'s01_profile.py',p/'s03_profile_run.py',p/'s04_summarize.py',root/'ML_model_equation_selection/s03_run.py',root/'.tools/kira-equation-selection/kira-lazy']}
(p/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'runs':summary['runs'],'all_exact':summary['all_exact'],'groups':summary['groups'],'audit_allocated_bytes':sum(x.stat().st_blocks*512 for x in p.iterdir() if x.is_file())},indent=2))
