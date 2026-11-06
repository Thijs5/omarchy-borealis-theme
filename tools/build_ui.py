"""Build Borealis app overrides from installed Omarchy templates.

Only the staging-directory assignments are changed in a temporary copy of the
stock renderer. HOME, live user templates, and system files are never changed.
"""
from pathlib import Path
import argparse,json,os,re,shutil,subprocess,tempfile,tomllib

ROOT=Path(__file__).resolve().parents[1]


def luminance(value):
    rgb=[int(value[i:i+2],16)/255 for i in (1,3,5)]
    return sum((v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4)*w for v,w in zip(rgb,[.2126,.7152,.0722]))


def contrast(a,b):
    x,y=sorted([luminance(a),luminance(b)])
    return (y+.05)/(x+.05)


def composite(value,background):
    if len(value)!=9:return value
    alpha=int(value[7:9],16)/255
    return '#'+''.join(f'{round(int(value[i:i+2],16)*alpha+int(background[i:i+2],16)*(1-alpha)):02X}' for i in (1,3,5))


def neovim_callback():
    return '''      on_highlights = function(h, c)
        -- Aether uses muted as both text and a filled badge/menu background.
        -- Separate selected fills and resolve low-contrast explicit text pairs.
        h.Visual = { fg = c.bright_fg, bg = c.selection }
        h.VisualNOS = { fg = c.bright_fg, bg = c.selection }
        h.PmenuSel = { fg = c.bright_fg, bg = c.selection }
        h.PmenuMatchSel = { fg = c.bright_cyan, bg = c.selection }
        h.BlinkCmpMenuSelection = { fg = c.bright_fg, bg = c.selection }
        h["@tag.delimiter.tsx"] = { fg = c.blue }
        local function lum(hex)
          if type(hex) ~= "string" or not hex:match("^#%x%x%x%x%x%x$") then return nil end
          local channels = {}
          for i = 2, 6, 2 do
            local v = tonumber(hex:sub(i, i + 1), 16) / 255
            channels[#channels + 1] = v <= 0.04045 and v / 12.92 or ((v + 0.055) / 1.055) ^ 2.4
          end
          return channels[1] * 0.2126 + channels[2] * 0.7152 + channels[3] * 0.0722
        end
        local function ratio(a, b)
          local x, y = lum(a), lum(b)
          if not x or not y then return nil end
          return (math.max(x, y) + 0.05) / (math.min(x, y) + 0.05)
        end
        for _, style in pairs(h) do
          if type(style) == "table" and style.fg and style.bg then
            local current = ratio(style.fg, style.bg)
            if current and current < 4.5 then
              for _, candidate in ipairs({ c.fg, c.bg, c.bright_fg, "#000000" }) do
                if ratio(candidate, style.bg) >= 4.5 then style.fg = candidate; break end
              end
            end
          end
        end
      end,
'''


