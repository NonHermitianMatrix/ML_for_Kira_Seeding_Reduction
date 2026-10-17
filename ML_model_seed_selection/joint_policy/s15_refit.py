"""Replace mismatched validation-worker measurements before any reserved test."""
import shutil,subprocess
from s00_engine import *

def main():
 assert not list((HERE/'model_test').glob('nonplanar_box*.json.gz')),'Reserved testing must not have started'
 assert rt.read(HERE/'matched_validation/completion.json')['complete']
 old=HERE/'validation_initial';old.mkdir(exist_ok=True);files=[]
 for path in (HERE/'validation').glob('nonplanar_box_h922*.json.gz'):
  shutil.copyfile(path,old/path.name);new=HERE/'matched_validation'/path.name;assert new.exists()
  files.append(dict(name=path.name,old_sha256=inputs.sha(path),new_sha256=inputs.sha(new)));shutil.copyfile(new,path)
 assert len(files)==126,len(files)
 for name in ['nonplanar_box.json','fixed_nonplanar_box.json','nonplanar_box_freeze.json']:
  shutil.copyfile(HERE/'trained_model'/name,old/name)
 shutil.copyfile(HERE/'validation/nonplanar_box_selection.json',old/'nonplanar_box_selection.json')
 # Every reduction below must already have a complete saved record.
 protocol=rt.read(HERE/'protocols/nonplanar_box.json')
 for phase in ['training','validation']:
  for c in protocol[phase]:
   for name in protocol['actions']+(['previous'] if phase=='validation' else []):
    for rep in range(3 if phase=='validation' else 1):assert (HERE/phase/(c['id']+'_'+name+'_r'+str(rep)+'.json.gz')).exists()
 save(HERE/'validation_refit_receipt.json',dict(complete=False,reason='Second validation profile and previous-application control require the same worker. Its original worker had no free memory for the control job. Repeat all methods for this profile on one worker before any reserved test.',files=files,reserved_measurements_seen=0))
 subprocess.run([sys.executable,str(HERE/'s03_train.py'),'nonplanar_box'],check=True)
 data=rt.read(HERE/'validation_refit_receipt.json');data['complete']=True;data['final_model_sha256']=inputs.sha(HERE/'trained_model/nonplanar_box.json');save(HERE/'validation_refit_receipt.json',data)

if __name__=='__main__':main()
