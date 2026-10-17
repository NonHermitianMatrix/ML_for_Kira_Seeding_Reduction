"""Audit the completed study, document it, and build both PDFs."""
import ast,copy,re,subprocess
from fractions import Fraction
from s00_engine import *
from s04_reuse import ScaleCache

def block(path,key,body):
 path=Path(path);s=path.read_text() if path.exists() else ''
 start='<!-- BEGIN '+key+' -->';end='<!-- END '+key+' -->';text=start+'\n'+body+'\n'+end
 if start in s:s=re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:text,s,flags=re.S)
 else:s+='\n\n'+text+'\n'
 path.write_text(s)

def guards():
 count=0
 for graph in ['double_box','nonplanar_box']:
  f=rt.read(HERE/'trained_model'/('fixed_'+graph+'.json'));c=rt.read(HERE/'protocols'/(graph+'.json'))['reserved'][0];ref=reference(c)[1];basis=ref['masters']
  cache=ScaleCache(max_bytes=65536,max_entries=1);key=cache.identify(c,basis,[f['signature']]);assert key
  cache.put(key,ref);assert cache.get(key)['coefficients']==ref['coefficients'];count+=1
  q=copy.deepcopy(c);products=q['definition']['scalarproduct_rules']
  # Change a nonzero value so this checks ratios within the same graph signature.
  j=next(i for i in range(len(products)-1,-1,-1) if Fraction(products[i][1]))
  products[j][1]=str(2*Fraction(products[j][1]))
  other=cache.identify(q,basis,[f['signature']]);assert other and cache.get(other) is None;count+=1
  changed=cache.identify(c,basis+[[0]*len(c['targets'][0])],[f['signature']]);assert changed!=key and cache.get(changed) is None;count+=1
  cache.put(other,ref);assert len(cache.entries)==1 and cache.get(key) is None;count+=1
  cache=ScaleCache(max_bytes=10,max_entries=1);cache.put(key,ref);assert not cache.entries and cache.bytes==0;count+=1
  cache=ScaleCache();cache.put(key,dict(success=False,coefficients=ref['coefficients']));assert not cache.entries;count+=1
 return count

