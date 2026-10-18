"""Repeat the predefined storage grid using 128-bit integral weights."""
from s00_common import *
def main():
 code=(HERE/'s07_sector_checks.py').read_text().replace("BIN=ROOT/'.tools/kira-sector-storage/kira'","BIN=ROOT/'.tools/kira-sector-wide/kira'").replace("'integration/","'wide_integration/")
 g=dict(__name__='wide_checks',__file__=str(HERE/'s07_sector_checks.py'));exec(compile(code,str(HERE/'s07_sector_checks.py'),'exec'),g);g['main']()
if __name__=='__main__':main()
