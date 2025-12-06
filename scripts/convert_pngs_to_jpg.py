from PIL import Image
import glob
import os

DIAGRAM_DIR = os.path.join(os.path.dirname(__file__), '..', 'diagrams')
DIAGRAM_DIR = os.path.abspath(DIAGRAM_DIR)

png_files = sorted(glob.glob(os.path.join(DIAGRAM_DIR, '*.png')))
if not png_files:
    print('No PNG files found in', DIAGRAM_DIR)
    raise SystemExit(0)

for png in png_files:
    jpg = os.path.splitext(png)[0] + '.jpg'
    try:
        with Image.open(png) as im:
            # Convert RGBA (transparent) to white background for JPG
            if im.mode in ('RGBA', 'LA'):
                bg = Image.new('RGB', im.size, (255,255,255))
                bg.paste(im, mask=im.split()[3])
                bg.save(jpg, quality=95)
            else:
                rgb = im.convert('RGB')
                rgb.save(jpg, quality=95)
        print('WROTE', jpg)
    except Exception as e:
        print('FAILED', png, '->', e)

print('Done converting', len(png_files), 'files')
