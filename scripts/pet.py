#!/usr/bin/env python3
"""Minimal local web-pet authoring helper. No artwork generation or approval."""
import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def positive(v):
    return type(v) is int and 0 < v <= 9007199254740991


def safe_file(root, value):
    require(isinstance(value, str) and value and '\\' not in value, 'invalid path')
    rel = Path(value)
    require(not rel.is_absolute() and '..' not in rel.parts, 'path must stay inside project')
    target = (root / rel).resolve()
    require(target.is_relative_to(root.resolve()) and target.is_file(), f'missing or unsafe file: {value}')
    return target


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r'[a-z0-9][a-z0-9-]*', value), 'invalid ID')


def anchor(value, width, height):
    require(isinstance(value, dict), 'anchor required')
    for key, limit in [('x', width), ('y', height)]:
        v = value.get(key)
        require(type(v) in (int, float) and 0 <= v <= limit, 'anchor outside canvas')


def approved(record, version):
    a = record.get('approval', {})
    require(a.get('decision') == 'approved' and a.get('revision') == version and
            a.get('approved_at') and a.get('evidence_ref'), 'explicit approval for this revision required')
    require(a.get('payload_sha256') == payload_hash(record), 'approved content changed; review this revision again')


def payload_hash(record):
    return digest(json.dumps({k: v for k, v in record.items() if k != 'approval'}, sort_keys=True, ensure_ascii=False).encode())


def topology(body):
    parts = body.get('parts', [])
    require(parts and all(isinstance(p, dict) for p in parts), 'body parts required')
    ids = [p.get('id') for p in parts]
    for i in ids:
        identifier(i)
    require(len(set(ids)) == len(ids), 'duplicate body part')
    parents = {p['id']: p.get('parent') for p in parts}
    for start in ids:
        seen = set()
        current = start
        while current is not None:
            require(current in parents and current not in seen, 'invalid or cyclic body topology')
            seen.add(current)
            current = parents[current]


def validate(root):
    from PIL import Image
    root = root.resolve()
    project = read(root / 'project.json')
    require(project.get('schema_version') == '0.1', 'unsupported schema_version')
    identifier(project.get('pet_id'))
    h = project['host']
    require(positive(h['width']) and positive(h['height']), 'invalid host dimensions')
    anchor(h['anchor'], h['width'], h['height'])
    require(isinstance(project.get('ariaLabel'), str) and project['ariaLabel'].strip(), 'ariaLabel required')
    brief = read(root / 'character/PET_BRIEF.json')
    bible = read(root / 'character/CHARACTER_BIBLE.json')
    lock = read(root / 'character/CHARACTER_LOCK.json')
    require(positive(brief['revision']) and positive(lock['version']), 'invalid character revision')
    approved(brief, brief['revision'])
    approved(lock, lock['version'])
    require(brief['input_mode'] in ['idea', 'existing_image', 'real_pet'], 'invalid input mode')
    for key in ['character_type', 'use_case', 'style', 'must_keep']:
        require(brief.get(key), f'brief missing {key}')
    for key in ['identity', 'visual_identity', 'web_readability', 'body_topology']:
        require(bible.get(key), f'bible missing {key}')
    topology(lock['body_topology'])
    require(lock.get('bible_sha256') == payload_hash(bible), 'Bible changed or not bound to approved lock')
    require(lock['body_topology'] == bible['body_topology'], 'Bible and lock topology differ')
    require(lock.get('must_keep') and lock.get('orientation_rules'), 'identity invariants required')
    canonical = safe_file(root, lock['canonical']['path'])
    require(digest(canonical.read_bytes()) == lock['canonical']['sha256'], 'canonical hash differs')
    with Image.open(canonical) as im:
        im.verify()
    clips = {}
    hashes = {}
    for path in sorted((root / 'actions').glob('*/clip.json')):
        c = read(path)
        cid = c['id']
        identifier(cid)
        require(cid not in clips and path.parent.name == cid, 'duplicate or mismatched clip ID')
        require(c['lock_version'] == lock['version'], 'clip uses a different lock version')
        w, height = c['width'], c['height']
        require(positive(w) and positive(height) and w >= 3 and height >= 3, 'invalid frame dimensions')
        anchor(c['anchor'], w, height)
        frames = {}
        for f in c['frames']:
            identifier(f['id'])
            require(f['id'] not in frames, 'duplicate frame ID')
            source = safe_file(root, f['path'])
            with Image.open(source) as im:
                require(im.format == 'PNG' and im.mode == 'RGBA' and im.size == (w, height), 'expected matching RGBA PNG')
                a = im.getchannel('A')
                lo, hi = a.getextrema()
                box = a.getbbox()
                require(lo == 0 and hi > 0 and box is not None, 'frame needs transparent and visible pixels')
                require(box[0] >= 1 and box[1] >= 1 and box[2] <= w-1 and box[3] <= height-1, 'frame touches canvas border')
            hashes[f['path']] = digest(source.read_bytes())
            frames[f['id']] = f['path']
        sequence, times = c['sequence'], c['durationsMs']
        require(sequence and len(sequence) == len(times) and all(positive(t) for t in times), 'invalid timing')
        require(all(i in frames for i in sequence), 'sequence references missing frame')
        require(c['reduced_motion_frame'] in frames, 'missing reduced motion fallback')
        clips[cid] = {**c, 'frames': frames}
    require(clips, 'no clips found')
    actions = project['actions']
    require(actions and project['default_action'] in actions, 'default action missing')
    for aid, family in actions.items():
        identifier(aid)
        require(set(family) in ({'single'}, {'enter', 'loop', 'exit'}), 'action must be single or enter/loop/exit')
        require(all(cid in clips for cid in family.values()), 'action references missing clip')
    require('single' in actions[project['default_action']], 'default action must be single')
    sources = {'project': project, 'brief': brief, 'bible': bible, 'lock': lock, 'clips': clips, 'frameHashes': hashes}
    for p in sorted((SKILL / 'assets/web').glob('*')):
        if p.is_file():
            sources['web/' + p.name] = digest(p.read_bytes())
    build_id = digest(json.dumps(sources, sort_keys=True, ensure_ascii=False).encode())
    report = {'technical_pass': True, 'build_id': build_id, 'clips': len(clips),
              'playback_entries': sum(len(c['sequence']) for c in clips.values()),
              'unique_source_files': len(set(hashes.values())),
              'note': 'Technical checks do not establish visual quality or user acceptance.'}
    return project, clips, hashes, report


