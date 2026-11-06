"""Check actual theme roles and resolved Aether highlights, without applying it."""
from pathlib import Path
import argparse,json,os,re,subprocess,tempfile,tomllib
from build_ui import contrast,composite

ROOT=Path(__file__).resolve().parents[1]


def audit(aether_dir):
    p=tomllib.loads((ROOT/'colors.toml').read_text());checks=[]
    def add(role,fg,bg,minimum=4.5):
        checks.append(dict(role=role,foreground=fg,background=bg,ratio=contrast(fg,bg),minimum=minimum))
    foregrounds=['foreground','dark_foreground','light_foreground','bright_foreground','muted','red','orange','yellow','green','cyan','blue','magenta','brown','bright_red','bright_yellow','bright_green','bright_cyan','bright_blue','bright_magenta','accent']
    for fg in foregrounds:
        for bg in ['background','dark_background','darker_background','lighter_background']:
            add(f'Palette: {fg} on {bg}',p[fg],p[bg])
    add('Selected text',p['selection_foreground'],p['selection'])
    vs=json.loads((ROOT/'vscode-theme.json').read_text())['colors']
    for key,fg in vs.items():
        if not isinstance(fg,str) or not re.fullmatch('#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?',fg):continue
        if not (key.endswith('.foreground') or key.endswith('Foreground') or key=='foreground'):continue
        candidates=[key.replace('Foreground','Background').replace('.foreground','.background')]
        if key.startswith(('editor','peekView','notebook')):candidates+=['editor.background']
        elif key.startswith('statusBar'):candidates+=['statusBar.background']
        elif key.startswith('tab.'):candidates+=['tab.inactiveBackground','editor.background']
        elif key.startswith('terminal'):candidates+=['terminal.background']
        elif key.startswith('sideBar'):candidates+=['sideBar.background']
        elif key.startswith('activityBar'):candidates+=['activityBar.background']
        elif key.startswith('panel'):candidates+=['panel.background']
        else:candidates+=['editor.background']
        bgkey=next((k for k in candidates if k in vs and k!=key),'editor.background')
        bg=composite(vs[bgkey],p['background']);fg=composite(fg,bg)
        minimum=3.0 if any(x in key for x in ['Whitespace','Ruler','Overview','progress']) else 4.5
        add(f'VS Code: {key} on {bgkey}',fg,bg,minimum)
    for fgkey,bgkey in [('button.foreground','button.hoverBackground'),
                        ('button.secondaryForeground','button.secondaryHoverBackground'),
                        ('extensionButton.foreground','extensionButton.hoverBackground')]:
        bg=composite(vs[bgkey],p['background']);add('VS Code hover: '+fgkey,composite(vs[fgkey],bg),bg)
    add('Obsidian tags',p['accent'],p['selection'])
    add('Obsidian accent buttons',p['background'],p['accent'])
    for alpha,label in [('B3','muted'),('99','faint')]:
        add('Obsidian '+label+' text',composite(p['foreground']+alpha,p['background']),p['background'])
    for bg in ['background','lighter_background','selection']:
        add('Keyboard focus indicator on '+bg,p['accent'],p[bg],3)
    for alpha,label in [('0A','normal fill'),('14','hover fill'),('2E','selected fill')]:
        bg=composite(p['foreground']+alpha,p['background'])
        add('Shell '+label+' text',p['foreground'],bg)
        add('Shell '+label+' focus outline',p['accent'],bg,3)
    add('Lock error text',p['red'],p['background'])
    # Resolve the installed Aether v3 implementation with the actual theme opts.
    if not (aether_dir/'lua/aether').is_dir():raise RuntimeError('Aether v3 is required for the Neovim runtime audit; use --aether-dir')
    with tempfile.TemporaryDirectory(prefix='borealis-nvim-') as work:
        output=Path(work)/'highlights.json'
        env=os.environ.copy();env.update(BOREALIS_THEME_DIR=str(ROOT),BOREALIS_AETHER_DIR=str(aether_dir),BOREALIS_AUDIT_OUT=str(output))
        subprocess.run(['nvim','--headless','-u','NONE','-i','NONE','-n','-l',str(ROOT/'tools/audit_neovim.lua')],env=env,check=True)
        highlights=json.loads(output.read_text())
    for row in highlights:
        if row['name']=='EndOfBuffer':continue # deliberately hidden filler, not content
        minimum=3 if row['name'] in ['MiniStarterItemBullet','DapUIFloatBorder'] else 4.5
        add('Neovim: '+row['name'],row['fg'],row['bg'],minimum)
    for f in ROOT.glob('*.json'):json.loads(f.read_text())
    for f in ROOT.glob('*.toml'):tomllib.loads(f.read_text())
    failures=[r for r in checks if r['ratio']<r['minimum']]
    text=[r for r in checks if r['minimum']==4.5]
    report={'scope':'Opaque default surfaces; stock Omarchy templates plus Borealis overrides and actual Aether v3 highlights. Not a whole-desktop WCAG certification or arbitrary ANSI/opacity audit.',
            'standard':'WCAG 2.2 contrast formula; normal text >=4.5, meaningful non-text indicators >=3',
            'sources':['https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html','https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html'],
            'checks':checks,'summary':{'pairs':len(checks),'text_pairs':len(text),'minimum_text_ratio':min(r['ratio'] for r in text),'failures':len(failures)},'failures':failures}
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports/readability.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['summary'],indent=2))
    if failures:print(json.dumps(failures,indent=2));raise SystemExit(1)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--aether-dir',type=Path,default=Path.home()/'.local/share/nvim/lazy/aether')
    audit(parser.parse_args().aether_dir)
