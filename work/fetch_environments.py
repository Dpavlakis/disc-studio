"""Download the five CC0 photographic lighting presets from Poly Haven."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

DEST = Path(__file__).resolve().parents[1] / 'outputs' / 'lighting'
PRESETS = {
    'living-room': ('lebombo', 'Living room · Window light'),
    'office': ('unfinished_office', 'Office · Daylight'),
    'garden': ('garden_nook', 'Garden · Sunshine'),
    'forest': ('forest_slope', 'Forest · Dappled shade'),
    'sunset': ('venice_sunset', 'Waterfront · Sunset'),
}

def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'LocalDiscStudio/1.0 (personal HDRI lighting preview)'})
    return urllib.request.urlopen(request, timeout=60).read()

def download(item):
    key, (asset, label) = item
    metadata = json.loads(get('https://api.polyhaven.com/files/' + asset))
    info = metadata['hdri']['2k']['hdr']
    payload = get(info['url'])
    assert payload.startswith(b'#?RADIANCE') or payload.startswith(b'#?RGBE'), asset
    if info.get('md5'):
        assert hashlib.md5(payload).hexdigest() == info['md5'], asset
    file = key + '.hdr'
    (DEST / file).write_bytes(payload)
    print(label, len(payload), 'bytes', flush=True)
    return key, {'label': label, 'file': file, 'asset': asset, 'source': 'https://polyhaven.com/a/' + asset,
                 'download': info['url'], 'license': 'CC0', 'sha256': hashlib.sha256(payload).hexdigest()}

if __name__ == '__main__':
    DEST.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        presets = dict(pool.map(download, PRESETS.items()))
    (DEST / 'environments.json').write_text(json.dumps(presets, indent=2), encoding='utf-8')
    (DEST / 'ENVIRONMENT-CREDITS.txt').write_text(
        'Photographic HDRI environments from Poly Haven, released under CC0.\n'
        'License: https://polyhaven.com/license\nResolution: 2048 x 1024 (2K), Radiance HDR.\n\n' +
        '\n'.join(v['label'] + '\n' + v['source'] + '\n' for v in presets.values()), encoding='utf-8')
