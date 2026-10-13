"""Check folder-guide coverage without loading scientific data or model weights."""
import argparse
import json
from pathlib import Path, PurePosixPath
import subprocess

ROOT=Path(__file__).resolve().parents[1]
CODE_SUFFIXES={'.py','.sh','.cpp','.h','.hpp','.cc','.c','.patch','.wl'}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree',default='HEAD',help='Git tree or commit to inspect.')
    parser.add_argument('--output',type=Path,help='Optional JSON output file.')
    args=parser.parse_args()
    raw=subprocess.check_output(['git','ls-tree','-r','-z',args.tree],cwd=ROOT)
    files={};dirs={'.'};codes=[]
    for item in raw.split(b'\0'):
        if not item:continue
        meta,name=item.split(b'\t',1);mode,kind,oid=meta.decode().split();name=name.decode()
        p=PurePosixPath(name);files[name]=(mode,oid)
        dirs.update(str(d) for d in p.parents)
        if mode!='120000' and (p.suffix in CODE_SUFFIXES or p.name=='Makefile'):codes.append(name)
    missing=[]
    for d in sorted(dirs):
        name=('' if d=='.' else d+'/')+'README.md'
        if name not in files or files[name][0]=='120000':missing.append(name)
    # Read only the code-folder guides, directly from the committed objects.
    cache={};undocumented=[]
    for name in codes:
        d=str(PurePosixPath(name).parent);guide=('' if d=='.' else d+'/')+'README.md'
        if guide not in cache:
            cache[guide]=subprocess.check_output(['git','show',args.tree+':'+guide],cwd=ROOT).decode() if guide in files else ''
        if PurePosixPath(name).name not in cache[guide]:undocumented.append(name)
    result={'directories':len(dirs),'readmes':len(dirs)-len(missing),'code_files':len(codes),
            'missing_readmes':missing,'undocumented_code_files':undocumented,
            'scientific_data_read':False,'model_weights_loaded':False,
            'scope':'Every directory in the Git tree. Symlink destinations provide their own guides. Archive members are not Git directories.'}
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if missing or undocumented:raise SystemExit(1)
if __name__=='__main__':main()
