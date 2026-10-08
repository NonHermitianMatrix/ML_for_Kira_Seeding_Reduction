"""Write completion descriptions only from independently validated test results."""
from s02_common import *
r=read(HERE/"results.json");v=read(HERE/"validation.json")
assert v["passed"] and v["result_sha256"]==sha(HERE/"results.json")
n=r["targets"];p=r["policies"]["predicted"].get("sufficient",0)
f=r["policies"]["full"].get("sufficient",0);b=r["policies"]["background"].get("sufficient",0)
paragraph=f"The exact Kira sufficiency test is complete for {n:,} reserved targets in {r['families']:,} families. Predicted seeds suffice for {p:,} targets ({100*p/n:.3f}%). The full candidate pool suffices for {f:,} ({100*f/n:.3f}%), and background identities without IBP seeds suffice for {b:,} ({100*b/n:.3f}%). All symbolic decisions agree with three independent finite-field row-space checks. The model and threshold remain unchanged. This test checks existence of a reduction within the stored identity pools; it does not reconstruct all master coefficients or measure a native Kira speedup."
path=HERE/"README.md";text=path.read_text()
text=text.replace("The validated pilot is complete. The full evaluation is in progress. Only results.json together with a passing validation.json identifies the completed full test.",paragraph)
text+="\nThe completed results are in results.json, family_results.csv and results/; validation.json verifies coverage and hashes. figures/ contains the two PDF figures and PNG previews. s25_finalize_readmes.py updates folder descriptions from the checked result counts.\n"
path.write_text(text)
for path,link in [(ROOT/"README.md","ML_model_seed_selection/kira_sufficiency_test/README.md"),(MODEL/"README.md","kira_sufficiency_test/README.md"),(MODEL/"model_test/README.md","../kira_sufficiency_test/README.md")]:
 text=path.read_text()
 marker="<!-- exact-kira-sufficiency -->"
 assert marker not in text
 text+="\n"+marker+"\n"+paragraph+f"\n\nSee the [Kira sufficiency test]({link}) for the equations, fixed protocol, raw symbolic remainders and independent checks.\n"
 path.write_text(text)
print(paragraph)