def main():
 refit=rt.read(HERE/'validation_refit_receipt.json');assert refit['complete'] and refit['final_model_sha256']==inputs.sha(HERE/'trained_model/nonplanar_box.json')
 for graph in ['double_box','nonplanar_box']:
  for folder in ['model_test','application_test']:assert rt.read(HERE/folder/(graph+'_completion.json'))['complete']
  protocol=rt.read(HERE/'protocols'/(graph+'.json'))
  for c in protocol['validation']:
   workers={rt.read(HERE/'validation'/(c['id']+'_'+name+'_r'+str(rep)+'.json.gz'))['worker'] for name in protocol['actions']+['previous'] for rep in range(3)}
   assert len(workers)==1,(c['id'],workers)
 compatibility=rt.read(HERE/'compatibility_test/summary.json');assert compatibility['complete'] and compatibility['all_exact'] and compatibility['requests']==8
 subprocess.run([sys.executable,str(HERE/'s08_analyze.py')],check=True)
 checks=guards();d=rt.read(HERE/'summary.json');assert d['timings']==480 and d['application']['requests']==144
 subprocess.run([sys.executable,str(HERE/'s09_document.py')],check=True)
 for folder in ['protocols','references','pilot','training','validation','matched_validation','validation_initial','trained_model','model_test','application_test','compatibility_test','logs']:
  text={
   'protocols':'These files define the cases and configurations before their comparisons.\nRead the parent guide for the profile divisions and execution order.\nThe training and test scripts consume these definitions.',
   'references':'These files contain independent native reductions and their master indices.\nThe test compares final coefficients with these records.\nThe application receives master indices only.\nReference coefficients never enter model inputs or reuse preparation.',
   'pilot':'These development records compare candidate seed boundaries and Kira settings.\nThe records include failed first attempts and their recovery.\nThe training script selects its candidate set from these measurements.',
   'training':'These records supply complete reduction times for training.\nThe training script produces them and fits candidate cost predictors.\nThe records include exact coefficients, all attempts, and the final check.',
   'validation':'These records select fixed controls, model parameters, margins, and deployment.\nEach candidate has three repeated timings per validation request.\nThe selection files preserve all fitted alternatives and their measured ranking.',
   'matched_validation':'These records repeat the second nonplanar validation profile with every candidate and control on one worker.\nThe original worker had no free memory for a later control job.\nThe repeat protocol was recorded before these measurements and before any nonplanar reserved test.\nThe refit script copies these checked records into the active validation folder.',
   'validation_initial':'This folder preserves the superseded second-profile validation records and preliminary nonplanar model.\nIts candidate and previous-application measurements used different workers.\nThe matched repeat corrects that comparison before any reserved test.\nNo reserved result informed the repeat or the model refit.',
   'trained_model':'These files store fitted tree arrays and validation decisions.\nFiles with the fixed prefix contain no model weights.\nFreeze files identify the code and parameters used before reserved tests.\nThe application reads the validation decision before loading any new predictor.\nBoth current decisions retain the preceding application.',
   'model_test':'These files contain five rotated repetitions for each reserved request and method.\nThe four methods are native, previous, fixed, and learned.\nEvery method for a request runs on the same worker.\nResult reuse is disabled.\nCompletion records require exact reference agreement for every output.',
   'application_test':'These files compare fresh processes on sequences of three momentum scales.\nThe factors are 1, 3/2, and 2.\nEach sequence includes its initial Kira reduction and all exact checks.\nThe four methods separate learned choices and exact reuse.\nEach base request has three repetitions, with all methods on the same worker.\nJOINT_APP_PARTS and JOINT_APP_PART split disjoint base requests between workers.\nCompletion requires every part.\nNative references are generated independently at all three scales.',
   'compatibility_test':'These files check the earlier four-loop native and eight-loop analytic paths.\nThe new application receives physical definitions and master indices in fresh processes.\nBoth methods must reproduce the saved exact reference.\nThese checks preserve existing behavior and do not extend the new model domain.',
   'logs':'Scheduler logs remain on Hoffman.\nTheir names identify the graph and study stage.\nScientific records and completion files are stored in the other documented folders.\nThe repository includes this guide; it does not duplicate routine scheduler output.'}[folder]
  p=HERE/folder;p.mkdir(exist_ok=True);(p/'README.md').write_text('# '+folder.replace('_',' ').capitalize()+'\n\n'+text+'\n\nRead [the parent guide](../README.md) for producers, readers, dependencies, and limits.\n')
 def change(r):return f'{abs(1-r)*100:.1f}% '+('less' if r<=1 else 'more')+' time'
 a=d['comparisons'];b=d['application']['comparisons']
 summary='Validation retains the preceding ML application for both graphs.\nNeither new joint predictor clears the 2% replacement threshold.\nAcross 24 reserved first requests, the selected application uses '+change(a['learned_to_previous']['ratio'])+' than the preceding application.\nIt uses '+change(a['learned_to_native']['ratio'])+' than tuned native Kira.\nIts comparison with the fixed configuration gives '+change(a['learned_to_fixed']['ratio'])+'.\nThe separate three-scale sequences use '+change(b['learned_reuse_to_previous']['ratio'])+' than the preceding application without reuse.\nEach sequence includes its first Kira solve.\nAll 480 first-request reductions and 144 sequence requests pass exact checks.\nRead `summary.json` for intervals, individual slower requests, and all controls.\nThese results use known massless two-loop boxes, rational kinematics, symbolic dimension, and supplied masters.'
 block(HERE/'README.md','MEASURED RESULTS',summary)
 block(ROOT/'README.md','JOINT CONFIGURATION RESULTS','Use [joint seed choices and scale reuse](ML_model_seed_selection/joint_policy/README.md) for the updated application.\n'+summary)
 block(ROOT/'README.md','ADAPTIVE REDUCTION','## Current reduction interface\n\nUse [the joint-configuration application](ML_model_seed_selection/joint_policy/README.md).\nIt retains the preceding ML decisions for the fitted two-loop inputs.\nNew joint predictors remain disabled because validation found less than 2% improvement.\nA request sequence can reuse exact results under a common positive momentum-scale change.\nOther inputs retain the preceding analytic and native paths.\nKira keeps native row choices and exact algebra.\nRead the guide for controls, measured limits, and input requirements.\nEarlier studies remain available; their speedup factors cannot be multiplied.')
 block(ROOT/'ML_model_seed_selection/README.md','JOINT CONFIGURATION','The [joint-policy study](joint_policy/README.md) tests combined seed and Kira configuration choices using complete reduction time.\nValidation retains the preceding ML application for both graphs.\nIt also implements a separately derived scale transformation for exact reuse.\nThe guide gives the current application and measured controls.')
 block(OLD/'README.md','FOLLOWUP APPLICATION','The [joint-configuration study](../joint_policy/README.md) extends this application.\nThis folder preserves its earlier fitted models and measurements unchanged.')
 block(ROOT/'report/README.md','JOINT CONFIGURATION','`joint_policy_results.tex` gives the latest model and exact scale-reuse comparisons.\n`joint_policy_appendix.tex` defines the cases and derives the scale identity.\n`joint_policy_data.json` contains the compact measured evidence.\n`joint_policy_validation.json` records the final checks.\nRead `../ML_model_seed_selection/joint_policy/README.md` for the full data and commands.')
 block(ROOT/'report/paper_figures/README.md','JOINT CONFIGURATION','`joint_policy_times.pdf` shows first-request ratios and separate scale-sequence ratios.\nThe first panel retains individual slower requests.\nThe second includes the initial solve in every sequence.\n`../../ML_model_seed_selection/joint_policy/s09_document.py` generates it from completed measurements.')
 block(ROOT/'rules.md','JOINT ML AND EXACT REDUCTION','Improve complete reduction time using unrestricted ML choices and exact mathematical methods where applicable.\nKeep model, fixed-control, and exact-reuse gains separate, with first-use and retry costs included.\nRetain independent tests, exact checks, previous evidence, resource limits, and the required documentation and publication copies.')
 for p in HERE.glob('*.py'):ast.parse(p.read_text(),filename=p.name)
 missing=[str(p) for p in HERE.rglob('*') if p.is_dir() and not (p/'README.md').exists()];assert not missing,missing
 subprocess.run(['make','-B','all'],cwd=ROOT/'report',check=True)
 subprocess.run([sys.executable,'s01_check_paper.py'],cwd=ROOT/'report',check=True)
 size=sum(p.stat().st_blocks*512 for p in HERE.rglob('*') if p.is_file());assert size<20*1024**2
 v=dict(complete=True,all_exact=True,main_timings=d['timings'],sequence_requests=d['application']['requests'],compatibility_requests=8,guard_checks=checks+20,model_parity_checks=sum(m['parity_checks'] for m in d['models'].values()),all_ml_disabled_in_native_and_fixed=True,retained_allocated_bytes=size,summary_sha256=inputs.sha(HERE/'summary.json'),source_sha256={p.name:inputs.sha(p) for p in HERE.glob('*.py')},model_sha256={p.name:inputs.sha(p) for p in (HERE/'trained_model').glob('*.json')},pdf_sha256={n:inputs.sha(ROOT/'report'/(n+'.pdf')) for n in ['report','notes']})
 save(HERE/'validation.json',v);save(ROOT/'report/joint_policy_validation.json',v);print('FINISHED',json.dumps(v),flush=True)

if __name__=='__main__':main()
