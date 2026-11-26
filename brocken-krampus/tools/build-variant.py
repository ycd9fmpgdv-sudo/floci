"""Builds variants/modern.html from index.html plus variants/modern.css.
Usage: python3 tools/build-variant.py [ARTIFACT_COPY.html]
The optional second file gets the same page with image paths next to it (for publishing)."""
import os, re, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(root, 'index.html'), encoding='utf-8').read()
fonts = re.search(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2[^"]*"[^>]*>', s).group(0)
s = s.replace(fonts, '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&family=Geist+Mono:wght@400;500&family=Instrument+Serif:ital@0;1&display=swap">')
s = s.replace('<title>Die Zwei vom Brocken</title>', '<title>Die Zwei vom Brocken Modern</title>')
s = s.replace('<meta name="theme-color" content="#060607">', '<meta name="theme-color" content="#e2e2dd">')
s = s.replace('</style>', open(os.path.join(root, 'variants', 'modern.css'), encoding='utf-8').read() + '</style>', 1)
s = re.sub(r'.*<link rel="(manifest|icon|apple-touch-icon)".*\n', '', s)
repo = s.replace('src="img/', 'src="../img/').replace('srcset="img/', 'srcset="../img/').replace('url(img/', 'url(../img/').replace("'img/", "'../img/")
open(os.path.join(root, 'variants', 'modern.html'), 'w', encoding='utf-8').write(repo)
if len(sys.argv) > 1:
    open(sys.argv[1], 'w', encoding='utf-8').write('\n'.join(l for l in s.split('\n') if '<!--repo-only-->' not in l))
print('ok')
