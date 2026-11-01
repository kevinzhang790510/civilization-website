import copy, hashlib, json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from export_approved import export, FORMAL_DIR
from build import validate, ROOT

class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.path=self.root/FORMAL_DIR/'第001章.md'; self.path.parent.mkdir(parents=True)
        self.text='---\nstatus: 定稿\nauthorApproved: true\n---\n# 验证标题\n\n验证段落。\n'
        self.path.write_text(self.text,encoding='utf-8')
        self.entry=dict(id='book1-ch001',volume=1,order=1,title='验证标题',path=FORMAL_DIR+'/第001章.md',status='已发布',authorApproved=True,sha256=hashlib.sha256(self.path.read_bytes()).hexdigest())
        (self.root/'publication').mkdir()
    def tearDown(self): self.tmp.cleanup()
    def run_export(self,entries=None):
        (self.root/'publication/chapters.json').write_text(json.dumps(dict(schemaVersion=1,chapters=[self.entry] if entries is None else entries)),encoding='utf-8')
        return export(self.root)
    def test_empty(self): self.assertEqual(self.run_export([])['chapters'],[])
    def test_approved(self):
        data=self.run_export(); validate(data)
        self.assertEqual(data['chapters'][0]['paragraphs'],['验证段落。'])
        self.assertNotIn('path',data['chapters'][0]); self.assertNotIn('sha256',data['chapters'][0])
    def test_modified_body(self):
        self.path.write_text(self.text+'\n更改。',encoding='utf-8')
        with self.assertRaises(ValueError): self.run_export()
    def test_unlisted(self):
        (self.path.parent/'第002章.md').write_text('DO_NOT_PUBLISH',encoding='utf-8')
        self.assertNotIn('DO_NOT_PUBLISH',json.dumps(self.run_export()))
    def test_unapproved(self):
        for key,value in [('authorApproved',False),('status','草稿')]:
            old=self.entry[key]; self.entry[key]=value
            with self.assertRaises(ValueError): self.run_export()
            self.entry[key]=old
    def test_independent_file_markers(self):
        for body in [self.text.replace('status: 定稿','status: 草稿'),self.text.replace('authorApproved: true','authorApproved: false')]:
            self.path.write_text(body,encoding='utf-8'); self.entry['sha256']=hashlib.sha256(self.path.read_bytes()).hexdigest()
            with self.assertRaises(ValueError): self.run_export()
    def test_forbidden_paths(self):
        for path in ['03_人物档案/第001章.md','10_第一部_石之永恒/文风测试/第001章.md',FORMAL_DIR+'/../第001章.md','/tmp/第001章.md',FORMAL_DIR+'/草稿/第001章.md']:
            self.entry['path']=path
            with self.assertRaises(ValueError): self.run_export()
    def test_symlinks(self):
        self.path.unlink(); target=self.root/'secret.md'; target.write_text(self.text,encoding='utf-8'); self.path.symlink_to(target)
        with self.assertRaises(ValueError): self.run_export()
    def test_duplicates(self):
        with self.assertRaises(ValueError): self.run_export([self.entry,copy.deepcopy(self.entry)])
    def test_private_metadata(self):
        self.entry['internalNote']='DO_NOT_PUBLISH'
        with self.assertRaises(ValueError): self.run_export()
    def test_markup(self):
        for markup in ['![photo](../private.png)','<!-- internal -->','# Internal heading']:
            self.path.write_text(self.text+'\n'+markup,encoding='utf-8'); self.entry['sha256']=hashlib.sha256(self.path.read_bytes()).hexdigest()
            with self.assertRaises(ValueError): self.run_export()
    def test_public_payload(self):
        data=self.run_export(); data['chapters'][0]['path']='private'
        with self.assertRaises(ValueError): validate(data)
        del data['chapters'][0]['path']; data['chapters'][0]['status']='草稿'
        with self.assertRaises(ValueError): validate(data)
    def test_template_matches(self):
        self.assertEqual((ROOT/'scripts/export_approved.py').read_bytes(),(ROOT/'private-repository-setup/publication/export_approved.py').read_bytes())

if __name__=='__main__': unittest.main()
