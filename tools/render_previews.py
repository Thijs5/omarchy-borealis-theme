"""Regenerate selected stills, the repository hero and the five-scene sheet."""
import json
import shutil

import cv2
import numpy as np

from render import ROOT, NAMES, POSTER_FRAMES, FPS, SECONDS, frame, render


def main():
    titles=['Vestrahorn / emerald','Jokulsarlon / rose-violet',
            'Kirkjufell / mint-teal','Svartifoss / violet',
            'Omarchy / aurora veil']
    reports=[]
    # The sheet uses exact integer enlargements, including its cropped logo.
    sheet=np.full((1432,1328,3),[20,15,31],np.uint8)
    for kind,name in enumerate(NAMES):
        render(kind,posters_only=True)
        logical=frame(kind,2*np.pi*POSTER_FRAMES[kind]/(FPS*SECONDS))
        if kind<4:
            x=16+(kind%2)*656
            y=16+(kind//2)*472
            tile=cv2.resize(logical,(640,400),interpolation=cv2.INTER_NEAREST)
        else:
            x,y=24,960
            tile=cv2.resize(logical[50:150],(1280,400),interpolation=cv2.INTER_NEAREST)
        h,w=tile.shape[:2]
        sheet[y:y+h,x:x+w]=tile
        cv2.putText(sheet,titles[kind],(x,y+h+31),cv2.FONT_HERSHEY_SIMPLEX,
                    .72,(223,237,229),1,cv2.LINE_8)
        reports.append({'scene':name,'frame':POSTER_FRAMES[kind],
                        'seconds':POSTER_FRAMES[kind]/FPS,
                        'source':f'backgrounds/{name}.mp4',
                        'still':f'previews/{name}.png'})
    previews=ROOT/'previews'
    shutil.copyfile(previews/'01-vestrahorn.png',ROOT/'preview.png')
    # Retain the filename of the individually approved still for shared links.
    shutil.copyfile(previews/'01-vestrahorn.png',previews/'borealis-vestrahorn-preview.png')
    cv2.imwrite(str(previews/'contact-sheet.png'),cv2.cvtColor(sheet,cv2.COLOR_RGB2BGR))
    (ROOT/'reports/stills.json').write_text(json.dumps({
        'method':'Selected source frames; 2560x1600 nearest-neighbour 8x; original lighting and palette',
        'hero':'preview.png','contact_sheet':'previews/contact-sheet.png','stills':reports},indent=2)+'\n')


if __name__=='__main__':
    main()
