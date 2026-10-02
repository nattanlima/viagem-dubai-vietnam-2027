"""Build a portable, self-contained presentation using only the Python standard library."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PARTS = {
    '__D3__': 'vendor/d3.min.js',
    '__DATA__': 'data/itinerary.json',
    '__MAPS__': 'data/maps.json',
    '__MEDIA__': 'data/hero.json',
    '__PHOTOS__': 'data/photos.json',
    '__ROUTES__': 'data/routes.json',
    '__MAPLIBRE__': 'vendor/maplibre-gl.js',
    '__MAPLIBRE_CSS__': 'vendor/maplibre-gl.css',
    '__UPGRADE_CSS__': 'src/styles.css',
    '__APP__': 'src/app.js',
}

def build():
    result = (ROOT / 'src/presentation.template').read_text('utf-8')
    for token, name in PARTS.items():
        if result.count(token) != 1:
            raise ValueError(f'Missing or duplicate insertion point: {token}')
        result = result.replace(token, (ROOT / name).read_text('utf-8'))
    if re.search(r'__(?:D3|DATA|MAPS|MEDIA|PHOTOS|ROUTES|MAPLIBRE|APP)__', result):
        raise ValueError('Unresolved assets')
    (ROOT / 'index.html').write_text(result, 'utf-8')
    print(f'Built index.html ({len(result.encode("utf-8")):,} bytes)')

if __name__ == '__main__':
    build()
