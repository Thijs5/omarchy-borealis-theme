"""Translucent aurora veils, sampled onto a fixed pixel grid.

Broad pleats carry long, nearly vertical strands above a softly fading hem.
Continuous emission is added to the night sky at logical-pixel resolution.
There are no hard palette bands, masks at the veil boundary or image filters.
"""
import numpy as np

W,H=320,200
SKY_H=H
ROWS=np.arange(SKY_H,dtype=np.float32)[None,:]


# RGB light and the small pale component of its strongest concentrations.
GREEN=(np.array([28,155,58]),np.array([90,75,90]))
TEAL=(np.array([35,138,120]),np.array([80,80,80]))
ROSE=(np.array([146,75,139]),np.array([78,83,84]))
MINT=(np.array([57,149,124]),np.array([85,90,87]))
VIOLET=(np.array([119,81,161]),np.array([89,86,90]))


def spline(points,u):
    """A softly tensioned Catmull-Rom path along the hanging hem."""
    points=np.asarray(points,np.float32)
    extended=np.vstack([2*points[0]-points[1],points,2*points[-1]-points[-2]])
    position=np.clip(u,0,1)*(len(points)-1)
    index=np.minimum(position.astype(int),len(points)-2)
    f=(position-index)[:,None]
    p0,p1,p2,p3=[extended[index+i] for i in range(4)]
    m1=.42*(p2-p0);m2=.42*(p3-p1)
    return (2*f**3-3*f**2+1)*p1+(f**3-2*f**2+f)*m1+(-2*f**3+3*f**2)*p2+(f**3-f**2)*m2


def sheet(points,phase,flux,heights=None,strength=1,seed=0,motion=1,tilt=.08,split_rose=False):
    points=np.asarray(points,np.float32).copy()
    count=len(points)
    control=np.linspace(0,1,count)
    # Different parts of the fold open and close at different times. This
    # changes the actual outline and projected depth, not just its texture.
    envelope=np.sin(np.pi*control)**.7
    points[:,0]+=motion*envelope*(7*np.sin(phase+control*5.1+seed)+3*np.sin(2*phase-control*4))
    points[:,1]+=motion*envelope*(5*np.sin(phase-control*5.9+seed*.6)+2*np.sin(2*phase+control*7))
    dense_u=np.linspace(0,1,960)
    dense=spline(points,dense_u)
    arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(dense,axis=0),axis=1))]
    length=float(arc[-1])
    samples=330
    u=np.interp(np.linspace(0,length,samples),arc,dense_u)
    path=spline(points,u)
    emission=np.interp(u,control,np.asarray(flux))
    emission*=.87+.13*np.sin(phase-u*8+seed)
    # Aperiodic multiscale strands in curve coordinates. They are clustered by
    # the changing projection, rather than tiled into equal-width screen bars.
    pleats=.65+.16*np.sin(u*22-phase+seed)+.07*np.sin(u*39+phase+.3)
    fibers=.88+.08*np.sin(u*289-2*phase+seed)+.04*np.sin(u*173+phase)
    threads=np.clip(pleats*fibers,.16,1)
    # Local highlights extend up the sheet rather than tracing its lower edge.
    threads*=1+1.1*np.exp(-((u-(.31+.012*np.sin(phase)))/.025)**2)
    threads*=1+.7*np.exp(-((u-(.69+.015*np.sin(phase+1)))/.035)**2)
    if heights is None:heights=np.full(count,35)
    reach=np.interp(u,control,heights)*(.90+.10*np.sin(phase+u*6))
    base=path[:,1]+1.7*np.sin(u*53+phase)+.6*np.sin(u*131+2*phase)
    distance=base[:,None]-ROWS
    positive=np.maximum(distance,0)
    body=1.05*np.exp(-(positive/reach[:,None])**1.3)
    core=.045*np.exp(-((distance-1.0)/3.2)**2)
    # A few pixels below each individual strand soften the cut into clusters.
    below=np.exp(-(np.minimum(distance,0)/14.0)**2)
    energy=(body+core)*below*(emission*threads*strength)[:,None]
    energy*=length/samples
    lean=tilt+.022*np.sin(u*19+phase+seed)
    ray_x=path[:,0,None]+positive*lean[:,None]+.0006*positive**1.4*np.sin(u[:,None]*17+phase)
    width=(.86+.55*np.sin(u*31+seed)**2)[:,None]
    nearest=np.floor(ray_x+.5).astype(int)
    density=np.zeros(W*SKY_H,np.float64)
    if split_rose:
        rose_density=np.zeros_like(density)
        rose_fraction=np.clip((positive-(30+10*np.sin(u*13+phase))[:,None])/24,0,1)
        rose_fraction=rose_fraction**2*(3-2*rose_fraction)
        rose_energy=energy*rose_fraction*.48
        energy=energy*(1-.90*rose_fraction)
    y_indices=np.broadcast_to(np.arange(SKY_H),(samples,SKY_H))
    for offset in [-1,0,1]:
        x=nearest+offset
        weight=np.maximum(0,1-np.abs(x-ray_x)/width)
        valid=(x>=0)&(x<W)&(energy>.0001)&(weight>0)
        indices=(y_indices[valid]*W+x[valid]).ravel()
        density+=np.bincount(indices,weights=(energy*weight)[valid].ravel(),minlength=W*SKY_H)
        if split_rose:
            rose_density+=np.bincount(indices,weights=(rose_energy*weight)[valid].ravel(),minlength=W*SKY_H)
    if split_rose:return density.reshape(SKY_H,W),rose_density.reshape(SKY_H,W)
    return density.reshape(SKY_H,W)


