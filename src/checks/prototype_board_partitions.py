"""Benchmark exact board partitioning before registering M4 material."""
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from parts import hull
from parts.board_tools import split_material,plane_x


if __name__=='__main__':
    start=time.time()
    deck=hull.make_deck()
    print('Deck reference ready',time.time()-start,flush=True)
    cuts=[plane_x(n*3.75/12) for n in range(-26,27)]
    boards=split_material(deck,cuts)
    print('Partitioned deck:',len(boards),'boards; material',sum(s.Volume() for s in boards),
          'reference',deck.Volume(),'total faces',sum(len(s.Faces()) for s in boards),
          'reference faces',len(deck.Faces()),'elapsed',time.time()-start,flush=True)
