"""Run ONLY inside the private repository's trusted CI. No network, no Markdown execution."""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

FORMAL_DIR = '10_第一部_石之永恒/正文'
MANIFEST = 'publication/chapters.json'


def fail():
    # Never print private paths, titles, or manuscript text to CI logs.
    raise ValueError('Publication validation failed; inspect the private approval checklist.')


def regular(root, relative):
    p = PurePosixPath(relative)
    if p.is_absolute() or '..' in p.parts or '\\' in relative:
        fail()
    target = root.joinpath(*p.parts)
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink():
            fail()
    if not target.is_file() or not target.resolve().is_relative_to(root.resolve()):
        fail()
    return target


def export(root):
    root = Path(root).resolve()
    manifest = json.loads(regular(root, MANIFEST).read_text('utf-8'))
    if set(manifest) != {'schemaVersion', 'chapters'} or manifest['schemaVersion'] != 1 or not isinstance(manifest['chapters'], list):
        fail()
    result, seen_ids, seen_orders, seen_paths = [], set(), set(), set()
    for entry in manifest['chapters']:
        keys = {'id', 'volume', 'order', 'title', 'path', 'status', 'authorApproved', 'sha256'}
        if not isinstance(entry, dict) or set(entry) != keys:
            fail()
        if entry['volume'] != 1 or type(entry['order']) is not int or entry['order'] < 1:
            fail()
        if entry['status'] != '已发布' or entry['authorApproved'] is not True:
            fail()
        if not isinstance(entry['id'], str) or not re.fullmatch(r'book1-ch[0-9]{3,}', entry['id']):
            fail()
        if not isinstance(entry['title'], str) or not entry['title'].strip() or len(entry['title']) > 100:
            fail()
        if not isinstance(entry['path'], str) or not re.fullmatch(re.escape(FORMAL_DIR) + r'/第[0-9]{3,}章\.md', entry['path']):
            fail()
        if entry['id'] in seen_ids or entry['order'] in seen_orders or entry['path'] in seen_paths:
            fail()
        seen_ids.add(entry['id']); seen_orders.add(entry['order']); seen_paths.add(entry['path'])
        data = regular(root, entry['path']).read_bytes()
        if len(data) > 2_000_000 or hashlib.sha256(data).hexdigest() != entry['sha256']:
            fail()
        # Fixed metadata envelope: not executable YAML or Markdown/HTML.
        text = data.decode('utf-8').replace('\r\n', '\n')
        prefix = '---\nstatus: 定稿\nauthorApproved: true\n---\n'
        if not text.startswith(prefix):
            fail()
        body = text[len(prefix):].strip()
        # Require title to match; title and metadata never become prose paragraphs.
        heading, sep, body = body.partition('\n')
        if heading != '# ' + entry['title'] or not sep or not body.strip():
            fail()
        # Initial format is plain paragraphs only. Disallow headings, HTML, links,
        # images, fences, comments, and metadata in the body; no embedded private assets.
        if re.search(r'<|>|```|!\[|\]\(|^\s*#|^---\s*$', body, re.M):
            fail()
        paragraphs = [s.strip() for s in re.split(r'\n\s*\n', body.strip()) if s.strip()]
        result.append({'id': entry['id'], 'volume': 1, 'order': entry['order'],
                       'title': entry['title'], 'status': '已发布', 'paragraphs': paragraphs})
    result.sort(key=lambda c: c['order'])
    return {'schemaVersion': 1, 'chapters': result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--private-root', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        result = export(args.private_root)
    except Exception:
        raise SystemExit('Publication validation failed; no output written. Inspect private approvals.') from None
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Validated publication payload generated.')

if __name__ == '__main__':
    main()
