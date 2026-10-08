"""Freeze the native seed-envelope comparison on the same seven independent bases."""
from s01_common import *
def main():
 plan=read(HERE/"plan.json")
 p=dict(plan,family_cases=[c for c in plan["family_cases"] if c["domain"]!="vacuum"],
    batch_sizes=[16],policies=["ml_native_seeds"],native_policies=["kira_native","kira_native_trim"],
    selection="same seven independent-basis cases and largest nested target batch from the frozen main comparison",
    native_envelope="per predicted seed sector, maxima of r,s,d; Kira generates the enclosed seeds and applies its own symmetries and selection",
    native_first_attempt_seconds=60,native_fallback_seconds=100)
 assert len(p["family_cases"])==7
 folder=HERE/"native_seed";folder.mkdir(exist_ok=True);(folder/"results").mkdir(exist_ok=True)
 if (folder/"plan.json").exists():assert read(folder/"plan.json")==p
 else:write(folder/"plan.json",p)
 inputs=read(HERE/"frozen_inputs.json")["sha256"]
 paths=[HERE/name for name in ["s10_native_worker.py","s11_native_run.py","s12_native_array.sh","s13_native_audit.py","s14_prepare_native.py"]]+[folder/"plan.json"]
 hashes=dict(inputs);hashes.update({str(f.relative_to(ROOT)):sha(f) for f in paths})
 if (folder/"frozen_inputs.json").exists():assert read(folder/"frozen_inputs.json")["sha256"]==hashes
 else:write(folder/"frozen_inputs.json",dict(sha256=hashes,threshold=.5))
 print("Native envelope comparison frozen: seven families, three policies, three repeats")
if __name__=="__main__":main()
