"""Use spare slots for finished shards while other earlier shards continue."""
import argparse
from s02_common import *
def main(index):
 state=read(HERE/("worker_%02d.json"%index))
 if not state.get("finished"):
  print("Worker",index,"still has an existing writer; deferred.",flush=True)
  return
 from s40_finish_remaining import main as resume
 resume(index)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--worker",required=True,type=int);main(p.parse_args().worker)
