"""Validate complete exact hull-board partition before live registration."""
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts import planking


if __name__=='__main__':
    start=time.time()
    planking.REPORT=lambda *values:print('Strake progress',values,'elapsed',time.time()-start,flush=True)
    strakes=planking.hull_strakes()
    print('Strake regions',len(strakes),'elapsed',time.time()-start,flush=True)
    print([(r['id'],round(r['shape'].Volume(),4)) for r in strakes],flush=True)
    boards=planking.physical_hull_boards()
    print('Physical boards',len(boards),'elapsed',time.time()-start,flush=True)
    parts=list(planking.hull_board_parts())
    print('Finish regions',len(parts),'invalid',[(n,s.isValid(),len(s.Solids())) for n,s,_,_ in parts if not s.isValid() or len(s.Solids())!=1],
          'faces',sum(len(s.Faces()) for _,s,_,_ in parts),'elapsed',time.time()-start,flush=True)
