"""Finish application checks, documentation, and the evidence audit."""
import ast,json,os,re,subprocess,sys
from s00_policy import *

def main():
 for folder,graphs in [('initial_test',['double_box']),('model_test',['double_box','nonplanar_box'])]:
  for g in graphs:
   f=rt.read(HERE/folder/(g+'_completion.json'));assert f['complete']
   for n,h in f.get('hashes',{}).items():assert inputs.sha(HERE/n)==h,n
 for n in ['s09_application.py','s12_check_integration.py','s08_analyze.py','s10_document.py']:
  subprocess.run([sys.executable,str(HERE/n)],check=True)
 d=rt.read(HERE/'summary.json');a=d['adaptive'];i=d['initial']
 app=rt.read(HERE/'application/summary.json');integration=rt.read(HERE/'integration_test/summary.json')
 assert app['all_exact'] and app['requests']==48 and app['matched']==4
 assert integration['all_exact'] and integration['requests']==24
 assert all(v['all_successful_outputs_exact'] for v in [i,a])
 assert not a['failed_trials'] and not a['failed_references']
 for folder in ['initial_test','model_test']:
  for path in (HERE/folder).glob('*.json.gz'):
   r=rt.read(path)
   assert not r.get('reference_coefficients_supplied',False),path.name
   if r['success']:assert r.get('reference_checked') and not r.get('mismatches'),path.name
   if r['method']=='native':
    assert not r.get('selection',{}).get('prediction_used') and r.get('seed_policy') is None
    for attempt in r['attempts']:
     assert attempt.get('equation_mode','off')=='off'
     assert not attempt.get('weights_sha256') and not attempt.get('model')
 for path in (HERE/'trained_model').glob('cost_*.json'):
  for n,h in rt.read(path)['source_sha256'].items():assert inputs.sha(HERE/n)==h,n
 def replace(p,key,body):
  s=p.read_text();start='<!-- BEGIN '+key+' -->';end='<!-- END '+key+' -->';block=start+'\n'+body+'\n'+end
  if start in s:s=re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:block,s,flags=re.S)
  else:s+='\n\n'+block+'\n'
  p.write_text(s)
 def percent(r):return f'{abs(1-r)*100:.1f}% '+('less' if r<=1 else 'more')+' time'
 summary='The first evolved seed boundary uses '+percent(i['comparisons']['learned_to_native']['ratio'])+' than tuned native Kira on eight planar requests.\nIt uses '+percent(i['comparisons']['learned_to_fixed']['ratio'])+' than the initial fixed-width control.\nThe broader selected workflow uses '+percent(a['comparisons']['learned_to_native']['ratio'])+' than tuned native Kira on '+str(a['matched'])+' matched two-loop requests.\nIt uses '+percent(a['comparisons']['learned_to_previous']['ratio'])+' than the preceding application.\nIts comparison with the fixed sparse control gives '+percent(a['comparisons']['learned_to_fixed']['ratio'])+'.\nAll successful outputs pass exact coefficient checks.\nThe fixed sparse control can use a boundary discovered during training.\nSee `summary.json` for intervals, individual times, failures, and scope.\n'
 for graph in ['double_box','nonplanar_box']:
  summary+=graph+(': Validation enables the cost predictor.\n' if d['models']['cost_'+graph]['enabled'] else ': Validation retains the fixed sparse boundary.\n')
 replace(HERE/'README.md','MEASURED RESULTS',summary)
 replace(HERE/'README.md','FINISH SCRIPT','Run `s14_finish.py` after both reserved test jobs and the validation helper finish.\nIt checks the application, writes both documents, and checks their evidence.\nIt does not publish files or change fitted models.')
 replace(HERE/'auxiliary_validation/README.md','SHARED RECORDS','Timing records from this worker are in `../supplementary_validation/`.\n`promotion.json` lists completed records copied into the main validation set.\n`s00_execution_snapshot.py` preserves the first helper version.\nThe corrected parent script reuses its completed timings and fixes record promotion.\nThe correction changes no seed boundary or measured reduction.\nNo reserved result enters validation.')
 command='Use `ML_model_seed_selection/cost_geometry/s11_integrated.py` for the updated application.\nSee [the seed-policy guide](ML_model_seed_selection/cost_geometry/README.md) for inputs, execution, and controls.\n'+summary.replace('`summary.json`','`ML_model_seed_selection/cost_geometry/summary.json`')
 replace(ROOT/'README.md','COST-TRAINED SEED APPLICATION',command)
 replace(ROOT/'README.md','ADAPTIVE REDUCTION','\n## Current reduction interface\n\nUse [the integrated seed-policy application](ML_model_seed_selection/cost_geometry/README.md).\nIt first checks the exact scalar massless banana formula.\nIt then applies sparse seed selection in its validated domain.\nOther supported inputs use the preceding Kira batch and equation workflow.\nKira keeps native row elimination and exact algebra.\nValidation enables model predictions only when they improve complete time.\nNative reductions require a supplied master basis.\nRead the measured results and limits in the guide and paper.\nEarlier studies remain available for comparison.\nTheir speedup factors use different workloads and cannot be multiplied.\n')
 replace(ROOT/'ML_model_seed_selection/README.md','COST-TRAINED SEED STUDY','The [cost geometry study](cost_geometry/README.md) trains seed boundaries from complete Kira times.\nIt includes fitted models, separate test cases, exact checks, and the complete application.')
 replace(ROOT/'report/README.md','COST-TRAINED SEED RESULTS','`seed_geometry_results.tex` gives the new seed-policy measurements.\n`seed_geometry_appendix.tex` defines the model and derives its distance and counting formulas.\n`seed_geometry_data.json` contains the compact timing evidence.\nThe first evolved boundary and the broader cost-selection study have separate controls.\nBoth documents include these results.\nSee `../ML_model_seed_selection/cost_geometry/README.md` for the code and full records.')
 replace(ROOT/'report/paper_figures/README.md','SEED GEOMETRY FIGURE','`seed_geometry_times.pdf` compares complete time with tuned native and fixed sparse controls.\n`../../ML_model_seed_selection/cost_geometry/s10_document.py` generates the figure from saved test results.\nThe dashed line marks equal time.\nThe axes include this reference and every measured point.')
 replace(ROOT/'rules.md','SPARSE SEED COST TRAINING','Train seed choices from measured complete reduction time and integrate them before equation generation.\nCompare tuned native Kira, fixed sparse choices, and the preceding application on frozen reserved inputs.\nRetain exact checks, recovery, unsuccessful trials, and separate attribution for learned and fixed choices.\nKeep the report, notes, guides, cluster, repository, and local report current under the existing resource limits.')
 for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
 missing=[str(p) for p in HERE.rglob('*') if p.is_dir() and not (p/'README.md').exists()]
 assert not missing,missing
 subprocess.run(['make','-B','all'],cwd=ROOT/'report',check=True)
 subprocess.run([sys.executable,'s01_check_paper.py'],cwd=ROOT/'report',check=True)
 total=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
 assert total<20*1024**2,total
 audit=dict(complete=True,initial_timings=i['timings'],adaptive_timings=a['timings'],all_successful_outputs_exact=True,failed_cases_retained=True,controls_disable_all_ml=True,matched_requests=a['matched'],application_requests=app['requests'],integration_requests=integration['requests'],guard_checks=integration['guard_checks'],parity_checks=integration['model_parity_checks'],retained_bytes=total,summary_sha256=inputs.sha(HERE/'summary.json'),source_sha256={p.name:inputs.sha(p) for p in HERE.glob('*.py')},model_sha256={p.name:inputs.sha(p) for p in (HERE/'trained_model').glob('*.json')},pdf_sha256={n:inputs.sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']})
 inputs.write(HERE/'validation.json',audit);inputs.write(ROOT/'report/seed_geometry_validation.json',audit)
 print('FINISHED',json.dumps(audit),flush=True)

if __name__=='__main__':main()
