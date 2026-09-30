import importlib.util
import tempfile
import unittest
from pathlib import Path
from PIL import Image

spec = importlib.util.spec_from_file_location('pet', Path(__file__).resolve().parents[1] / 'scripts/pet.py')
pet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pet)


def fixture(root):
    pet.init(root)
    body = {'parts': [{'id': 'core', 'parent': None}], 'attachments': []}
    image = Image.new('RGBA', (24, 32))
    for x in range(8, 16):
        for y in range(8, 25): image.putpixel((x, y), (60, 140, 230, 255))
    image.save(root / 'reference/canonical.png')
    approval = {'decision': 'approved', 'revision': 1, 'approved_at': 'test-only', 'evidence_ref': 'synthetic-fixture-not-user-acceptance'}
    brief = pet.read(root / 'character/PET_BRIEF.json')
    brief.update(character_type='synthetic', use_case='tests', style='geometry', must_keep=['rectangle'], approval=approval)
    pet.write(root / 'character/PET_BRIEF.json', brief)
    pet.write(root / 'character/CHARACTER_BIBLE.json', {'identity': {'type': 'fixture'}, 'visual_identity': {'color': 'blue'}, 'web_readability': {'signature': 'rectangle'}, 'body_topology': body})
    pet.write(root / 'character/CHARACTER_LOCK.json', {'version': 1, 'canonical': {'path': 'reference/canonical.png', 'sha256': pet.digest((root / 'reference/canonical.png').read_bytes())}, 'bible_sha256': pet.payload_hash(pet.read(root / 'character/CHARACTER_BIBLE.json')), 'body_topology': body, 'must_keep': ['rectangle'], 'orientation_rules': {'mirror': False}, 'approval': approval})
    for name in ['PET_BRIEF', 'CHARACTER_LOCK']:
        p = root / 'character' / (name + '.json')
        data = pet.read(p); data['approval']['payload_sha256'] = pet.payload_hash(data); pet.write(p, data)
    for cid in ['idle', 'rest-enter', 'rest-loop', 'rest-exit']:
        folder = root / 'actions' / cid
        folder.mkdir()
        image.save(folder / '000.png')
        pet.write(folder / 'clip.json', {'id': cid, 'lock_version': 1, 'width': 24, 'height': 32, 'anchor': {'x': 12, 'y': 28}, 'frames': [{'id': 'f0', 'path': f'actions/{cid}/000.png'}], 'sequence': ['f0', 'f0'], 'durationsMs': [100, 200], 'reduced_motion_frame': 'f0'})
    project = pet.read(root / 'project.json')
    project['host'] = {'width': 24, 'height': 32, 'anchor': {'x': 12, 'y': 28}}
    project['actions'] = {'idle': {'single': 'idle'}, 'rest': {'enter': 'rest-enter', 'loop': 'rest-loop', 'exit': 'rest-exit'}}
    pet.write(root / 'project.json', project)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'pet'
        fixture(self.root)
    def tearDown(self): self.temp.cleanup()
    def mutate(self, change):
        p = self.root / 'actions/idle/clip.json'
        data = pet.read(p); change(data); pet.write(p, data)
    def test_build_repeats_and_immutability(self):
        result = pet.build(self.root)
        self.assertTrue(result['technical_pass'])
        self.assertEqual(result['playback_entries'], 8)
        self.assertTrue(pet.build(self.root)['reused'])
        self.mutate(lambda c: c['durationsMs'].__setitem__(0, 110))
        self.assertNotEqual(result['build_id'], pet.build(self.root)['build_id'])
    def test_missing_frame(self):
        self.mutate(lambda c: c['sequence'].append('absent'))
        self.mutate(lambda c: c['durationsMs'].append(10))
        with self.assertRaisesRegex(ValueError, 'missing frame'): pet.validate(self.root)
    def test_bad_durations(self):
        for v in [0, -1, float('nan'), float('inf'), True]:
            self.mutate(lambda c: c['durationsMs'].__setitem__(0, v))
            with self.assertRaises(ValueError): pet.validate(self.root)
    def test_bad_dimensions(self):
        self.mutate(lambda c: c.update(width=1))
        with self.assertRaisesRegex(ValueError, 'dimensions'): pet.validate(self.root)
    def test_unsafe_path(self):
        self.mutate(lambda c: c['frames'][0].update(path='../outside.png'))
        with self.assertRaisesRegex(ValueError, 'inside project'): pet.validate(self.root)
    def test_pending_lock(self):
        p = self.root / 'character/CHARACTER_LOCK.json'
        c = pet.read(p); c['approval']['decision'] = 'pending'; pet.write(p,c)
        with self.assertRaisesRegex(ValueError, 'approval'): pet.validate(self.root)
    def test_changed_canonical(self):
        (self.root / 'reference/canonical.png').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'hash'): pet.validate(self.root)
    def test_changed_approved_text(self):
        p = self.root / 'character/CHARACTER_LOCK.json'
        data = pet.read(p); data['must_keep'].append('different'); pet.write(p, data)
        with self.assertRaisesRegex(ValueError, 'content changed'): pet.validate(self.root)
    def test_modified_build_rejected(self):
        result = pet.build(self.root)
        Path(result['preview']).write_text('edited')
        with self.assertRaisesRegex(ValueError, 'modified'): pet.build(self.root)
    def test_cycle(self):
        with self.assertRaisesRegex(ValueError, 'cyclic'):
            pet.topology({'parts':[{'id':'a','parent':'b'},{'id':'b','parent':'a'}]})
    def test_alpha_failure(self):
        Image.new('RGBA',(24,32),(0,0,0,255)).save(self.root/'actions/idle/000.png')
        with self.assertRaisesRegex(ValueError,'transparent'):pet.validate(self.root)
    def test_changed_bible(self):
        p=self.root/'character/CHARACTER_BIBLE.json'
        data=pet.read(p);data['visual_identity']={'color':'red'};pet.write(p,data)
        with self.assertRaisesRegex(ValueError,'Bible changed'):pet.validate(self.root)
    def test_runtime_does_not_leak_extra_fields(self):
        self.mutate(lambda c:c.update(private_notes='not-for-runtime'))
        result=pet.build(self.root)
        manifest=pet.read(Path(result['preview']).parent/'manifest.json')
        self.assertNotIn('private_notes',manifest['clips']['idle'])
    def test_symlink_escape(self):
        external=Path(self.temp.name)/'outside.png'
        external.write_bytes((self.root/'actions/idle/000.png').read_bytes())
        (self.root/'actions/idle/link.png').symlink_to(external)
        self.mutate(lambda c:c['frames'][0].update(path='actions/idle/link.png'))
        with self.assertRaisesRegex(ValueError,'unsafe'):pet.validate(self.root)
    def test_mixed_clip_dimensions(self):
        p=self.root/'actions/rest-enter/clip.json';c=pet.read(p)
        c.update(width=30,anchor={'x':15,'y':28});pet.write(p,c)
        image=Image.new('RGBA',(30,32));image.paste(Image.open(self.root/'actions/idle/000.png'),(3,0));image.save(self.root/'actions/rest-enter/000.png')
        self.assertTrue(pet.build(self.root)['technical_pass'])

if __name__ == '__main__': unittest.main()
