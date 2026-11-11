import sys,unittest,tempfile,json,gzip,sqlite3
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import clean,load,digest,DAG,request
from unittest.mock import patch
import urllib.error
class PipelineTests(unittest.TestCase):
    def row(self):return dict(id='123',date='2024-02-29T23:30:00',primary_type='THEFT',arrest=False,domestic=True,community_area='0',latitude='0',longitude='0')
    def test_leap_day_and_nulls(self):
        r=clean(self.row()); self.assertEqual(r[10:],[2024,2,3,23,'Winter'] if isinstance(r[10:],list) else (2024,2,3,23,'Winter'));self.assertIsNone(r[6]);self.assertIsNone(r[7])
    def test_booleans_fail_closed(self):
        r=self.row();r['arrest']='false'
        with self.assertRaises(ValueError):clean(r)
    def test_idempotent_replay_and_checksum(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);f=p/'page.json.gz'
            with gzip.open(f,'wt') as h:json.dump([self.row()],h)
            (p/'manifest.json').write_text(json.dumps({'pages':[{'file':f.name,'sha256':digest(f)}]}))
            db=p/'db.sqlite';cfg={'start':'2020-01-01','end':'2026-11-01'}
            load(p,db,cfg);load(p,db,cfg)
            with sqlite3.connect(db) as c:self.assertEqual(c.execute('select count(*) from crimes').fetchone()[0],1)
            f.write_bytes(b'corrupt')
            with self.assertRaises(ValueError):load(p,db,cfg)
            with sqlite3.connect(db) as c:self.assertEqual(c.execute('select count(*) from crimes').fetchone()[0],1)
    def test_transient_retry_and_permanent_failure(self):
        with patch('pipeline.urllib.request.urlopen', side_effect=urllib.error.HTTPError('url',429,'rate limit',{},None)) as call, patch('pipeline.time.sleep'):
            with self.assertRaises(urllib.error.HTTPError):request('https://example.com')
            self.assertEqual(call.call_count,6)
        with patch('pipeline.urllib.request.urlopen', side_effect=urllib.error.HTTPError('url',400,'bad query',{},None)) as call:
            with self.assertRaises(urllib.error.HTTPError):request('https://example.com')
            self.assertEqual(call.call_count,1)
    def test_dag_order(self):
        seen=set()
        for task,deps in DAG.items():self.assertTrue(set(deps)<=seen);seen.add(task)
if __name__=='__main__':unittest.main()
