import glob
import os

try:
    from cairosvg import svg2png
except Exception as e:
    raise RuntimeError("Missing cairosvg. Please install with: pip install cairosvg")

SVG_DIR = os.path.join(os.path.dirname(__file__), '..', 'diagrams')
SVG_DIR = os.path.abspath(SVG_DIR)

if not os.path.isdir(SVG_DIR):
    raise SystemExit(f"Directory not found: {SVG_DIR}")

svgs = sorted(glob.glob(os.path.join(SVG_DIR, '*.svg')))
if not svgs:
    print('No SVG files found in', SVG_DIR)
    raise SystemExit(0)

for svg in svgs:
    png = os.path.splitext(svg)[0] + '.png'
    try:
        svg2png(url=svg, write_to=png)
        print('WROTE', png)
    except Exception as e:
        print('FAILED', svg, '->', e)

print('Done converting', len(svgs), 'files')
