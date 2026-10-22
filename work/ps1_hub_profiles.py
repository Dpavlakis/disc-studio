"""Approved PS1 hub relief, radii and heights expressed in millimetres."""
import numpy as np

FEATURES={
 'top':[(7.62,.11,.09),(9.65,.37,.12),(10.35,.24,-.065),(11.7,.18,.045),(12.05,.14,-.026),(20.5,.045,-.016)],
 'bottom':[(7.63,.11,.065),(10.05,.065,-.035),(11.75,.08,.035),(12.05,.10,-.022),(17.55,.20,.12),(18.0,.12,-.045),(20.5,.05,-.022)]}

def height(r,side):
 return sum(h*np.exp(-((r-c)/w)**2) for c,w,h in FEATURES[side])

def profile(side,start,end):
 lo,hi=sorted((start,end));samples=list(np.linspace(lo,hi,24))
 for c,w,h in FEATURES[side]:
  samples.extend(c+w*t for t in (-3,-2,-1.5,-1,-.5,0,.5,1,1.5,2,3) if lo<c+w*t<hi)
 radii=np.array(sorted(set(samples)))
 if end<start:radii=radii[::-1]
 sign=1 if side=='top' else -1
 return [(float(r)/1000,sign*(.6+float(height(r,side)))/1000) for r in radii]
