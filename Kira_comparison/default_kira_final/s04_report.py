"""Write the primary comparison table from saved, checked measurements."""
from pathlib import Path
import json,statistics,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/"report"
d=json.loads((H/"summary.json").read_text());assert d["complete"]
p=json.loads(__import__("gzip").decompress((H/"protocol.json.gz").read_bytes()))
assert d["protocol_sha256"]==hashlib.sha256((H/"protocol.json.gz").read_bytes()).hexdigest()
names={"double_box":"Planar double box","nonplanar_box":"Nonplanar double box","sunrise":"Massive sunrise","vacuum3":"Three-loop vacuum"}
lines=[r"\begin{table}[!htbp]\centering\small",r"\caption{Primary comparison: the final method versus original Kira 3.1 with default algorithms for the stated job. Times sum request medians over pairs verified in all three repetitions. The completion column gives default/method counts; the pair column gives matched/requested counts. A factor above one and a positive saving mean less time with our method.}",r"\label{tab:default-kira-final}",r"\setlength{\tabcolsep}{4pt}",r"\begin{tabular}{@{}lrrrrrr@{}}\toprule",r"Integral class & Completed & Pairs & Kira (s) & Method (s) & Factor & Saved (\%)\\\midrule"]
def row(name,g):
 n=g["matched"];c=g["completed"];v=g["seconds"]
 if n:
  return name+f' & {c["default"]}/{c["method"]} & {n}/{g["requests"]} & {v["default"]:.3f} & {v["method"]:.3f} & {g["speedup"]:.2f} & {100*(1-v["method"]/v["default"]):.1f}'+r"\\"
 return name+f' & {c["default"]}/{c["method"]} & 0/{g["requests"]}'+r" & --- & --- & --- & ---\\"
for key in names:lines.append(row(names[key],d["groups"][key]))
total=dict(requests=d["requests"],matched=d["matched"],completed={m:sum(x["verified"][m] for x in d["rows"]) for m in ["default","method"]},seconds=d["seconds"],speedup=d["speedup"])
lines.extend([r"\midrule",row("Total",total),r"\bottomrule\end{tabular}",r"\end{table}"])
lines.append(f'We obtain {d["matched"]} matched requests out of {d["requests"]}. Default Kira completes {total["completed"]["default"]} requests in all three repetitions, and our method completes {total["completed"]["method"]}. The coefficient audit performs {d["checks"]:,} exact comparisons.')
if d["matched"]:
 v=d["seconds"]
 lines.append(f'The summed matched times are {v["default"]:.3f} seconds for default Kira and {v["method"]:.3f} seconds for our method. Their ratio gives a {d["speedup"]:.2f}-fold speed factor and {100*(1-v["method"]/v["default"]):.1f}\\% less elapsed time on these matched requests.')
failed=[r for r in d["rows"] if not all(r["verified"].values())]
if failed:
 lines.append("Unmatched requests remain in the completion counts. Their elapsed times and failure reasons are retained, but they do not enter a finite speed factor.")
lines.append("We exclude setup runs that did not complete the measurement procedure or could not launch either native reducer. Their records remain separate from the physical reduction comparison.")
all_method_seconds=sum(statistics.median(r["times"]["method"]) for r in d["rows"])
if total["completed"]["method"]==d["requests"]:
 lines.append(f'Across all {d["requests"]} requests, our method takes {all_method_seconds:.3f} seconds as a sum of request medians.')
if total["completed"]["default"]<d["requests"]:
 lines.append(f'Default Kira does not complete all requests under these limits, so we report no speed factor for the full {d["requests"]}-request workload. The finite factor above applies only to the {d["matched"]} matched requests.')
(P/"paper_default_rows.tex").write_text("\n".join(lines)+"\n")
(P/"default_kira_data.json").write_text(json.dumps(d,indent=2)+"\n")
(H/"results/README.md").write_text("""# Recorded comparisons

Each compressed JSON file records one request, method, and repetition.
The default method uses the original Kira executable.
The method entry uses the frozen final application.
Records contain elapsed time, completion, exact checks, limits, and returned coefficients.
Read all three repetitions before calculating a request median.
Use only pairs verified in all repetitions for a finite speed factor.
Keep unsuccessful records in the completion counts.
Run ../s02_compare.py to produce these files.
Run ../s04_report.py to make the report table.
""")
print(json.dumps({k:d[k] for k in ["requests","matched","seconds","speedup","checks","all_outputs_verified"]}))

# Put the same primary measurement in the abstract and conclusion.
import re
counts={m:sum(r["verified"][m] for r in d["rows"]) for m in ["default","method"]}
if d["matched"]:
 v=d["seconds"];saved=100*(1-v["method"]/v["default"])
 primary=(f'On {d["matched"]} matched native requests, summed median time changes from '
          f'{v["default"]:.3f} to {v["method"]:.3f} seconds, a {d["speedup"]:.2f}-fold speed factor '
          f'and {saved:.1f}\\% time saving.')
else:
 primary='The bounded comparison supplies no pair that passes all three repetitions, so it supplies no finite speed factor.'
primary+=(f' Under the stated limits, default Kira completes {counts["default"]} of 20 requests '
          f'in all repetitions, and our method completes {counts["method"]}.')
for name in ["paper_abstract.tex","paper_conclusion.tex"]:
 q=P/name;text=q.read_text()
 pattern=r'(?<=% BEGIN PRIMARY COMPARISON\n).*?(?=\n% END PRIMARY COMPARISON)'
 assert len(re.findall(pattern,text,re.S))==1
 addition=primary
 if name=="paper_conclusion.tex":
  addition+=' This is a direct comparison with default algorithms for the specified physical job, including the total effect of the retained changes. It does not isolate ML, and it supplies no default-Kira result for the other 73 analytic requests.'
 q.write_text(re.sub(pattern,lambda m:addition,text,flags=re.S))
