import sys, json, os
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,'..'))
from diff import raster; from build import outline, OUT; import v02
data=json.load(open(os.path.join(OUT,'parts.json')))
def runs(A,y):
    row=A[850-y]; xs=[];inside=False
    for i,v in enumerate(row):
        if v and not inside: s=i;inside=True
        if not v and inside: xs.append((s-100,i-100));inside=False
    return xs
k=sys.argv[1]
A=raster(outline(data[k])); B=raster(v02.outline(k))
for y in map(int,sys.argv[2].split(',')): print(y,'mới',runs(A,y),'\n    v0.2',runs(B,y))