def build(review):
    palette=tomllib.loads((ROOT/'colors.toml').read_text())
    omarchy=Path(os.environ.get('OMARCHY_PATH','/usr/share/omarchy'))
    renderer=(omarchy/'bin/omarchy-theme-set-templates').read_text()
    replacements={
        'NEXT_THEME_DIR="$HOME/.local/state/omarchy/current/next-theme"':'NEXT_THEME_DIR="${BOREALIS_STAGE:?}"',
        'USER_TEMPLATES_DIR="$HOME/.config/omarchy/themed"':'USER_TEMPLATES_DIR="${BOREALIS_TEMPLATES:?}"',
    }
    for old,new in replacements.items():
        if renderer.count(old)!=1:raise RuntimeError('Installed renderer staging interface changed')
        renderer=renderer.replace(old,new)
    with tempfile.TemporaryDirectory(prefix='borealis-ui-') as work:
        work=Path(work);stage=work/'stage';stage.mkdir();(work/'empty-templates').mkdir()
        shutil.copy2(ROOT/'colors.toml',stage/'colors.toml')
        script=work/'render-templates.sh';script.write_text(renderer)
        env=os.environ.copy();env.update(OMARCHY_PATH=str(omarchy),BOREALIS_STAGE=str(stage),BOREALIS_TEMPLATES=str(work/'empty-templates'))
        subprocess.run(['bash',str(script)],env=env,check=True)
        review.mkdir(parents=True,exist_ok=True)
        raw=review/'stock-generated';shutil.copytree(stage,raw,dirs_exist_ok=True)

        # Keep high-contrast text on dark secondary surfaces. Muted is a text
        # colour; it is no longer reused as an opaque text-bearing fill here.
        vscode=json.loads((stage/'vscode-theme.json').read_text());colors=vscode['colors']
        replacements={
            'button.secondaryBackground':'lighter_background',
            'button.secondaryHoverBackground':'selection',
            'toolbar.activeBackground':'selection',
            'inputOption.hoverBackground':'selection',
            'statusBarItem.activeBackground':'selection',
            'statusBarItem.compactHoverBackground':'selection',
            'commandCenter.activeBackground':'selection',
            'extensionButton.background':'lighter_background',
            'extensionButton.hoverBackground':'selection',
            'notebook.cellStatusBarItemHoverBackground':'selection',
            'notebook.focusedCellBackground':'lighter_background',
            'editorInlayHint.foreground':'dark_foreground',
            'editorLineNumber.dimmedForeground':'muted',
            'focusBorder':'accent','list.focusOutline':'accent',
            'list.inactiveFocusOutline':'muted',
            'list.activeSelectionForeground':'bright_foreground',
            'list.inactiveSelectionForeground':'foreground',
            'statusBarItem.prominentHoverForeground':'bright_foreground',
            'statusBarItem.remoteHoverForeground':'bright_foreground',
            'statusBarItem.errorHoverForeground':'bright_foreground',
            'statusBarItem.warningHoverForeground':'bright_foreground',
            'welcomePage.progress.background':'lighter_background',
        }
        for key,role in replacements.items():colors[key]=palette[role]
        for key in ['editorWhitespace.foreground','editorRuler.foreground']:
            colors[key]=palette['muted']+'A0'
        for key in ['editorOverviewRuler.rangeHighlightForeground',
                    'editorOverviewRuler.wordHighlightForeground',
                    'editorOverviewRuler.wordHighlightTextForeground']:
            colors[key]=palette['accent']+'80'
        colors['editorOverviewRuler.modifiedForeground']=palette['orange']+'B0'
        for key in ['editorOverviewRuler.deletedForeground','diffEditorOverview.removedForeground']:
            colors[key]=palette['red']+'B0'
        (ROOT/'vscode-theme.json').write_text(json.dumps(vscode,indent=2)+'\n')

        obsidian=(stage/'obsidian.css').read_text()
        obsidian+='\n/* Borealis: readable tags and dark text on bright accent buttons. */\n.theme-dark, .theme-light {\n'
        obsidian+=f"  --tag-background: {palette['selection']};\n  --tag-color: {palette['accent']};\n  --text-on-accent: {palette['background']};\n"
        obsidian+=f"  --text-faint: color-mix(in srgb, {palette['foreground']} 60%, transparent);\n"
        obsidian+='}\n'
        obsidian+='\n.theme-dark ::selection, .theme-light ::selection {\n'
        obsidian+=f"  color: {palette['selection_foreground']};\n  background: {palette['selection']};\n"
        obsidian+='}\n'
        (ROOT/'obsidian.css').write_text(obsidian)

        neovim=(stage/'neovim.lua').read_text();needle='      },\n    },'
        if neovim.count(needle)!=1:raise RuntimeError('Neovim template structure changed')
        neovim=neovim.replace(needle,'      },\n'+neovim_callback()+'    },',1)
        (ROOT/'neovim.lua').write_text(neovim)

        # Section overrides preserve all stock control keys while strengthening
        # keyboard focus and selected outlines. Lock text sits on an opaque card.
        shell=(stage/'shell.toml').read_text()
        for section in ['controls','lock']:
            match=re.search(r'^\['+section+r'\]\n.*?(?=^\[|\Z)',shell,re.M|re.S)
            if not match:raise RuntimeError('Missing shell section '+section)
            body=match.group(0)
            if section=='controls':
                for key,value in {'focus-color':f'"{palette["accent"]}"','focus-fill-alpha':'0.10',
                                  'focus-border':f'"{palette["accent"]}"','focus-border-alpha':'1.0',
                                  'selected-border':f'"{palette["accent"]}"','selected-border-width':'1',
                                  'selected-border-alpha':'1.0'}.items():
                    body=re.sub(r'^'+re.escape(key)+r'\s*=.*$',f'{key} = {value}',body,flags=re.M)
            else:body=re.sub(r'^background-alpha\s*=.*$','background-alpha = 1.0',body,flags=re.M)
            (ROOT/f'shell.{section}.toml').write_text(body.rstrip()+'\n')

        # A second stock render applies the real section-override mechanism.
        for name in ['vscode-theme.json','obsidian.css','neovim.lua','shell.controls.toml','shell.lock.toml']:
            shutil.copy2(ROOT/name,stage/name)
        subprocess.run(['bash',str(script)],env=env,check=True)
        final=review/'generated';shutil.copytree(stage,final,dirs_exist_ok=True)
        for f in stage.glob('*'):
            if not f.is_file():continue
            content=f.read_text()
            if '{{' in content:raise RuntimeError('Unresolved template '+f.name)
            if f.suffix=='.json':json.loads(content)
            if f.suffix=='.toml':tomllib.loads(content)
        print('Generated and syntax-checked',len(list(stage.glob('*'))),'theme files.')
        print('Readability overrides:',', '.join(['vscode-theme.json','obsidian.css','neovim.lua','shell.controls.toml','shell.lock.toml']))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--review-dir',type=Path,default=ROOT.parent/'borealis-review/ui')
    build(parser.parse_args().review_dir)
