"""Publish exact built models to the official viewer, preserving the original root."""
import hashlib, html, json, os, shutil, urllib.request
from pathlib import Path

REPO='BarryLee911/tt-sky-adc3542-ddr'
VERSIONS=[
    ('legacy',Path('site'),39845775719,'11c630ee90fc27b1330f48f587303fb95fbd12d5',
     '2d3b4ae61f6a28ec43189525f36e57645668198aaa9f15ca137097cf72dcc6da'),
    ('current',Path('site/adc3543-80mhz'),39857447569,'19251b9eab3faf2706395b46df51e0fb04280217',
     '895b60be8f4fcf25d19bc29b9a0c01748448009fc4f1dde9cd28ae718b4694a2')]

for source,dest,run,commit,expected in VERSIONS:
    request=urllib.request.Request(f'https://api.github.com/repos/{REPO}/actions/runs/{run}',
        headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(request) as r: info=json.load(r)
    assert info['head_sha']==commit and info['conclusion']=='success',(run,info['head_sha'],info['conclusion'])
    models=list(Path(source).rglob('*.oas'));assert len(models)==1
    assert hashlib.sha256(models[0].read_bytes()).hexdigest()==expected
    pdk=json.loads(next(Path(source).rglob('pdk.json')).read_text())['PDK']
    assert pdk=='sky130A'
    dest.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(models[0],dest/'tinytapeout.oas')
    gdss=list(Path(source).rglob('*.gds'));assert len(gdss)==1
    shutil.copyfile(gdss[0],dest/'tinytapeout.gds')
    (dest/'index.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>TinyTapeout 3D viewer</title></head>
<body><script>const model=new URL('tinytapeout.oas',location.href).href;
location.replace('https://gds-viewer.tinytapeout.com/?pdk=sky130A&model='+encodeURIComponent(model));
</script><p>Opening the official TinyTapeout viewer.</p></body></html>''',encoding='utf-8')
    (dest/'source.json').write_text(json.dumps(dict(repository=REPO,commit=commit,run_id=run,model_sha256=expected,pdk=pdk),indent=2),encoding='utf-8')

Path('site/adc3543-80mhz/status.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>ADC3543 80MHz layout</title></head>
<body><h1>ADC3543 80MHz / 40MS/s layout</h1><p>Source commit: 19251b9eab3faf2706395b46df51e0fb04280217.</p>
<p>GDS, precheck and functional gate-level simulation passed. Full PVT timing is not closed:
worst setup -2.187ns, worst hold +0.109ns. Retained external DDR assumptions also have no positive common aperture.</p>
<p><a href="./">Open official 3D viewer</a> · <a href="source.json">Model provenance</a> ·
<a href="https://github.com/BarryLee911/tt-sky-adc3542-ddr/pull/1">RTL and validation PR</a></p></body></html>''',encoding='utf-8')
print('MODELS_VERIFIED original root preserved; 80MHz model at adc3543-80mhz/')
