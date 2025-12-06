import asyncio
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

DIAGRAM_DIR = Path(__file__).parent.parent / 'diagrams'

async def render_svg_to_png(svg_path: Path, png_path: Path):
    """Render SVG to PNG using Playwright Chromium."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1200, 'height': 800})
        await page.goto(f'file://{svg_path.absolute()}')
        await page.screenshot(path=str(png_path), full_page=False)
        await browser.close()
        print(f'WROTE PNG: {png_path}')

async def convert_svg_to_png_and_jpg():
    """Convert all SVGs to PNG and JPG."""
    svg_files = sorted(DIAGRAM_DIR.glob('*.svg'))
    if not svg_files:
        print('No SVG files found')
        return
    
    for svg in svg_files:
        png = svg.with_suffix('.png')
        try:
            await render_svg_to_png(svg, png)
        except Exception as e:
            print(f'FAILED SVG->PNG {svg}: {e}')
    
    # Now convert PNGs to JPGs
    png_files = sorted(DIAGRAM_DIR.glob('*.png'))
    for png in png_files:
        jpg = png.with_suffix('.jpg')
        try:
            with Image.open(png) as im:
                # Convert RGBA to white background for JPG
                if im.mode in ('RGBA', 'LA', 'P'):
                    im = im.convert('RGB')
                im.save(jpg, 'JPEG', quality=95)
            print(f'WROTE JPG: {jpg}')
        except Exception as e:
            print(f'FAILED PNG->JPG {png}: {e}')

asyncio.run(convert_svg_to_png_and_jpg())
print('Done!')
