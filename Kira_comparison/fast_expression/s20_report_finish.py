"""Apply final report formatting and state the measured completion cohorts."""
import argparse,json,pathlib,re
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPORT=ROOT/"report"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit",required=True);a=ap.parse_args()
 s=json.loads((HERE/"test_summary.json").read_text())
 amendment=json.loads((HERE/"scheduler_amendment.json").read_text())
 p=REPORT/"kira_fast_expression.tex";t=p.read_text()
 t=t.replace("Tests checked normal exits, delayed exits,\nforced termination, invalid process identifiers and the absence of\nunreaped children.","Tests checked that the arithmetic process exits normally or reaches\nthe existing termination limit.")
 t=t.replace("At most two trials run concurrently.","The array began with two simultaneous trials and increased to three\nand then six after memory and storage checks. The individual limits,\ntargets, models and calculation code stayed fixed.")
 find=lambda n,d,b:next(c for c in s["comparisons"] if (c["numerator"],c["denominator"],c["size"])==(n,d,b))
 counts=[]
 for size in [1,16]:
  c=find("exit_ml","stock_ml",size)
  line=f'For batches of {size} target'+('' if size==1 else 's')+f', the two learned workflows both completed all five repeats in {c["paired_batches"]} of twelve batches. '
  lost,gained=len(c["control_only"]),len(c["modified_only"])
  if lost or gained:line+=f'The original workflow alone completed {lost} batches, and the modified workflow alone completed {gained} batches. '
  else:line+='Their completed batch sets agreed. '
  control=find("exit_ml","exit_pool",size);lost,gained=len(control["control_only"]),len(control["modified_only"])
  if lost or gained:line+=f'With the modified shutdown, the full pool alone completed {lost} batches and learned selection alone completed {gained} batches. '
  counts.append(line)
 paragraph=" ".join(counts)+"The quoted ratios use only the stated complete paired subsets; all other outcomes remain in the completion counts.\n\n"
 marker="% responsive-exit-cohorts"
 if marker in t:t=t.split(marker)[0]+t.split("% responsive-exit-cohorts-end",1)[1].lstrip("\n")
 t=t.replace(r"\begin{figure}",marker+"\n"+paragraph+"% responsive-exit-cohorts-end\n\n"+r"\begin{figure}",1)
 t=t.replace("Independent checks evaluated", "Independent checks compared").replace("target coefficients against the raw Kira exports", "sampled master-coefficient vectors with the raw Kira exports")
 labels={"stock_pool":"The original full-pool workflow","stock_ml":"The original learned workflow","exit_pool":"The modified full-pool workflow","exit_ml":"The modified learned workflow"}
 paragraphs=[]
 for policy,label in labels.items():
  v=s["totals"][policy]
  paragraphs.append(f'{label} completed {v["exact"]} trials exactly, with {v["failed"]} failed measured trials and {v["skipped"]} skipped repetitions. Its completed trials required fallback {v["completed_fallbacks"]} times.\n\n')
 if len({(v["exact"],v["failed"],v["skipped"]) for v in s["totals"].values()})==1:
  v=s["totals"]["exit_ml"]
  replacement=f'Each workflow completed {v["exact"]} trials exactly and recorded {v["failed"]} failed attempts and {v["skipped"]} skipped repetitions. Each learned workflow used full-pool fallback {v["completed_fallbacks"]} times among its completed trials. The paired comparisons below identify the successful batch sets.\n\n'
  block="".join(paragraphs)
  assert block in t
  t=t.replace(block,replacement)
 p.write_text(t)
 p=REPORT/"references.bib";t=p.read_text()
 block=(f'@misc{{KiraResponsiveExitData,\n author = {{Saraswat, Rushil}},\n'
        ' title = {Responsive Fermat Shutdown and Learned Seed Selection in Exact {Kira} Reductions},\n'
        ' year = {2026},\n'
        f' howpublished = {{\\href{{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/{a.data_commit}/Kira_comparison/fast_expression}}{{Frozen code, paired solver comparisons, exact checks and complete timings}}}}\n'
        '}\n')
 t,n=re.subn(r"(?ms)^@misc\{KiraResponsiveExitData,.*?^\}\s*",lambda m:block,t,count=1);assert n==1
 p.write_text(t)
 p=REPORT/"report.tex";t=p.read_text();primary=find("exit_ml","stock_ml",1)
 t=t.replace("In twelve new held-out one-loop instances, its one-target time ratio",f'In {primary["paired_batches"]} complete paired single-target batches from twelve new held-out one-loop instances, its time ratio')
 anchor="These results\nsupport conclusions within the tested domains"
 t=t.replace(anchor,"The shutdown study adds twelve one-loop instances in six further\nheld-out kinematic groups. These results\nsupport conclusions within the tested domains")
 p.write_text(t)
 print("Report cohorts, scheduler conditions and citation formatting checked.")
if __name__=="__main__":main()
