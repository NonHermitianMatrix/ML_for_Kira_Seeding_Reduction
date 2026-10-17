"""Check the live interface, build both documents, and record publication evidence."""
import functools,json,math,subprocess,sys
from s00_probe import HERE,ROOT,BOUNDS,rt,inputs,save

def main():
 assert rt.read(HERE/'trained_model/prediction_parity.json')['passed']
 structural=[]
 for graph,entry in rt.read(HERE/'trained_model/freeze.json')['selection'].items():
  option=entry['option']
  if option is None:continue
  rows=(HERE/'trained_model'/(option['name']+'.txt')).read_text().splitlines();nodes=[x.split() for x in rows[1:]]
  assert int(rows[0])==len(nodes) and 0<len(nodes)<=8191
  for node in nodes:
   feature=int(node[0]);assert feature<15 or feature in [22,23]
   assert math.isfinite(float(node[1])) and 0<=float(node[4])<=1
   if feature>=0:assert all(0<=int(node[j])<len(nodes) for j in [2,3])
  @functools.lru_cache(None)
  def depth(i):
   node=nodes[i]
   return 0 if int(node[0])<0 else 1+max(depth(int(node[2])),depth(int(node[3])))
  maximum=depth(0);assert maximum<=24
  structural.append(dict(graph=graph,model=option['name'],nodes=len(nodes),maximum_path_depth=maximum))
 inputs.write(HERE/'trained_model/runtime_structure.json',dict(passed=True,models=structural,node_limit=8191,path_depth_limit=24))
 subprocess.run([sys.executable,str(HERE/'s15_index_transfer.py')],check=True)
 subprocess.run([sys.executable,str(HERE/'s12_application.py')],check=True)
 # Build the seed-bound evidence first. Its scientific inputs remain unchanged.
 subprocess.run([sys.executable,str(BOUNDS/'s13_finish.py')],check=True)
 for script in ['s05_analyze.py','s06_document.py','s08_readmes.py']:
  subprocess.run([sys.executable,str(HERE/script)],check=True)
 subprocess.run(['make','-B','all'],cwd=ROOT/'report',check=True)
 subprocess.run([sys.executable,'s01_check_paper.py'],cwd=ROOT/'report',check=True)
 paper=rt.read(ROOT/'report/paper_validation.json');d=rt.read(HERE/'summary.json')
 assert paper['original_notes_reconstructable'] and paper['self_repository_citations']==0 and d['all_successful_outputs_exact']
 retained=sum(q.stat().st_blocks*512 for root in [HERE,BOUNDS] for q in root.rglob('*') if q.is_file());assert retained<32*1024**2
 old=rt.read(BOUNDS/'validation.json');old['pdf_sha256']=paper['pdf_sha256'];old['combined_new_studies_retained_bytes']=retained
 for dest in [BOUNDS/'validation.json',ROOT/'report/learned_bounds_validation.json']:inputs.write(dest,old)
 audit=dict(complete=True,all_successful_outputs_exact=True,live_interface_checked=True,compiled_model_structures_checked=True,controls_disable_all_ml=True,failed_cases_retained=True,summary_sha256=inputs.sha(HERE/'summary.json'),freeze_sha256=inputs.sha(HERE/'trained_model/freeze.json'),sources={str(p.relative_to(ROOT)):inputs.sha(p) for p in HERE.glob('s*') if p.is_file()},pdf_sha256=paper['pdf_sha256'],retained_bytes=retained,combined_upper_bytes=old['combined_upper_bytes'])
 for dest in [HERE/'validation.json',ROOT/'report/equation_refinement_validation.json']:inputs.write(dest,audit)
 print('EQUATION_REFINEMENT_PUBLICATION_READY',flush=True)
if __name__=='__main__':main()
