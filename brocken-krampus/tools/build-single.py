"""Packs index.html and img/*.webp into one self-contained HTML file for sending around.
Usage: python3 tools/build-single.py OUTPUT.html   (run from the brocken-krampus folder)"""
import base64, os, re, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(root, 'index.html'), encoding='utf-8').read()

def uri(name):
    data = open(os.path.join(root, 'img', name + '.webp'), 'rb').read()
    return 'data:image/webp;base64,' + base64.b64encode(data).decode()

s = re.sub(r'.*<link rel="(manifest|icon|apple-touch-icon)".*\n', '', s)
s, n = re.subn(r' style="background-image:url\(img/forest-(\d)\.webp\)"', r' data-f="\1"', s)
forest_css = ''.join('.forest-layer[data-f="%d"] { background-image: url(%s); }\n' % (i, uri('forest-%d' % i)) for i in range(3))
s = s.replace('</style>', forest_css + '</style>', 1)
views = {'viewer-%s-%s' % (v, k): uri('viewer-%s-%s' % (v, k)) for v in 'lp' for k in ('bg', 'body', 'head', 'fore')}
old = "var src = 'img/viewer-' + v + '-' + k + '.webp';"
assert old in s
s = s.replace(old, "var src = IMG['viewer-' + v + '-' + k];")
s = s.replace('var META = ', 'var IMG = {' + ','.join('"%s":"%s"' % kv for kv in views.items()) + '};\nvar META = ', 1)
s = re.sub(r'img/([a-z0-9-]+)\.webp', lambda m: uri(m.group(1)), s)
assert 'img/' not in re.sub(r'data:image/webp;base64,[A-Za-z0-9+/=]+', '', s), 'unresolved image path'
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('written', sys.argv[1], round(len(s.encode()) / 1e6, 2), 'MB')
