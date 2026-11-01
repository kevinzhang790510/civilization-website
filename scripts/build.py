"""Build exclusively from public web assets and approved publication payload."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition):
    if not condition:
        raise ValueError('Invalid public publication payload')


def validate(payload):
    require(isinstance(payload, dict) and set(payload) == {'schemaVersion', 'chapters'})
    require(payload['schemaVersion'] == 1 and isinstance(payload['chapters'], list))
    ids, orders = set(), set()
    for c in payload['chapters']:
        require(set(c) == {'id', 'volume', 'order', 'title', 'status', 'paragraphs'})
        require(isinstance(c['id'], str) and re.fullmatch(r'book1-ch[0-9]{3,}', c['id']))
        require(c['volume'] == 1 and c['status'] == '已发布')
        require(type(c['order']) is int and c['order'] > 0)
        require(c['id'] not in ids and c['order'] not in orders)
        ids.add(c['id']); orders.add(c['order'])
        require(isinstance(c['title'], str) and 0 < len(c['title'].strip()) <= 100)
        require(isinstance(c['paragraphs'], list) and c['paragraphs'])
        require(all(isinstance(p, str) and p.strip() for p in c['paragraphs']))
    return sorted(payload['chapters'], key=lambda c: c['order'])


def build():
    chapters = validate(json.loads((ROOT / 'published/chapters.json').read_text('utf-8')))
    out = ROOT / 'dist'
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    # Explicit allowlist: no recursive copy of repository, docs, tests, or private inputs.
    for name in ('index.html', 'style.css', 'app.js'):
        src = ROOT / 'web' / name
        require(src.is_file() and not src.is_symlink())
        shutil.copyfile(src, out / name)
    content = json.dumps(chapters, ensure_ascii=False).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    (out / 'content.js').write_text('const CHAPTERS = ' + content + ';\n', encoding='utf-8')
    (out / '.nojekyll').touch()
    print('Built standalone website in dist/.')

if __name__ == '__main__':
    build()
