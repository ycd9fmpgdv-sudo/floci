"""Packs index.html and img/*.webp into one HTML file for sending around (e.g. via WhatsApp).

  python3 tools/build-single.py OUT.html
      images inlined; fonts and three.js still load from the internet

  python3 tools/build-single.py OUT.html --standalone VENDOR_DIR
      fully self-contained: no network requests at all. VENDOR_DIR must contain
      three.min.js and OrbitControls.js (npm pack three@0.128.0) and fonts/*.woff2
      (latin files from @fontsource/pirata-one, im-fell-english, im-fell-english-sc,
      special-elite, source-sans-3). Images are re-encoded smaller (needs Pillow).
"""
import base64, io, os, re, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1]
vendor = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '--standalone' else None
s = open(os.path.join(root, 'index.html'), encoding='utf-8').read()

def b64(data, mime):
    return 'data:%s;base64,%s' % (mime, base64.b64encode(data).decode())

def image(name):
    data = open(os.path.join(root, 'img', name + '.webp'), 'rb').read()
    if vendor:
        from PIL import Image
        im = Image.open(io.BytesIO(data))
        im.thumbnail((1500, 1500))
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=66, method=6)
        data = buf.getvalue()
    return b64(data, 'image/webp')

s = re.sub(r'.*<link rel="(manifest|icon|apple-touch-icon)".*\n', '', s)
s, n = re.subn(r' style="background-image:url\(img/forest-(\d)\.webp\)"', r' data-f="\1"', s)
forest_css = ''.join('.forest-layer[data-f="%d"] { background-image: url(%s); }\n' % (i, image('forest-%d' % i)) for i in range(3))
s = s.replace('</style>', forest_css + '</style>', 1)
views = {'viewer-%s-%s' % (v, k): image('viewer-%s-%s' % (v, k)) for v in 'lp' for k in ('bg', 'body', 'head', 'fore')}
old = "var src = 'img/viewer-' + v + '-' + k + '.webp';"
assert old in s
s = s.replace(old, "var src = IMG['viewer-' + v + '-' + k];")
s = s.replace('var META = ', 'var IMG = {' + ','.join('"%s":"%s"' % kv for kv in views.items()) + '};\nvar META = ', 1)
s = re.sub(r'img/([a-z0-9-]+)\.webp', lambda m: image(m.group(1)), s)

if vendor:
    s = re.sub(r'<link rel="(preconnect|stylesheet)" href="https://fonts\.(googleapis|gstatic)\.com[^>]*>\n', '', s)
    fonts = [('IM Fell English SC', 'normal', 400, 'im-fell-english-sc-latin-400-normal'),
             ('IM Fell English', 'normal', 400, 'im-fell-english-latin-400-normal'),
             ('IM Fell English', 'italic', 400, 'im-fell-english-latin-400-italic'),
             ('Pirata One', 'normal', 400, 'pirata-one-latin-400-normal'),
             ('Special Elite', 'normal', 400, 'special-elite-latin-400-normal'),
             ('Source Sans 3', 'normal', 400, 'source-sans-3-latin-400-normal'),
             ('Source Sans 3', 'italic', 400, 'source-sans-3-latin-400-italic'),
             ('Source Sans 3', 'normal', 600, 'source-sans-3-latin-600-normal')]
    face = ''.join('@font-face { font-family: "%s"; font-style: %s; font-weight: %d; font-display: swap; src: url(%s) format("woff2"); }\n'
                   % (fam, sty, w, b64(open(os.path.join(vendor, 'fonts', f + '.woff2'), 'rb').read(), 'font/woff2')) for fam, sty, w, f in fonts)
    s = s.replace('<style>', '<style>\n' + face, 1)
    for name, url in (('three-src', 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'),
                      ('orbit-src', 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js')):
        assert s.count("add('%s')" % url) == 1, url
        s = s.replace("add('%s')" % url, "add(inlineScript('%s'))" % name)
    s = s.replace('var ThreeLoader = (function () {',
                  "function inlineScript(id) { return URL.createObjectURL(new Blob([document.getElementById(id).textContent], { type: 'text/javascript' })); }\nvar ThreeLoader = (function () {", 1)
    libs = ''
    for name, f in (('three-src', 'three.min.js'), ('orbit-src', 'OrbitControls.js')):
        code = open(os.path.join(vendor, f), encoding='utf-8').read()
        assert '</script' not in code
        libs += '<script type="text/plain" id="%s">%s</script>\n' % (name, code)
    s = s.replace('<script>\n(function () {', libs + '<script>\n(function () {', 1)
    rest = re.sub(r'data:[a-z/0-9]+;base64,[A-Za-z0-9+/=]+', '', s)
    external = sorted(set(re.findall(r'https?://(?!claude\.ai|wa\.me|www\.w3\.org)[^\s"\')]+', rest)))
    assert not [u for u in external if 'three' in u or 'fonts.g' in u], external

assert 'img/' not in re.sub(r'data:[a-z/0-9]+;base64,[A-Za-z0-9+/=]+', '', s), 'unresolved image path'
open(out, 'w', encoding='utf-8').write(s)
print('written', out, round(len(s.encode()) / 1e6, 2), 'MB')
