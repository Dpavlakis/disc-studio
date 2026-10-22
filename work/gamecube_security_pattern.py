import random
def security_bars():
 rng=random.Random(410276);cursor=15.;bars=[]
 while cursor<201:
  width=rng.choice([.22,.31,.48,.72,1.02,1.28])*rng.uniform(.86,1.13)
  bars.append((cursor,min(201,cursor+width)))
  gap=rng.choices([.15,.28,.51,.86,1.4],[5,6,4,2,1])[0]*rng.uniform(.8,1.25)
  cursor+=width+gap
 return bars