VESTRAHORN=[(-30,126),(20,119),(63,104),(91,87),(118,75),(143,70),
            (176,73),(198,63),(226,55),(257,62),(293,54),(347,38)]
JOKULSARLON=[(-25,118),(23,116),(61,108),(94,99),(132,105),
             (169,96),(202,86),(238,88),(277,79),(344,65)]
KIRKJUFELL=[(-25,93),(25,89),(66,81),(103,56),(143,51),
            (179,55),(212,53),(245,46),(279,48),(345,43)]
SVARTIFOSS=[(-28,60),(25,74),(66,84),(101,77),(136,80),
            (170,69),(206,63),(245,47),(284,52),(344,43)]


def fields(kind,phase):
    if kind==0:
        field=sheet(VESTRAHORN,phase,[0,.25,.65,.80,.55,.50,.85,.42,.80,.60,.45,0],
                    [55,58,76,85,88,84,92,86,78,84,75,60],strength=.68,seed=1,motion=.85,tilt=.012)
        return [(field,GREEN)]
    if kind==1:
        green,rose=sheet(JOKULSARLON,phase,[0,.25,.55,.82,.64,.45,.75,.65,.35,0],
                         [60,65,75,82,88,84,82,78,74,60],strength=.82,seed=3,
                         motion=.8,tilt=-.012,split_rose=True)
        # Keep the same continuous veil and height-dependent blend, but give
        # the lagoon rose-violet light with a faint cool teal upper reach.
        return [(green,ROSE),(rose,TEAL)]
    if kind==2:
        green=sheet(KIRKJUFELL,phase,[0,.20,.48,.68,.44,.50,.36,.62,.48,0],
                    [40,44,50,56,62,60,58,50,52,40],strength=.47,seed=5,motion=.6,tilt=-.01)
        return [(green,MINT)]
    if kind==3:
        teal=sheet(SVARTIFOSS,phase,[0,.25,.48,.72,.55,.35,.75,.90,.40,0],
                   [50,55,66,72,76,70,68,66,60,50],strength=.63,seed=8,motion=.8,tilt=-.01)
        # Broad color blending follows the existing light, without introducing
        # new outlines, stripes, or independent moving sheets.
        emerald_share=.20*np.exp(-((np.arange(W)[None,:]-74)/95)**2)
        return [(teal*(1-emerald_share),VIOLET),(teal*emerald_share,GREEN)]
    raise ValueError('Unknown aurora scene')


def aurora(kind,phase):
    layers=fields(kind,phase)
    # Continuous emission is evaluated on the logical pixel grid. Hard palette
    # thresholds and winner-takes-all hue selection made opaque contour blocks.
    emission=np.zeros((H,W,3),np.float32)
    for field,(color,highlight) in layers:
        light=-np.expm1(-np.maximum(field,0)*.85)
        emission+=light[...,None]*color+light[...,None]**4*highlight
    return emission,np.ones((H,W),bool)
