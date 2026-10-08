"""Combine native component reductions with exact Fermat algebra through Kira."""
from s01_common import *
def combine(family,path,work,plan,solver):
 identities=[];block=[]
 def consume(lines):
  terms=[]
  for line in lines:
   match=re.fullmatch(r"F\[([-\d,]+)\]\*\((.*)\)",line.strip())
   if not match:raise ValueError("Native output syntax: "+line[:200])
   terms.append(dict(indices=list(map(int,match[1].split(","))),coefficient=match[2].replace("^","**")))
  assert old.exact_equal(terms[0]["coefficient"],"-1")
  identities.append(dict(id="native_%06d"%len(identities),source={"kind":"native_reduction"},terms=terms))
 for line in path.read_text().splitlines()+[""]:
  if line.strip():block.append(line)
  elif block:consume(block);block=[]
 supplied_family=dict(family,identities=identities)
 return solver(supplied_family,family["targets"],None,work,plan)
