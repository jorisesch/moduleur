#!/usr/bin/env python3
"""Validate a compact Moduleur patch and render vector overlays plus a two-page PDF."""
import argparse
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
import tempfile
from xml.sax.saxutils import escape

SKILL = Path(__file__).resolve().parents[1]
PANEL = json.loads((SKILL / 'references/panel.json').read_text())
W, H = PANEL['template']['width'], PANEL['template']['height']
COLORS = {'audio': '#007f78', 'pitch': '#245fc4', 'cv': '#a05500', 'gate': '#bd3548', 'midi': '#7c42a3'}
SIGNAL_LABELS = {'audio': 'AUDIO', 'pitch': 'PITCH CV', 'cv': 'MOD CV', 'gate': 'GATE/TRIG', 'midi': 'MIDI'}
INK = '#152b39'
STYLE_PROFILES = {
    'classic': {'ink': INK, 'accent': '#007f78', 'panel': '#edf2f4', 'paper': '#ffffff', 'body': 'Helvetica', 'bold': 'Helvetica-Bold', 'rule': 'bar'},
    'editorial': {'ink': '#202020', 'accent': '#9b3b2f', 'panel': '#f2eee8', 'paper': '#fbfaf7', 'body': 'Times-Roman', 'bold': 'Helvetica-Bold', 'rule': 'line'},
    'minimal': {'ink': '#111111', 'accent': '#315efb', 'panel': '#f5f5f5', 'paper': '#ffffff', 'body': 'Helvetica', 'bold': 'Helvetica-Bold', 'rule': 'thin'},
    'archive': {'ink': '#263128', 'accent': '#6c735f', 'panel': '#e8e8df', 'paper': '#f4f3ea', 'body': 'Courier', 'bold': 'Courier-Bold', 'rule': 'double'},
    'industrial': {'ink': '#171717', 'accent': '#e05a24', 'panel': '#ececec', 'paper': '#f8f8f6', 'body': 'Helvetica', 'bold': 'Helvetica-Bold', 'rule': 'blocks'},
}
DEFAULT_STYLE = 'minimal'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(obj, allowed, context):
    require(isinstance(obj, dict), f'{context}: expected an object')
    require(not set(obj) - set(allowed), f'{context}: unknown keys {set(obj) - set(allowed)}')


def text(value, context, limit=1000):
    require(isinstance(value, str) and value.strip() and len(value) <= limit,
            f'{context}: expected nonempty text, at most {limit} characters')
    require(all(32 <= ord(c) <= 126 for c in value),
            f'{context}: use printable ASCII (portable PDF fonts)')


def point(value, context):
    require(isinstance(value, (list, tuple)) and len(value) == 2, f'{context}: expected [x,y]')
    for v, maximum in zip(value, [W, H]):
        require(type(v) in (int, float) and math.isfinite(v) and 0 <= v <= maximum,
                f'{context}: coordinate outside template')


