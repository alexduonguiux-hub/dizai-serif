#!/usr/bin/env python3
"""Đo độ dày nét VUÔNG GÓC (skeleton + distance transform) trên ảnh bảng chữ.

Chạy từ gốc repo: python3 tools/perp_thickness.py   (cần scikit-image, scipy)
Mỗi glyph in: độ dày các nét cắt qua ở 20/35/50/65/80% cap, và độ dày các nét
ngang ở cột 35/50/65% bề ngang. Đơn vị font, cap = 700, ±3 u."""
import numpy as np
from skimage.morphology import skeletonize
from scipy import ndimage as ndi
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from measure_sheet import load_ink
R='reference/regular/'
cfg={R+'caps-A-K.webp':(126,362,'A B C D E F G H I J K'.split()),
     R+'caps-L-R.webp':(85,382,'L M N O P Q R'.split()),
     R+'caps-S-Z.webp':(115,373,'S T U V W X Y Z'.split()),
     R+'figures-0-9.png':(100,347,['0','1','2','3','4','5','6','78','9'])}
def runs(line):
    r=[];s=None
    for i,v in enumerate(line):
        if v and s is None:s=i
        if not v and s is not None:r.append((s,i-s));s=None
    return r
for f,(top,base,names) in cfg.items():
    ink=load_ink(f); k=700/(base-top)
    cols=ink.any(0); segs=[];s=None
    for x in range(ink.shape[1]):
        if cols[x] and s is None:s=x
        if not cols[x] and s is not None: segs.append((s,x));s=None
    for nm,(a,b) in zip(names,segs):
        g=np.pad(ink[:,a:b],2); sk=skeletonize(g); dt=ndi.distance_transform_edt(g)
        sy,sx=np.nonzero(sk)
        out=[]
        for frac in (0.2,0.35,0.5,0.65,0.8):
            y=int(base-(base-top)*frac)+0
            row=[]
            for x0,w in runs(g[y]):
                cx=x0+w/2; d=(sx-cx)**2+(sy-y)**2; i=d.argmin()
                # local: median 2*dt of skeleton pts within 4px
                m=d<=max(16,d.min()+4)
                row.append(round(2*np.median(dt[sy[m],sx[m]])*k))
            out.append(row)
        # horizontals: vertical runs at 3 columns
        hz=[]
        for fx in (0.35,0.5,0.65):
            x=int((b-a)*fx)+2; col=[]
            for y0,h in runs(g[:,x]):
                cy=y0+h/2; d=(sx-x)**2+(sy-cy)**2; m=d<16
                if m.any(): col.append(round(2*np.median(dt[sy[m],sx[m]])*k))
            hz.append(col)
        print('%-3s across@20..80%%:%s  vertical-scan:%s'%(nm,out,hz))
