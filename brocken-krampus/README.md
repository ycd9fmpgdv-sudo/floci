# Die Zwei vom Brocken

Eine atmosphärische Einzelseite über eine erfundene Harzer Sage.

- `index.html` ist die Seite. Die gemalten Szenen liegen als fertige Bilder in `img/`,
  damit die Seite auch auf Handys schnell und sparsam läuft.
- `tools/studio.html` enthält den Maler, der die Kreatur und alle Szenen auf Canvas zeichnet.
  `tools/render-images.js` erzeugt daraus `img/*.webp` und `img/meta.json`
  (Playwright mit Chromium nötig: `node tools/render-images.js`).
  Nach einer Änderung an `meta.json` muss der `META`-Block in `index.html` angepasst werden.
- Der 3D-Berg und die 3D-Gurke laden three.js r128 von cdnjs und jsDelivr, auf Handys erst nach Antippen.

Lokal ansehen: `python3 -m http.server` in diesem Ordner, dann http://localhost:8000 öffnen.

## Als eine Datei verschicken (z. B. WhatsApp)

`python3 tools/build-single.py Die-Zwei-vom-Brocken.html --standalone VENDOR` baut eine einzige HTML-Datei
ohne jede Internetverbindung: Bilder, Schriften (@fontsource, OFL) und three.js r128 (MIT) stecken darin.
`VENDOR` enthält `three.min.js`, `OrbitControls.js` (aus `npm pack three@0.128.0`) und `fonts/*.woff2`
(latin-Dateien aus `npm pack @fontsource/pirata-one @fontsource/im-fell-english @fontsource/im-fell-english-sc @fontsource/special-elite @fontsource/source-sans-3`).
