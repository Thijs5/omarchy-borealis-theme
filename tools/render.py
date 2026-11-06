"""Borealis / Iceland. Draw at 320x200; enlarge by integer nearest neighbour.

Hand-authored landmark silhouettes and flat colour clusters. Aurora rays are
sampled directly on the logical grid; no image filters or source photo pixels.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import cv2
import numpy as np
from nightsky import draw_stars, draw_meteor

ROOT=Path(__file__).resolve().parents[1]
W,H,FPS,SECONDS=320,200,24,40
NAMES=['01-vestrahorn','02-jokulsarlon','03-kirkjufell','04-svartifoss','05-omarchy']
# Selected presentation frames from the actual 24 fps, 40-second loops.
# Preserve the approved Vestrahorn still; other scenes use their own light peak.
POSTER_FRAMES=[714,558,756,366,558]
Y,X=np.mgrid[:H,:W].astype(np.float32)


def rgb(value):
    return np.array([int(value[i:i+2],16) for i in (0,2,4)],np.uint8)


def poly(canvas,points,color):
    value=tuple(map(int,rgb(color)))+((255,) if canvas.shape[2]==4 else ())
    cv2.fillPoly(canvas,[np.array(points,np.int32)],value,lineType=cv2.LINE_8)


def line(canvas,points,color,width=1):
    value=tuple(map(int,rgb(color)))+((255,) if canvas.shape[2]==4 else ())
    cv2.polylines(canvas,[np.array(points,np.int32)],False,value,width,cv2.LINE_8)


def terrain(kind):
    c=np.zeros((H,W,4),np.uint8)
    if kind==0:
        # Vestrahorn: an extended, jagged massif, not a single alpine cone.
        poly(c,[(0,139),(21,134),(42,136),(58,125),(71,119),(84,102),
                (94,93),(100,99),(112,75),(119,82),(130,70),(135,57),
                (143,65),(148,79),(154,75),(164,91),(172,87),(181,114),
                (193,123),(202,115),(210,119),(216,110),(223,119),
                (230,121),(241,137),(267,142),(320,144),(320,151),(0,151)],'343A49')
        poly(c,[(58,132),(84,106),(94,95),(93,115),(81,130),(72,141)],'485360')
        poly(c,[(83,141),(107,101),(112,77),(119,84),(114,101),
                (104,115),(97,140)],'5C6871')
        poly(c,[(99,141),(116,108),(130,73),(135,59),(139,68),
                (133,87),(121,105),(111,139)],'798B91')
        poly(c,[(111,142),(130,105),(143,67),(148,81),(143,98),
                (129,114),(122,141)],'485565')
        poly(c,[(137,141),(151,104),(154,78),(164,94),(164,108),
                (178,131),(190,143)],'46535C')
        poly(c,[(178,141),(182,120),(193,127),(203,118),(204,131),
                (218,142)],'202D37')
        poly(c,[(135,60),(131,75),(126,83),(128,76),(132,65)],'B0C2BC')
        poly(c,[(111,79),(108,96),(104,103),(108,99),(114,84)],'9DB3B2')
        poly(c,[(143,69),(139,84),(138,97),(130,108),(132,99),(140,77)],'879FA5')
        poly(c,[(156,83),(159,97),(167,113),(173,119),(167,115),(157,99)],'6F858E')
        poly(c,[(44,145),(83,138),(116,141),(142,137),(176,142),
                (207,140),(252,147),(278,147),(320,150),(320,153),(0,153)],'24313A')
        # Black dunes overlap the wet sand in unequal, broad arcs.
        poly(c,[(0,166),(22,159),(47,161),(69,171),(94,179),
                (114,189),(148,200),(0,200)],'0D1620')
        poly(c,[(0,166),(22,159),(47,161),(61,167),(36,164),(16,166)],'2D383B')
        poly(c,[(0,187),(32,176),(58,180),(74,187),(105,193),
                (118,200),(0,200)],'17232B')
        poly(c,[(216,200),(244,185),(265,181),(286,170),(305,168),
                (320,170),(320,200)],'0D1720')
        poly(c,[(265,182),(286,170),(305,168),(320,170),(301,172),(283,177)],'2C383A')
        for x,y in [(26,161),(38,162),(54,180),(291,171),(302,169)]:
            line(c,[(x-3,y),(x-2,y-5),(x,y-1),(x+1,y-6),(x+2,y-1),(x+5,y-4)],'706B55')
    elif kind==1:
        # Jökulsárlón: a low glacial horizon and differently sized, faceted ice.
        poly(c,[(0,124),(25,118),(48,119),(66,113),(83,116),(103,108),
                (119,112),(137,107),(157,114),(178,113),(196,116),
                (224,111),(243,115),(269,113),(290,118),(320,119),
                (320,134),(0,134)],'3A4359')
        poly(c,[(44,125),(66,115),(82,119),(103,110),(119,114),
                (137,109),(157,116),(179,116),(200,121),(220,117),
                (244,121),(272,118),(289,122),(320,122),(320,130),(0,130)],'718998')
        poly(c,[(0,130),(38,128),(64,131),(91,127),(117,130),(152,127),
                (179,131),(218,128),(248,131),(285,128),(320,131),
                (320,135),(0,135)],'2C465A')
        # Small ice near the glacier, simplified by distance.
        for pts in [[(16,140),(22,134),(29,136),(34,141)],
                    [(62,139),(67,134),(76,136),(83,140)],
                    [(140,139),(146,133),(157,134),(165,140)],
                    [(242,140),(252,133),(262,137),(267,142)],
                    [(291,142),(300,135),(309,138),(315,142)]]:
            poly(c,pts,'7898A5')
        # Middle-right iceberg: a long, low slab with one lifted blue fin.
        poly(c,[(192,153),(207,147),(219,147),(226,136),(232,133),
                (239,143),(248,142),(256,147),(275,149),(285,157),
                (273,164),(211,163)],'477C94')
        poly(c,[(194,153),(208,148),(219,149),(226,138),(231,135),
                (231,146),(224,155),(210,156)],'B0CED1')
        poly(c,[(233,137),(239,145),(249,144),(256,149),(275,151),
                (280,155),(252,154),(242,150),(235,151)],'7EADB9')
        poly(c,[(220,155),(229,148),(231,137),(235,151),(242,154),
                (246,163),(226,162)],'32617D')
        # Foreground iceberg has a broken crown and an ash seam, not a pyramid.
        poly(c,[(16,175),(27,164),(40,160),(49,150),(61,153),(72,141),
                (78,144),(83,159),(97,163),(106,170),(124,175),
                (114,184),(89,190),(49,190),(24,184)],'4B8AA2')
        poly(c,[(18,175),(28,166),(41,163),(50,152),(61,156),(72,143),
                (75,145),(74,158),(64,168),(48,173),(37,180)],'B1D3D3')
        poly(c,[(40,179),(52,168),(64,168),(75,158),(77,147),(82,160),
                (96,165),(99,171),(86,173),(76,182),(58,187)],'7FB7C6')
        poly(c,[(91,176),(101,171),(122,176),(111,183),(91,189),
                (71,187),(79,181)],'37697F')
        poly(c,[(28,171),(42,164),(50,155),(52,158),(46,167),
                (37,175),(26,181),(24,180)],'394B61')
        # A small isolated fragment balances the large mass.
        poly(c,[(258,184),(269,175),(277,176),(281,169),(286,173),
                (289,181),(300,184),(292,189),(271,191)],'558CA4')
        poly(c,[(260,184),(270,177),(278,178),(282,172),(284,175),
                (281,184),(269,187)],'A6CDD1')
        poly(c,[(0,196),(26,191),(42,194),(67,199),(0,200)],'0D1B29')
    elif kind==2:
        # Kirkjufell: curved spreading foot, steep sloping roof and rock strata.
        poly(c,[(0,131),(33,127),(61,130),(84,126),(113,133),
                (143,128),(174,133),(211,129),(239,131),(265,125),
                (291,128),(320,126),(320,143),(0,143)],'303044')
        outline=[(38,145),(65,138),(83,132),(96,123),(107,112),
                 (116,99),(126,79),(134,67),(139,68),(149,74),(158,77),
                 (168,80),(172,86),(177,87),(182,98),(186,111),
                 (195,124),(210,134),(232,140),(263,145)]
        poly(c,outline,'4C5E60')
        poly(c,[(137,69),(151,78),(168,83),(172,89),(179,93),
                (184,111),(195,125),(211,135),(236,142),(263,145),
                (178,144),(166,131),(160,111),(150,96)],'2C3B48')
        # Sparse snow shelves trace the horizontal sediment/lava strata.
        poly(c,[(134,70),(139,71),(146,76),(138,76),(131,80)],'A3B8B3')
        poly(c,[(126,82),(143,83),(157,87),(169,88),(171,91),
                (151,90),(139,87),(124,87)],'5C7479')
        poly(c,[(120,94),(139,95),(148,99),(174,101),(176,104),
                (148,102),(135,99),(117,99)],'536A70')
        poly(c,[(112,108),(131,109),(145,113),(161,113),(164,116),
                (143,116),(129,113),(109,113)],'6B8689')
        poly(c,[(101,122),(121,121),(138,125),(160,125),(169,130),
                (141,128),(120,126),(97,128)],'5E777C')
        poly(c,[(83,133),(105,130),(121,133),(142,132),(162,135),
                (167,139),(140,136),(118,137),(101,134),(73,139)],'6E8788')
        poly(c,[(0,144),(39,142),(71,143),(111,142),(155,144),
                (203,144),(250,143),(291,142),(320,143),(320,148),(0,148)],'1C2B35')
        # Open calm water, a few broad shore stones in the near corners.
        poly(c,[(0,182),(18,175),(31,177),(43,186),(59,188),
                (75,200),(0,200)],'0D1822')
        poly(c,[(0,182),(18,175),(31,177),(35,181),(20,180),(9,185)],'3D5058')
        poly(c,[(240,200),(260,188),(276,187),(291,179),(309,181),
                (320,176),(320,200)],'101C28')
        poly(c,[(276,188),(291,179),(308,182),(298,185),(287,185)],'40545C')
    else:
        # Svartifoss: a continuous concave wall of hanging hexagonal prisms.
        poly(c,[(0,102),(32,96),(65,101),(93,106),(123,108),(156,110),
                (179,106),(209,99),(245,94),(281,91),(320,96),
                (320,181),(0,181)],'121B25')
        poly(c,[(0,99),(32,93),(67,97),(94,102),(125,104),(156,106),
                (178,102),(208,95),(246,90),(283,88),(320,92),
                (320,99),(285,95),(248,97),(211,102),(181,109),
                (156,112),(124,110),(94,108),(65,105),(31,101),(0,107)],'3A4A47')
        # Lower recessed column tier, visible beneath the hanging tips.
        for i,x in enumerate(range(8,315,8)):
            top=126+int(5*np.sin(x/43))
            bottom=169+int(5*np.sin(x/27))
            poly(c,[(x,top),(x+5,top-2),(x+6,bottom-3),
                    (x+2,bottom),(x,bottom-3)],['24323C','2D3D47','21303B'][i%3])
            line(c,[(x+1,top+6),(x+1,bottom-4)],'40515A' if i%4==0 else '34434B')
        # Adjacent upper columns have joined faces, dark seams and hexagonal ends.
        widths=[9,7,8,6,8,7,9,6,7,8,7,6,8,7,7,8,6,7,8,7,8,6,9,7,8,7,6,8,7,9,6,8,7,8,7,7,8,7,8,7,8,7,8,7]
        ends=[4,0,6,3,8,2,5,0,7,3,1,6,2]
        x=-2
        for i,width in enumerate(widths):
            top=int(np.interp(x,[0,35,100,156,210,278,320],[103,99,108,111,101,94,98]))
            bottom=int(np.interp(x,[0,75,158,240,320],[153,143,149,138,144]))+ends[i%len(ends)]
            lean=int(np.clip((x-165)/65,-2,2))
            front=['43505A','384650','4A565E','3B4A55'][i%4]
            side=['26333F','293844','2D3A44'][i%3]
            # Front face, right face, narrow lit arris, and a chamfered end cap.
            poly(c,[(x,top+2),(x+width-3,top),(x+width-3+lean,bottom-3),
                    (x+2+lean,bottom),(x+lean,bottom-2)],front)
            poly(c,[(x+width-3,top),(x+width-1,top+2),
                    (x+width-1+lean,bottom-2),(x+width-3+lean,bottom-3)],side)
            if i%3!=1:line(c,[(x+1,top+4),(x+1+lean,bottom-5)],'5B6970')
            poly(c,[(x+lean,bottom-2),(x+2+lean,bottom),
                    (x+width-3+lean,bottom-3),(x+width-2+lean,bottom)],'53616A')
            joint=top+14+(i*7)%17
            if joint<bottom-5:line(c,[(x+1,joint),(x+width-4,joint+1)],'1D2B36')
            x+=width
        # Narrow white stream drops in front of a deep shadow, not a wide cyan sheet.
        poly(c,[(155,110),(168,109),(169,127),(169,148),
                (174,166),(169,175),(155,174),(152,166),(157,146)],'405F70')
        poly(c,[(158,110),(165,110),(165,130),(164,150),
                (168,167),(165,172),(157,170),(156,163),(159,145)],'94C4CC')
        poly(c,[(159,111),(162,111),(161,135),(161,153),
                (163,167),(159,169),(158,159),(160,139)],'C3DFDD')
        poly(c,[(151,170),(160,165),(168,167),(174,173),(169,177),
                (156,177),(147,174)],'6D9FA9')
        # Broken, faceted basalt scree, larger towards the viewer.
        for pts,col in [
            ([(19,165),(29,158),(40,163),(39,173),(26,177)],'33464D'),
            ([(41,174),(52,161),(63,165),(66,177),(54,184)],'283A45'),
            ([(68,167),(78,160),(88,166),(84,177),(72,175)],'3F5156'),
            ([(97,175),(106,166),(119,170),(121,180),(108,185)],'2B3E49'),
            ([(196,175),(205,164),(218,166),(224,176),(212,183)],'354A51'),
            ([(228,167),(239,159),(252,164),(250,174),(238,180)],'2C4048'),
            ([(271,172),(284,159),(301,162),(309,175),(295,184)],'3C4C50')]:
            poly(c,pts,col)
            a,b,d=pts[0],pts[1],pts[2]
            poly(c,[a,b,d,(b[0]+1,b[1]+7)],'536163')
        # The stream bends around a broad near boulder; moss stays subdued.
        poly(c,[(153,177),(171,176),(187,180),(188,185),(174,189),
                (166,200),(109,200),(129,189),(143,185),(146,180)],'284658')
        poly(c,[(151,178),(169,178),(178,182),(174,185),(157,188),
                (147,197),(137,200),(124,200),(140,190),(148,185)],'668F9A')
        poly(c,[(0,183),(22,177),(45,182),(61,179),(83,186),
                (109,190),(119,200),(0,200)],'0F1C26')
        poly(c,[(0,181),(22,175),(43,180),(35,184),(20,182),(7,187)],'384D49')
        poly(c,[(187,200),(202,185),(224,182),(241,187),
                (264,180),(286,183),(305,175),(320,180),(320,200)],'111E27')
        poly(c,[(220,184),(234,178),(247,182),(243,189),(229,191)],'35484C')
    return c


LAND=[terrain(i) for i in range(4)]
mask=cv2.imread(str(ROOT/'assets/omarchy-mask.png'),cv2.IMREAD_UNCHANGED)
LOGO=np.zeros((H,W),bool)
LOGO[72:129,38:281]=cv2.resize(mask[:,:,3],(243,57),interpolation=cv2.INTER_NEAREST)>127
from aurora import aurora


def sky(kind,phase):
    c=np.full((H,W,3),rgb('101522' if kind in [0,3] else '161526'),np.uint8)
    poly(c,[(0,115),(49,110),(103,116),(165,108),(230,114),
            (277,109),(320,112),(320,200),(0,200)],'1C2737' if kind!=1 else '24263D')
    draw_stars(c,kind)
    pixels,active=aurora(kind,phase)
    # Let stationary stars show through the dimmer light. This also keeps
    # the emission from darkening any channel of the underlying night sky.
    c[active]=np.clip(c[active].astype(np.float32)+pixels[active],0,255).astype(np.uint8)
    draw_meteor(c,kind,phase)
    return c


def logo_frame(phase):
    from aurora import sheet
    # Use the same long, pleated light field as the landscape veils. The logo
    # is a clipping mask, never a stack of flat horizontal colour fills.
    hem=[(12,120),(45,115),(76,119),(106,110),(136,118),
         (165,114),(195,120),(226,110),(257,118),(302,114)]
    density=sheet(hem,phase,[.5,.72,.54,.92,.62,.70,.95,.56,.82,.5],
                  [62,65,57,66,60,64,59,66,60,63],
                  strength=1.1,seed=11,motion=.65,tilt=.008)
    light=-np.expm1(-density*1.6)
    # Overlapping altitude regions retain horizontal colour flow while their
    # hanging strands, dark gaps and pale concentrations move together.
    height=Y-72-2.5*np.sin(X/45-phase)-1.1*np.sin(X/23+phase)
    # Soft overlapping transitions rather than averaged wide hue bands: keep
    # the upper red chromatic and avoid a grey/olive red-green mixture.
    edges=[11,33,40,47,54]
    transitions=np.stack([1/(1+np.exp(np.clip(-(height-edge)/2.5,-60,60)))
                          for edge in edges])
    weights=np.concatenate([1-transitions[:1],
                            transitions[:-1]-transitions[1:],
                            transitions[-1:]],axis=0)
    colors=['C84C73','2CDD68','43BEA4','4A8CC5','9261C0','D16BAF']
    color=np.einsum('iyx,ic->yxc',weights,
                    np.array([rgb(value) for value in colors],np.float32))
    # A faint coloured bed keeps every letter legible. Most of its luminosity
    # comes from the translucent veil; pale mint is limited to dense strands.
    fill=rgb('140F1F')+color*(.08+1.12*light[...,None])
    pale=np.exp(-.5*((height-29)/13)**2)*light**4
    fill+=pale[...,None]*np.array([62,49,63])
    c=np.full((H,W,3),rgb('140F1F'),np.uint8)
    c[LOGO]=np.clip(fill[LOGO],0,255).astype(np.uint8)
    return c


def frame(kind,phase):
    phase%=2*np.pi
    if kind==4:return logo_frame(phase)
    c=sky(kind,phase)
    # Reflected light and masses, with sparse horizontal fragments and no mesh.
    horizon=[151,135,147,None][kind]
    if horizon is not None:
        complete=c.copy();opaque=LAND[kind][:,:,3]>0
        complete[opaque]=LAND[kind][:,:,:3][opaque]
        for y in range(horizon,H):
            source=max(0,horizon-1-int((y-horizon)*[1.75,1.15,1.8,1][kind]))
            shift=int(np.floor(.65*np.sin(phase+y/13)))
            reflected=np.roll(complete[source],shift,axis=0).astype(np.float32)
            c[y]=np.clip(reflected*[.32,.28,.34,0][kind]+rgb('091523'),0,255).astype(np.uint8)
        for y,x1,x2 in [(horizon+7,15,84),(horizon+17,167,252),(horizon+31,85,177),(horizon+43,214,289)]:
            if y<H:c[y:y+1,x1:x2]=rgb('1A2B3A')
    opaque=LAND[kind][:,:,3]>0
    c[opaque]=LAND[kind][:,:,:3][opaque]
    if kind==3:
        for x,start,length in [(160,0,4),(163,11,3),(159,21,4)]:
            y=115+int((start+phase/(2*np.pi)*50)%50)
            c[y:min(y+length,167),x]=rgb('D0E8E2')
    return c


def render(kind,posters_only=False):
    name=NAMES[kind]
    for folder in ['backgrounds','previews']:(ROOT/folder).mkdir(exist_ok=True)
    phase=2*np.pi*POSTER_FRAMES[kind]/(FPS*SECONDS)
    poster=cv2.resize(frame(kind,phase),(2560,1600),interpolation=cv2.INTER_NEAREST)
    cv2.imwrite(str(ROOT/f'previews/{name}.png'),cv2.cvtColor(poster,cv2.COLOR_RGB2BGR))
    if posters_only:return
    command=['ffmpeg','-v','warning','-y','-f','rawvideo','-pix_fmt','rgb24',
             '-s','320x200','-r',str(FPS),'-i','-',
             '-vf','scale=2560:1600:flags=neighbor:out_color_matrix=bt709',
             '-an','-c:v','libx264','-threads','2','-preset','slow','-crf','14',
             '-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709',
             '-color_trc','bt709','-movflags','+faststart',str(ROOT/f'backgrounds/{name}.mp4')]
    encoder=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for i in range(FPS*SECONDS):
            encoder.stdin.write(frame(kind,2*np.pi*i/(FPS*SECONDS)).tobytes())
        encoder.stdin.close()
        if encoder.wait():raise RuntimeError(name+' failed to encode')
    finally:
        if encoder.poll() is None:encoder.kill();encoder.wait()
    print('Finished '+name,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--posters-only',action='store_true')
    parser.add_argument('--scene',type=int,choices=range(1,6))
    args=parser.parse_args()
    kinds=[args.scene-1] if args.scene else range(5)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda kind:render(kind,args.posters_only),kinds))
