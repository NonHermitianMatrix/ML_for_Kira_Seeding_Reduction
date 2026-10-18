"""Refit after correcting the installed library's multi-output loss scaling."""
from s00_common import *
import numpy as np
import s01_train as training
from sklearn.neural_network import MLPRegressor

class ConsistentMLPRegressor(MLPRegressor):
 def _backprop(self,X,y,activations,deltas,coef_grads,intercept_grads):
  loss,cg,ig=super()._backprop(X,y,activations,deltas,coef_grads,intercept_grads)
  # This installed sklearn version averages loss across outputs but sums
  # output derivatives. Restore the objective differentiated by its gradient.
  penalty=.5*self.alpha*sum(np.sum(w*w) for w in self.coefs_)/len(X)
  return (loss-penalty)*y.shape[1]+penalty,cg,ig

def main():
 # Direct finite differences check every component of a small two-output fit.
 m=ConsistentMLPRegressor(hidden_layer_sizes=(3,),alpha=.1,random_state=1201,max_iter=3,solver='lbfgs')
 X=np.array([[.2,.4],[.3,-.1],[-.6,.2]]);Y=np.array([[.4,.1],[.2,-.2],[-.3,.5]])
 import warnings
 with warnings.catch_warnings():warnings.simplefilter('ignore');m.fit(X,Y)
 from sklearn.neural_network._multilayer_perceptron import _pack
 w=_pack(m.coefs_,m.intercepts_)
 def eval_at(v):
  acts=[X,None,None];ds=[None,None];cg=[np.empty_like(a) for a in m.coefs_];ig=[np.empty_like(a) for a in m.intercepts_]
  return m._loss_grad_lbfgs(v,X,Y,acts,ds,cg,ig)
 _,g=eval_at(w);errs=[]
 for i in range(len(w)):
  a=w.copy();b=w.copy();a[i]+=1e-6;b[i]-=1e-6
  finite=(eval_at(a)[0]-eval_at(b)[0])/2e-6;errs.append(abs(finite-g[i]))
 assert max(errs)<1e-6
 write(HERE/'refit/gradient_check.json',dict(complete=True,components=len(w),max_absolute_error=max(errs),reason='Installed multi-output MLP loss averaged outputs, while derivatives summed them. Corrected loss to sum outputs; no held-out data used.'))
 # Define the fresh protocol before fitting so the training metadata can read it.
 protocol=READ(HERE/'protocol.json');protocol['reserved']=cases(1213);protocol['parent_model_trial']='profile 1201 retained as initial implementation trial';protocol['seed']=1213;protocol['splits']='Use the original historical training and validation sets after the same physical holdouts. Freeze before new profile 1213. No reserved costs enter fitting or selection.'
 write(HERE/'refit/protocol.json',protocol)
 training.MLPRegressor=ConsistentMLPRegressor;training.HERE=HERE/'refit';training.main()
if __name__=='__main__':main()
