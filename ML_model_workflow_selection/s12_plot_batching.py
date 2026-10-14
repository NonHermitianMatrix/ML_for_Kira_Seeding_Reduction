"""Plot the completed joint-request comparison without changing any policy."""
import json,os,tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def main():
    data=json.loads((HERE/'request_batching/summary.json').read_text())
    assert data['complete'] and data['all_exact'] and data['workflows']==200
    with tempfile.TemporaryDirectory(prefix='kira_plot_',dir=os.environ.get('TMPDIR')) as cache:
        os.environ['MPLCONFIGDIR']=cache
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
        plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
        labels={'sunrise':'Sunrise','double_box':'Planar box','vacuum3':'Vacuum','ladder3':'Ladder',
                'nonplanar_box':'Nonplanar box','pentagon':'Pentagon','one_mass_box':'Box with virtuality'}
        kinds=list(labels)
        fig,axes=plt.subplots(1,2,figsize=(10,4.4),gridspec_kw={'width_ratios':[1.6,1]})
        values=[]
        for j,(method,label,color) in enumerate([
            ('joint_native','Joint native','#497799'),('joint_fixed','Joint integrated','#df8934'),
            ('joint_learned','Joint learned','#278264')]):
            x=[data['by_topology'][k][method] for k in kinds];values+=x
            axes[0].scatter(x,np.arange(len(kinds))+(j-1)*.18,label=label,color=color,s=30)
        axes[0].set_yticks(range(len(kinds)));axes[0].set_yticklabels([labels[k] for k in kinds]);axes[0].invert_yaxis()
        axes[0].axvline(1,color='.4',linestyle='--',linewidth=1)
        lo=min(values+[1]);hi=max(values+[1]);pad=max(.03,.08*(hi-lo))
        axes[0].set_xlim(max(0,lo-pad),hi+pad)
        axes[0].set_xlabel('Time / separate native time')
        axes[0].legend(loc='upper center',bbox_to_anchor=(.5,-.17),ncol=1,frameon=False,fontsize=8)
        ratios=['joint_native','joint_fixed','joint_learned','learned_to_joint_native','learned_to_joint_fixed']
        names=['Joint native / separate','Joint integrated / separate','Joint learned / separate',
               'Learned / joint native','Learned / joint integrated']
        lower=[];upper=[]
        for i,key in enumerate(ratios):
            r=data['aggregate'][key];a,b=r['interval'];v=r['ratio'];lower.append(a);upper.append(b)
            axes[1].errorbar(v,i,xerr=[[v-a],[b-v]],fmt='o',color='#278264',capsize=3)
        axes[1].set_yticks(range(len(names)));axes[1].set_yticklabels(names,fontsize=8);axes[1].invert_yaxis()
        axes[1].axvline(1,color='.4',linestyle='--',linewidth=1)
        lo=min(lower+[1]);hi=max(upper+[1]);pad=max(.03,.08*(hi-lo))
        axes[1].set_xlim(max(0,lo-pad),hi+pad);axes[1].set_xlabel('Time ratio (lower is faster)')
        for ax in axes:ax.grid(axis='x',alpha=.2)
        fig.tight_layout(w_pad=2)
        fig.savefig(ROOT/'report/paper_figures/request_batching.pdf',bbox_inches='tight')
        plt.close(fig)
    print(json.dumps({'plot':'request_batching.pdf','groups':len(data['cases'])}),flush=True)

if __name__=='__main__':main()
