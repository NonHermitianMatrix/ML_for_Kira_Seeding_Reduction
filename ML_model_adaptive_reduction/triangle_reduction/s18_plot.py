"""Show exact triangle gains and the separately measured native result."""
from s00_triangle_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
 s=read(HERE/'summary.json');plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,axes=plt.subplots(1,2,figsize=(9.5,3.7),constrained_layout=True)
 xs=list(range(1,14));ys=[s['triangle_loops'][str(i)]['ratio'] for i in xs];ax=axes[0]
 ax.plot(xs,ys,'o-',color='#17618b');ax.axhline(1,color='0.4',ls='--',lw=1);ax.set(xticks=[1,3,5,7,9,11,13],xlabel='Number of independent triangle loops',ylabel='New time / preceding time',ylim=(0,max(1.1,max(ys)*1.1)),title='Direct triangle reduction')
 names=['double_box','nonplanar_box','sunrise','vacuum3'];labels=['Planar box','Nonplanar box','Sunrise','Vacuum (3 loops)'];ax=axes[1]
 y=[s['groups'][g]['ratio'] for g in names];lo=[max(0,v-s['groups'][g]['interval'][0]) for g,v in zip(names,y)];hi=[max(0,s['groups'][g]['interval'][1]-v) for g,v in zip(names,y)]
 ax.errorbar(y,range(4),xerr=[lo,hi],fmt='o',capsize=3,color='#216c47');ax.axvline(1,color='0.4',ls='--',lw=1);ax.set(yticks=range(4),yticklabels=labels,xlabel='New time / preceding time',xlim=(max(0,min(v-l for v,l in zip(y,lo))-.10),max(1.05,max(v+h for v,h in zip(y,hi))+.05)),title='Native algebra selection');ax.invert_yaxis()
 for ax in axes:ax.grid(alpha=.18)
 dest=ROOT/'report/paper_figures/triangle_extension.pdf';fig.savefig(dest);plt.close(fig)
 write(HERE/'figure_data.json',dict(source_sha256=sha(HERE/'summary.json'),figure_sha256=sha(dest),triangle_ratios=ys,native_groups=names,native_ratios=y,uncertainty='Paired request bootstrap; complete-time sum ratio. One request per triangle loop except loop one.'))
if __name__=='__main__':main()
