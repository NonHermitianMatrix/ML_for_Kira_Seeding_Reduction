"""Resume native cases after enlarging only the retained-evidence storage guard."""
import argparse,importlib.util,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--case",type=int,required=True);args=ap.parse_args()
 if (HERE/"native_seed/results"/("complete_%02d.json"%args.case)).exists():
  print("Already complete; preserving original node record.");return
 extension=json.loads((HERE/"native_seed/storage_guard_extension.json").read_text())
 assert extension["combined_conservative_bytes"]<10000000000
 assert extension["new_output_limit_bytes"]==67108864
 spec=importlib.util.spec_from_file_location("native_controller",HERE/"s11_native_run.py")
 controller=importlib.util.module_from_spec(spec);spec.loader.exec_module(controller)
 original_read=controller.read
 def read(path):
  value=original_read(path)
  if pathlib.Path(path)==HERE/"native_seed/plan.json":
   value=dict(value);assert value["result_limit"]==extension["old_output_limit_bytes"]
   value["result_limit"]=extension["new_output_limit_bytes"]
  return value
 controller.read=read;controller.main()
if __name__=="__main__":main()