def validate(patch):
    keys(patch, ['schema_version', 'id', 'title', 'revision', 'status', 'summary', 'brain',
                 'description', 'external', 'connections', 'controls', 'normalled_policy', 'sources'], 'patch')
    require(patch.get('schema_version') == 1, 'Expected schema_version 1')
    for k in ['id', 'title', 'revision', 'summary', 'normalled_policy']:
        text(patch.get(k), k, 1000 if k == 'normalled_policy' else 180)
    require(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', patch['id']), 'id must be a lowercase slug')
    require(patch.get('status') in ['untested', 'auditioned'], 'status must be untested or auditioned')
    brain = patch.get('brain')
    keys(brain, ['firmware', 'version', 'mode', 'layout', 'settings'], 'brain')
    for k in ['firmware', 'version', 'mode']:
        text(brain.get(k), 'brain.' + k, 80)
    if brain['firmware'] == 'Le Controlleur':
        require(brain['mode'] in ['Sequencer', 'MIDI to CV'], 'Le Controlleur mode must be explicit')
    require(brain.get('layout') in ['three-knobs-two-buttons', 'settings-inset'], 'Unknown Brain layout')
    for name, value in [('brain.settings', brain.get('settings')), ('sources', patch.get('sources'))]:
        require(isinstance(value, list) and value, f'{name}: expected nonempty list')
        for item in value:
            text(item, name, 400)
    desc = patch.get('description')
    keys(desc, ['sound', 'setup', 'play', 'variations'], 'description')
    for k in ['sound', 'setup', 'play', 'variations']:
        require(isinstance(desc.get(k), list) and desc[k], f'description.{k}: expected nonempty list')
        for item in desc[k]:
            text(item, f'description.{k}', 800)
    ports = copy.deepcopy(PANEL['ports'])
    external = patch.get('external', {})
    require(isinstance(external, dict), 'external must be an object')
    for name, p in external.items():
        require(re.fullmatch(r'external\.[a-z0-9_-]+', name), 'External IDs must start with external.')
        keys(p, ['label', 'direction', 'x', 'y'], name)
        text(p.get('label'), name + '.label', 45)
        require(p.get('direction') in ['in', 'out'], name + ': invalid direction')
        point([p.get('x'), p.get('y')], name)
        ports[name] = p
    connections = patch.get('connections')
    require(isinstance(connections, list) and connections, 'connections must be nonempty')
    seen, inputs, cable_outputs, used, used_external = set(), set(), set(), set(), set()
    for c in connections:
        keys(c, ['id', 'from', 'to', 'kind', 'signal', 'via', 'label_at'], 'connection')
        text(c.get('id'), 'connection.id', 4)
        require(re.fullmatch(r'[A-Z0-9]+', c['id']), 'Connection IDs must be short uppercase letters/digits')
        require(c['id'] not in seen, 'Duplicate connection ID: ' + c['id'])
        seen.add(c['id'])
        require(c.get('kind') in ['cable', 'normal'], 'Connection kind must be cable or normal')
        require(c.get('signal') in COLORS, 'Unknown connection signal')
        for k, direction in [('from', 'out'), ('to', 'in')]:
            require(c.get(k) in ports, f"{c['id']}: unknown port {c.get(k)}")
            require(ports[c[k]]['direction'] == direction, f"{c['id']}: {k} endpoint is not an {direction}put")
            if c[k].startswith('external.'):
                used_external.add(c[k])
                require(c['kind'] == 'cable', 'External leads cannot be normalled')
            else:
                used.add(ports[c[k]]['module'])
        require(c['to'] not in inputs, 'Input connected twice (including normals): ' + c['to'])
        inputs.add(c['to'])
        if c['kind'] == 'cable':
            require(c['from'] not in cable_outputs, 'Multiple cables from one output: declare a splitter/multiple')
            cable_outputs.add(c['from'])
        require(isinstance(c.get('via', []), list), 'via must be a list of points')
        for v in c.get('via', []):
            point(v, c['id'] + '.via')
        if 'label_at' in c:
            point(c['label_at'], c['id'] + '.label_at')
    require(used_external == set(external), 'Unused external endpoints must be removed')
    controls = patch.get('controls')
    require(isinstance(controls, dict), 'controls must be an object')
    for name, setting in controls.items():
        require(name in PANEL['controls'], 'Unknown control: ' + name)
        keys(setting, ['position', 'value', 'critical', 'irrelevant'], name)
        if 'irrelevant' in setting:
            require(set(setting) == {'irrelevant'}, f'{name}: irrelevant cannot also have a position')
            text(setting['irrelevant'], name + '.irrelevant', 240)
        else:
            text(setting.get('value'), name + '.value', 28)
            require(type(setting.get('critical')) is bool, name + ': explicitly mark critical true/false')
            if PANEL['controls'][name]['kind'] == 'selector':
                require(setting['value'] in PANEL['controls'][name]['values'], name + ': invalid selector value')
                require('position' not in setting, name + ': selector uses value, not position')
            else:
                v = setting.get('position')
                require(type(v) in (int, float) and math.isfinite(v) and 0 <= v <= 1,
                        name + ': position must be 0..1')
    missing = [k for k, c in PANEL['controls'].items() if c['module'] in used and k not in controls]
    require(not missing, 'Missing settings or irrelevant reasons: ' + ', '.join(missing))
    if brain['layout'] == 'settings-inset':
        require(all('irrelevant' in v for k, v in controls.items() if k.startswith('brain.')),
                'Unknown Brain layout: put settings in inset, not guessed knob positions')
    return ports


class Drawing:
    """Same vector geometry sent to ReportLab and transparent SVG."""
    def __init__(self, canvas):
        self.canvas = canvas
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">']

    def line(self, points, color, width=1.5, dashed=False):
        c = self.canvas
        c.setStrokeColor(color); c.setLineWidth(width); c.setDash(4, 3) if dashed else c.setDash()
        p = c.beginPath(); p.moveTo(points[0][0], H - points[0][1])
        for x, y in points[1:]: p.lineTo(x, H-y)
        c.drawPath(p)
        d = ' stroke-dasharray="4 3"' if dashed else ''
        self.svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="{width}"{d}/>')

    def circle(self, x, y, r, stroke, fill='white', width=1):
        c=self.canvas; c.setDash(); c.setLineWidth(width); c.setStrokeColor(stroke); c.setFillColor(fill)
        c.circle(x,H-y,r,stroke=1,fill=1)
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" stroke="{stroke}" fill="{fill}" stroke-width="{width}"/>')

    def rect(self, x, y, w, h, fill):
        c=self.canvas; c.setFillColor(fill); c.rect(x,H-y-h,w,h,stroke=0,fill=1)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>')

    def label(self, x, y, value, size=8, color=INK, align='middle', backing=True):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        width=stringWidth(value,'Helvetica',size)
        left=x-width/2 if align=='middle' else x
        if backing: self.rect(left-2,y-size+1,width+4,size+3,'white')
        c=self.canvas; c.setFillColor(color); c.setFont('Helvetica',size)
        c.drawString(left,H-y,value)
        self.svg.append(f'<text x="{x}" y="{y}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" fill="{color}" text-anchor="{align}">{escape(value)}</text>')


def overlay(patch, ports):
    from reportlab.pdfgen import canvas
    stream=io.BytesIO(); c=canvas.Canvas(stream,pagesize=(W,H),pageCompression=1,invariant=1)
    c.setTitle(patch['title'] + ' - overlay')
    d=Drawing(c)
    # User-requested presentation change: hide only HOG in the footer.
    # The downloaded original and the remaining Shmoergh artwork stay intact.
    d.rect(506,871,35,14,'white')
    d.label(388,53,patch['title'],16,align='start')
    d.label(388,75,'Solid = cable    Dashed = active internal normal',8,align='start')
    # Preserve the official panel artwork and printed labels. Firmware names are
    # documented on page one; a different naming scheme is not a panel error.
    # Draw wiring first, allowing control indicators to remain legible on top.
    for route in patch['connections']:
        start,end=ports[route['from']],ports[route['to']]
        points=[[start['x'],start['y']],*route.get('via',[]),[end['x'],end['y']]]
        color=COLORS[route['signal']]; normal=route['kind']=='normal'
        d.line(points,'white',4.2)
        d.line(points,color,1.4 if normal else 2.2,normal)
        # Direction arrow at the destination, independent of crossings.
        a,b=points[-2:]; length=math.hypot(b[0]-a[0],b[1]-a[1])
        if length:
            ux,uy=(b[0]-a[0])/length,(b[1]-a[1])/length
            tip=[b[0]-ux*6,b[1]-uy*6]
            d.line([[tip[0]-ux*7-uy*3,tip[1]-uy*7+ux*3],tip,
                    [tip[0]-ux*7+uy*3,tip[1]-uy*7-ux*3]],color,1.4)
        for p in [start,end]: d.circle(p['x'],p['y'],4.2,color,'white',1.5)
        lx,ly=route.get('label_at',[(points[0][0]+points[1][0])/2,(points[0][1]+points[1][1])/2])
        d.circle(lx,ly,8,color,'white',1.2);d.label(lx,ly+2.8,route['id'],7.5,color,backing=False)
    for name, setting in patch['controls'].items():
        ctl=PANEL['controls'][name];x,y=ctl['x'],ctl['y']
        if 'irrelevant' in setting:
            # Small neutral dot denotes covered but nonfunctional control.
            d.label(x,y+4,'--',8,'#7d8790')
            continue
        color=INK if not setting['critical'] else '#bb3d14'
        width=2.8 if setting['critical'] else 1.7
        if ctl['kind']=='slider':
            sy=ctl['bottom']-setting['position']*(ctl['bottom']-ctl['top'])
            d.rect(x-6,sy-2.5,12,5,color)
            d.label(x+22,sy+3,setting['value'],7,color)
        else:
            if ctl['kind']=='selector':
                pos=ctl['values'].index(setting['value'])/2
                # Waveform legends on the original sheet sit at upper/right/lower right.
                angle=math.radians(45-90*pos)
            else:
                angle=math.radians(225-270*setting['position'])
            radius=ctl.get('radius',10)
            d.line([[x,y],[x+radius*math.cos(angle),y-radius*math.sin(angle)]],color,width)
            d.label(x,y+radius+10,setting['value'],7,color)
    for name,e in patch.get('external',{}).items():
        d.label(e['x'],e['y']-12,e['label'],8)
    d.label(55,873,'PATCH KEY',9,align='start')
    for i,(name,color) in enumerate(COLORS.items()):
        d.line([[55+i*93,891],[72+i*93,891]],color,2)
        d.label(77+i*93,894,SIGNAL_LABELS[name],8,color,align='start')
    d.rect(50,902,405,38,'white')
    d.label(55,914,'Orange control marks = critical. -- = irrelevant (reasons on page 1).',7,align='start',backing=False)
    d.label(55,928,'Positions are physical starting points. Cable IDs and firmware settings: page 1.',7,align='start',backing=False)
    c.showPage();c.save();d.svg.append('</svg>')
    return stream.getvalue(),'\n'.join(d.svg)+'\n'


def description(patch, ports, style_name=DEFAULT_STYLE):
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph
    from reportlab.pdfbase.pdfmetrics import stringWidth
    require(style_name in STYLE_PROFILES, 'Unknown style: '+style_name)
    profile=STYLE_PROFILES[style_name]
    ink=profile['ink']; accent=profile['accent']; body=profile['body']; boldfont=profile['bold']
    stream=io.BytesIO();c=canvas.Canvas(stream,pagesize=(W,H),pageCompression=1,invariant=1)
    c.setTitle(patch['title']);margin=44
    c.setFillColor(profile['paper']);c.rect(0,0,W,H,stroke=0,fill=1)
    c.setFillColor(ink)
    if profile['rule']=='bar': c.rect(0,H-13,W,13,stroke=0,fill=1)
    elif profile['rule']=='line': c.rect(margin,H-18,W-2*margin,1.5,stroke=0,fill=1)
    elif profile['rule']=='thin': c.rect(0,H-5,W,5,stroke=0,fill=1)
    elif profile['rule']=='double':
        c.rect(margin,H-17,W-2*margin,1,stroke=0,fill=1);c.rect(margin,H-21,W-2*margin,1,stroke=0,fill=1)
    else:
        c.setFillColor(accent)
        for x in range(0,int(W),44): c.rect(x,H-13,26,13,stroke=0,fill=1)
    def label(x,y,value,size=10,bold=False,color=INK):
        use_color=ink if color==INK else color
        c.setFillColor(use_color);c.setFont(boldfont if bold else body,size);c.drawString(x,H-y,value)
    def para(value,x,y,width,size=10,leading=14,color=INK):
        use_color=ink if color==INK else color
        paragraph_style=ParagraphStyle('body',fontName=body,fontSize=size,leading=leading,textColor=use_color)
        p=Paragraph(escape(value),paragraph_style);_,height=p.wrap(width,H)
        require(y+height<885,'Description page overflow: shorten prose or settings; do not add a second description page')
        p.drawOn(c,x,H-y-height)
        return y+height
    label(margin,46,'MODULEUR / PATCH NOTES',10,True)
    require(stringWidth(patch['title'],boldfont,27)<W-2*margin,'Title too long')
    label(margin,85,patch['title'],27,True)
    c.setFillColor(ink);c.setFont(body,8)
    c.drawRightString(W-margin,H-106,'SOURCE: github.com/jorisesch/moduleur')
    top=para(patch['summary'],margin,121,W-2*margin,11,15)+20
    # Firmware block is always prominent and cannot be omitted.
    brain=patch['brain']; block_height=52+len(brain['settings'])*15
    c.setFillColor(profile['panel']);c.rect(margin,H-top-block_height,W-2*margin,block_height,fill=1,stroke=0)
    label(margin+12,top+20,f"BRAIN: {brain['firmware']}  |  VERSION: {brain['version']}  |  MODE: {brain['mode']}",11,True)
    label(margin+12,top+37,'LAYOUT: '+brain['layout'],8)
    by=top+46
    for setting in brain['settings']:
        require(stringWidth(setting,'Helvetica',9)<W-2*margin-24,'Brain setting too long: split it into short entries')
        by=para(setting,margin+12,by,W-2*margin-24,9,13)+2
    y=top+block_height+22; gap=25; col=(W-2*margin-gap)/2
    def section(title, items, x, y, size=9.5):
        label(x,y+10,title.upper(),9,True,accent);y+=19
        for item in items:
            y=para(item,x,y,col,size,12)+4
        return y+9
    left=y;right=y
    for key,title in [('sound','Sound'),('setup','Setup'),('play','Play'),('variations','Variations')]:
        left=section(title,patch['description'][key],margin,left)
    left=section('Normalled wiring',[patch['normalled_policy']],margin,left,9)
    entries=[]
    for route in patch['connections']:
        entries.append(f"{route['id']}  {ports[route['from']]['label']} > {ports[route['to']]['label']}"
                       + (' [internal normal]' if route['kind']=='normal' else ''))
    right=section('Complete connection list',entries,margin+col+gap,right,9)
    critical={};irrelevant={}
    for name,s in patch['controls'].items():
        module,control=name.split('.',1)
        if s.get('critical'):critical.setdefault(module,[]).append(control+': '+s['value'])
        if 'irrelevant' in s:irrelevant.setdefault(module,[]).append(control+': '+s['irrelevant'])
    right=section('Critical starting positions',[k.upper()+' / '+ '; '.join(v) for k,v in critical.items()],margin+col+gap,right,9)
    if irrelevant:right=section('Controls not affecting this patch',[k.upper()+' / '+ '; '.join(v) for k,v in irrelevant.items()],margin+col+gap,right,8)
    require(max(left,right)<868,'Description page overflow: shorten prose, controls, or connection labels')
    label(margin,889,'Sources / attribution',8,True)
    sy=897
    for source in patch['sources']:
        # Compact source names/URLs; long source lists must be shortened by author.
        require(len(patch['sources'])<=3,'Use at most three concise source references')
        require(stringWidth(source,'Helvetica',7)<W-2*margin,'Source line too long')
        label(margin,sy+7,source,7);sy+=10
    label(margin,938,'Official background: Shmoergh. Patch notes and overlay are community-authored.',7)
    c.showPage();c.save();return stream.getvalue()


def build(patch_path, background, output, validate_only=False, style=DEFAULT_STYLE):
    patch=json.loads(patch_path.read_text());ports=validate(patch)
    if validate_only:
        print('Valid patch:',patch['id']);return
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise ValueError('Install renderer dependencies: python -m pip install -r '+str(SKILL/'scripts/requirements.txt')) from exc
    require(background.is_file(),'Missing official patch sheet: run downloads/refresh.sh or pass --background')
    require(hashlib.sha256(background.read_bytes()).hexdigest()==PANEL['template']['sha256'],
            'Official template SHA-256 changed: inspect it and revise panel.json before rendering')
    base=PdfReader(background)
    require(len(base.pages)==1,'Expected one background page')
    page=base.pages[0]
    require(abs(float(page.mediabox.width)-W)<0.01 and abs(float(page.mediabox.height)-H)<0.01,'Template dimensions mismatch')
    require(style in STYLE_PROFILES, 'Unknown style: '+style)
    overlay_pdf,overlay_svg=overlay(patch,ports);front=description(patch,ports,style)
    writer=PdfWriter();writer.add_page(PdfReader(io.BytesIO(front)).pages[0]);writer.add_page(page)
    writer.pages[1].merge_page(PdfReader(io.BytesIO(overlay_pdf)).pages[0])
    for output_page in writer.pages:
        output_page.compress_content_streams()
    writer.add_metadata({'/Title':patch['title'],'/Subject':patch['brain']['firmware']+' / '+patch['brain']['mode'],
                         '/Author':'Moduleur community patch notes'})
    writer.compress_identical_objects()
    combined=io.BytesIO();writer.write(combined)
    output.mkdir(parents=True,exist_ok=True)
    # Construct and validate everything before replacing final outputs.
    pdf_name='patch.pdf' if style==DEFAULT_STYLE else f'patch-{style}.pdf'
    artifacts=[(pdf_name,combined.getvalue())]
    if style==DEFAULT_STYLE: artifacts=[('overlay.svg',overlay_svg.encode()),('overlay.pdf',overlay_pdf),*artifacts]
    for name,data in artifacts:
        with tempfile.NamedTemporaryFile(dir=output,delete=False) as f:
            f.write(data);temporary=Path(f.name)
        temporary.replace(output/name)
        print(f'{output/name}: {len(data):,} bytes')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('patch',type=Path)
    parser.add_argument('--background',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--validate',action='store_true',help='Validate JSON without PDF dependencies')
    parser.add_argument('--style',choices=sorted(STYLE_PROFILES),default=DEFAULT_STYLE)
    args=parser.parse_args()
    # Find project root by its resource directory, not by .git (works in exports).
    project=next((p for p in args.patch.resolve().parents if (p/'downloads').is_dir()),Path.cwd())
    background=args.background or project/'downloads/patchsheets/moduleur-patch-sheet.pdf'
    build(args.patch,background,args.output or args.patch.parent,args.validate,args.style)


if __name__=='__main__':
    try:main()
    except (ValueError, KeyError, TypeError, OSError, ImportError) as exc:
        sys.exit('Patch error: '+str(exc))
