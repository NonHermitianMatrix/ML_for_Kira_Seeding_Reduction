"""Choose a small native action set using development data only."""
from s00_direct_common import *
from s03_cases import cases

def main():
 assert all(read(HERE/f'pilot{i}.json')['complete'] for i in [0,1]);scores=[]
 for order in range(1,9):
  rows=[read(HERE/'development'/(c['id']+'_order'+str(order)+'.json.gz')) for c in cases('development')];scores.append(dict(order=order,unverified=sum(not r['verified'] for r in rows),seconds=sum(r['application_seconds'] if r['verified'] else max(60,r['application_seconds']) for r in rows)))
 best=sorted(scores,key=lambda r:(r['unverified'],r['seconds']));orders=[1]+[r['order'] for r in best if r['order']!=1][:2]
 write(HERE/'actions.json',dict(complete=True,actions=['order1','dense','wide'],development=scores));print(json.dumps(dict(actions=['order1','dense','wide'],ordering_candidates=orders,development=scores)),flush=True)
if __name__=='__main__':main()
