"""Catalogue-based northern asterisms and one quiet meteor per 40-second loop.

East-left / north-up gnomonic projection, followed by a camera roll. Each scene
has its own framing; this is not a dated, surveyed view of the landmark.
"""
from pathlib import Path
import json
import numpy as np

W,H,PERIOD=320,200,40
ROOT=Path(__file__).resolve().parents[1]
CATALOG=json.loads((ROOT/'assets/northern-stars.json').read_text())['stars']
GROUPS={
    'Cassiopeia':{'chain':[21,168,264,403,542]},
    'Big Dipper':{'chain':[5191,5054,4905,4660,4554,4295,4301,4660]},
    'Little Dipper':{'chain':[424,6789,6322,5903,5563,5735,6116,5903]},
}
# Name, center RA/Dec, principal point, focal length, camera roll (radians).
VIEWS=[('Cassiopeia',15,60,230,35,230,-.35),
       ('Big Dipper',187,56,222,35,215,.05),
       ('Cassiopeia',15,60,82,34,230,-.20),
       ('Little Dipper',240,80,222,55,220,-.12)]
METEORS=[{'start':18.,'duration':.75,'from':[44,18],'to':[83,47]},
         {'start':24.,'duration':.75,'from':[55,11],'to':[95,39]},
         {'start':14.,'duration':.75,'from':[246,16],'to':[286,40]},
         {'start':30.,'duration':.75,'from':[44,17],'to':[89,41]}]


def project(star,view):
    _,ra0,dec0,cx,cy,f,roll=view
    a0,d0=np.radians([ra0,dec0]);a,d=np.radians([star['ra'],star['dec']])
    den=np.sin(d0)*np.sin(d)+np.cos(d0)*np.cos(d)*np.cos(a-a0)
    if den<=0:return None
    x=-np.cos(d)*np.sin(a-a0)/den*f
    y=-(np.cos(d0)*np.sin(d)-np.sin(d0)*np.cos(d)*np.cos(a-a0))/den*f
    return (int(round(np.cos(roll)*x-np.sin(roll)*y+cx)),
            int(round(np.sin(roll)*x+np.cos(roll)*y+cy)))


def make_field(kind):
    view=VIEWS[kind];name=view[0];members=set(GROUPS[name]['chain'])
    pixels=np.zeros((H,W,3),np.uint8);positions={}
    # Fainter stars first: an unresolved pair never erases its brighter member.
    for star in sorted(CATALOG,key=lambda s:-s['mag']):
        point=project(star,view)
        if point is None:continue
        x,y=point
        if not (3<=x<W-3 and 3<=y<116):continue
        level=float(np.clip(230-35*(star['mag']+.5),35,205))
        if star['hr'] in members:level=max(level,83)
        color=np.clip([level*.88,level,level*1.08],0,235).astype(np.uint8)
        pixels[y,x]=np.maximum(pixels[y,x],color)
        positions[star['hr']]={'hr':star['hr'],'x':x,'y':y,'magnitude':star['mag']}
    for hr in members:
        if hr not in positions:raise ValueError(f'{name}: missing primary star HR {hr}')
    chain=GROUPS[name]['chain']
    guide={'name':name,'stars':[positions[hr] for hr in dict.fromkeys(chain)],
           'lines':[[[positions[a]['x'],positions[a]['y']],
                     [positions[b]['x'],positions[b]['y']]] for a,b in zip(chain,chain[1:])],
           'view':dict(zip(['ra_center','dec_center','cx','cy','focal','roll'],view[1:])),
           'meteor':METEORS[kind]}
    return pixels,guide


FIELDS=[make_field(kind) for kind in range(4)]


def draw_stars(canvas,kind):
    np.maximum(canvas,FIELDS[kind][0],out=canvas)


def meteor_progress(kind,phase):
    event=METEORS[kind]
    seconds=(phase%(2*np.pi))/(2*np.pi)*PERIOD
    progress=(seconds-event['start'])/event['duration']
    return progress if 0<progress<1 else None


def draw_meteor(canvas,kind,phase):
    p=meteor_progress(kind,phase)
    if p is None:return
    event=METEORS[kind]
    start=np.array(event['from'],float);finish=np.array(event['to'],float)
    vector=finish-start;direction=vector/np.linalg.norm(vector)
    head=start+vector*p
    fade=float(np.sin(np.pi*p)**.7)
    length=min(9.,np.linalg.norm(vector)*p)
    # One logical pixel wide; short fading tail and no sparkles or secondary burst.
    trail=np.zeros_like(canvas)
    for distance in np.arange(length,-.5,-.5):
        pos=np.rint(head-direction*distance).astype(int)
        x,y=map(int,pos)
        if not (0<=x<W and 0<=y<H):continue
        weight=fade*.85*(1-distance/(length+.5))**1.6
        value=(np.array([167,201,198])*weight).astype(np.uint8)
        trail[y,x]=np.maximum(trail[y,x],value)
    canvas[:]=np.clip(canvas.astype(np.uint16)+trail.astype(np.uint16),0,255).astype(np.uint8)


def metadata():
    return {'catalog':{'name':'Bright Star Catalogue 5','epoch':'J2000',
                       'url':'https://www-kpno.kpno.noirlab.edu/Info/Caches/Catalogs/BSC5/catalog5.html'},
            'projection':'gnomonic, east-left/north-up before camera roll',
            'framing':'independently composed fields, not a dated geographic sky simulation',
            'scenes':[field[1] for field in FIELDS]}
