"""Reject exports with unresolved integrals before coefficient comparison."""
import ast,json,pathlib,shutil
HERE=pathlib.Path(__file__).resolve().parent
def main():
 p=HERE/"s02_run.py";s=p.read_text()
 anchor='   result["complete"]=set(rows)==expected\n'
 addition='''   if reference:
    allowed={tuple(a) for a in basis}
    unresolved=[a for a in result["masters"] if tuple(a) not in allowed]
    result["unresolved_integrals"]=unresolved
    if unresolved:
     result.update(complete=False,success=False,status="unresolved_basis",mismatches=[])
     return result
'''
 assert s.count(anchor)==1 and 'unresolved_integrals' not in s
 s=s.replace(anchor,anchor+addition);ast.parse(s);p.write_text(s)
 p=HERE/"s24_workflow.py";s=p.read_text()
 anchor='  assert not path.exists(),'
 s=s.replace(anchor,'  if os.environ.get("KIRA_WORKFLOW_ATTEMPT_TAG"):path=path.with_name(path.name.replace(".json.gz","_"+os.environ["KIRA_WORKFLOW_ATTEMPT_TAG"]+".json.gz"))\n'+anchor)
 ast.parse(s);p.write_text(s)
 p=HERE/"s40_seed_threshold_search.py";s=p.read_text()
 s=s.replace('    e=env.copy()','    e=env.copy()\n    if (HERE/"rejected_workflows"/path.name).exists():e["KIRA_WORKFLOW_ATTEMPT_TAG"]="admission_v2"')
 ast.parse(s);p.write_text(s)
 path=HERE/"seed_threshold_training/training_05_vacuum3_deep_seed_t0.01.json.gz"
 from s03_records import read_record
 r=read_record(path);assert not r["success"] and r["status"]=="reference_mismatch"
 trial=read_record(HERE.parents[1]/r["attempts"][0]);ref=read_record(pathlib.Path(trial["reference"]))
 extras=sorted(set(map(tuple,trial["masters"]))-set(map(tuple,ref["masters"])))
 assert extras==[(1,0,1,3,-1,0)]
 dest=HERE/"rejected_workflows"/path.name;dest.parent.mkdir(exist_ok=True);assert not dest.exists()
 path.rename(dest)
 (HERE/"basis_admission_fix.json").write_text(json.dumps(dict(reason="The seed subset left one non-master integral in the export despite the native master check. The exact comparison rejected it. Explicit output-basis admission now sends this incomplete result to the fixed native fallback.",unresolved_integrals=extras,preserved_failure=str(dest.relative_to(HERE.parents[1])),original_attempt=r["attempts"][0]),indent=2)+"\n")
if __name__=="__main__":main()