def build(root):
    project, clips, hashes, report = validate(root)
    dest = root / 'preview' / report['build_id']
    if dest.exists():
        stored = read(dest / 'checksums.json')
        require(all(digest(safe_file(dest, n).read_bytes()) == sha for n, sha in stored.items()), 'existing preview modified; preserve and use a new source revision')
        return {**report, 'preview': str(dest / 'index.html'), 'reused': True}
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=dest.parent) as temporary:
        stage = Path(temporary)
        frame_paths = {}
        for path, sha in hashes.items():
            output = 'frames/' + sha + '.png'
            (stage / 'frames').mkdir(exist_ok=True)
            shutil.copy2(safe_file(root, path), stage / output)
            frame_paths[path] = output
        runtime = {k: project[k] for k in ['schema_version', 'pet_id', 'host', 'ariaLabel', 'default_action', 'actions']}
        runtime['build_id'] = report['build_id']
        runtime['clips'] = {cid: {**{k: c[k] for k in ['width', 'height', 'anchor', 'sequence', 'durationsMs', 'reduced_motion_frame']}, 'frames': {fid: frame_paths[p] for fid, p in c['frames'].items()}} for cid, c in clips.items()}
        write(stage / 'manifest.json', runtime)
        write(stage / 'technical.json', report)
        for p in (SKILL / 'assets/web').glob('*'):
            shutil.copy2(p, stage / p.name)
        write(stage / 'checksums.json', {str(p.relative_to(stage)): digest(p.read_bytes()) for p in stage.rglob('*') if p.is_file()})
        shutil.copytree(stage, dest)
    return {**report, 'preview': str(dest / 'index.html'), 'status': 'candidate'}


def views(root):
    for p in (root / 'character').glob('*.json'):
        p.with_suffix('.md').write_text('# ' + p.stem + '\n\nReview view; edit JSON and regenerate.\n\nContent hash: ' + payload_hash(read(p)) + '\n\n```json\n' + json.dumps(read(p), ensure_ascii=False, indent=2) + '\n```\n')


def init(root):
    require(not root.exists(), 'project already exists; refusing overwrite')
    for name in ['character', 'reference', 'actions', 'assets', 'manifest', 'preview', 'QA']:
        (root / name).mkdir(parents=True)
    pending = {'decision': 'pending', 'revision': 1, 'approved_at': None, 'evidence_ref': None, 'payload_sha256': None}
    write(root / 'project.json', {'schema_version': '0.1', 'pet_id': 'my-pet', 'ariaLabel': 'My pet', 'host': {'width': 240, 'height': 320, 'anchor': {'x': 120, 'y': 304}}, 'default_action': 'idle', 'actions': {}})
    write(root / 'character/PET_BRIEF.json', {'revision': 1, 'input_mode': 'idea', 'name': '', 'character_type': '', 'use_case': '', 'style': '', 'personality': '', 'colors': [], 'proportions': '', 'signature_features': [], 'must_keep': [], 'allowed_optimization': [], 'expected_actions': [], 'field_evidence': {}, 'approval': pending})
    write(root / 'character/CHARACTER_BIBLE.json', {'identity': {}, 'visual_identity': {}, 'personality': '', 'must_never_change': [], 'flexible_elements': [], 'web_readability': {}, 'body_topology': {'parts': [], 'attachments': []}})
    write(root / 'character/CHARACTER_LOCK.json', {'version': 1, 'canonical': {'path': '', 'sha256': ''}, 'bible_sha256': None, 'body_topology': {'parts': [], 'attachments': []}, 'must_keep': [], 'allowed_variation': [], 'orientation_rules': {}, 'approval': pending})
    write(root / 'reference/index.json', {'references': []})
    write(root / 'QA/REVIEW.json', {'build_id': None, 'visual': {k: {'status': 'not_reviewed', 'evidence': ''} for k in ['identity', 'anatomy', 'contact', 'support', 'continuity', 'attachment_behavior', 'small_size_readability']}, 'user_acceptance': {'decision': 'pending', 'evidence_ref': None, 'scope': [], 'approved_at': None}})
    for p in (SKILL / 'assets/templates').glob('*.md'):
        shutil.copy2(p, root / ('actions' if p.name == 'ACTION_BRIEF.md' else 'reference') / p.name)
    views(root)
    return {'created': str(root), 'status': 'draft'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'views', 'validate', 'build'])
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    try:
        root = args.project.resolve()
        if args.command == 'init': result = init(root)
        elif args.command == 'views': views(root); result = {'views_updated': True}
        elif args.command == 'build': result = build(root)
        else: result = validate(root)[3]
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError, IndexError, ImportError) as error:
        print(json.dumps({'technical_pass': False, 'error': str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    sys.exit(main())
