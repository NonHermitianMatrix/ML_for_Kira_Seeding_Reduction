from s00_common import *
import shutil
base=HERE/'uncached_storage';base.mkdir(exist_ok=True)
for n in ['results','references','model_test','completion.json','protocol.json','uncached_stop.json']:
 q=HERE/'integration'/n
 if q.exists():shutil.move(str(q),str(base/n))
module('cached_storage_checks',HERE/'s07_sector_checks.py').main()
