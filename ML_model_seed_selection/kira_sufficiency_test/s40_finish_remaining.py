"""Finish only shards left incomplete after the preceding execution."""
import argparse
from s02_common import *
def main(index):
 state=read(HERE/("worker_%02d.json"%index))
 assert state.get("finished"),"The preceding worker must finish first"
 if not state["errors"] and state["completed"]==state["assigned"]:
  print("Worker",index,"already complete.",flush=True);return
 from s39_resume_output_48 import main as resume
 resume(index)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--worker",required=True,type=int);main(p.parse_args().worker)
