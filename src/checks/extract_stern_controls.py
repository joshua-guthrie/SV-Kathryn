"""Review native S04 cap-rail fastener picks; no geometry changes."""
from pathlib import Path
import numpy as np
from scipy.ndimage import convolve,maximum_filter
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]

if __name__=='__main__':
    path=ROOT/'renders/stern-deck-source.png'
    image=Image.open(path).convert('RGB');arr=np.array(image.convert('L'))
    region=(arr[:,250:720]<128).astype(float)
    yy,xx=np.mgrid[-17:18,-17:18];radius=np.sqrt(xx*xx+yy*yy)
    best=np.zeros_like(region)
    for r in (9,10,11,12,13,14):
        ring=((radius>=r-2)&(radius<=r+2)).astype(float);ring/=ring.sum()
        inside=(radius<r-4).astype(float);inside/=inside.sum()
        score=convolve(region,ring,mode='constant')-.45*convolve(region,inside,mode='constant')
        best=np.maximum(best,score)
    peaks=(best==maximum_filter(best,size=31))&(best>.57)
    y,x=np.where(peaks)
    draw=ImageDraw.Draw(image)
    for i,(xx,yy) in enumerate(zip(x+250,y),1):
        draw.ellipse((xx-17,yy-17,xx+17,yy+17),outline='red',width=3)
        draw.text((xx+19,yy-8),str(i),fill='red',font_size=20)
        print(i,int(xx),int(yy),round(float(best[yy,xx-250]),3))
    image.save(ROOT/'renders/stern-fastener-picks.png')
