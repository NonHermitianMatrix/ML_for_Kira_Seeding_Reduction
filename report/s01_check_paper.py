"""Bounded checks of the paper and preserved notes, with no research reruns."""
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
def main():
    source='\n'.join((HERE/n).read_text() for n in ['report.tex','paper_appendices.tex'])
    bib=(HERE/'paper_references.bib').read_text()
    cites={x.strip() for group in re.findall(r'\\cite\{([^}]+)\}',source) for x in group.split(',')}
    keys=set(re.findall(r'@\w+\{([^,]+),',bib))
    labels=re.findall(r'\\label\{([^}]+)\}',source)
    refs=set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',source))
    assert cites<=keys,cites-keys
    assert refs<=set(labels),refs-set(labels)
    assert len(labels)==len(set(labels))
    assert not re.search(r'NonHermitianMatrix|ML_for_Kira_Seeding_Reduction',source+bib)
    figs=re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',source)
    for f in figs:assert (HERE/f).read_bytes().startswith(b'%PDF'),f
    for name in ['report','notes']:
        assert (HERE/(name+'.pdf')).read_bytes().startswith(b'%PDF')
        log=HERE/(name+'.log')
        if log.exists():
            s=log.read_text(errors='replace')
            assert not re.search(r'(?:Citation|Reference) .+ undefined|There were undefined|^! ',s,re.M),name
    notes=(HERE/'notes.tex').read_text()
    abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',notes,re.S).group(1)
    archive=json.loads((HERE/'notes_preservation.json').read_text())
    assert hashlib.sha256(abstract.encode()).hexdigest()==archive['abstract_sha256']
    restored=notes.replace('Notes on Machine Learning for Kira IBP Reduction','Machine Learning for Kira IBP Reduction')
    assert hashlib.sha256(restored.encode()).hexdigest()==archive['original_source_sha256']
    for n,digest in archive['supporting_files'].items():
        assert hashlib.sha256((HERE/n).read_bytes()).hexdigest()==digest,n
    data=json.loads((HERE/'paper_figure_data.json').read_text())
    for name,record in data['sources'].items():
        path=HERE.parent/name
        if path.exists():assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256'],name
    result=dict(external_citation_keys=len(cites),internal_references=len(refs),figures=len(figs),
        self_repository_citations=0,original_abstract_preserved=True,original_notes_text_preserved_except_title=True,
        original_supporting_files_preserved=len(archive['supporting_files']),
        pdf_sha256={n:hashlib.sha256((HERE/(n+'.pdf')).read_bytes()).hexdigest() for n in ['report','notes']})
    (HERE/'paper_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':main()
