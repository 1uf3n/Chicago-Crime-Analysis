"""Chicago crime ETL. Python standard library only. Run from repository root."""
import argparse, calendar, csv, datetime as dt, gzip, hashlib, json, os
from pathlib import Path
import sqlite3, time, urllib.error, urllib.parse, urllib.request, uuid
ROOT = Path(__file__).resolve().parents[1]
FIELDS = 'id,date,primary_type,description,arrest,domestic,community_area,latitude,longitude,updated_on'
DAG = {'extract': [], 'transform_load': ['extract'], 'validate': ['transform_load'], 'analyze': ['validate'], 'visualize': ['analyze']}

def request(url, params=None):
    url += ('?' + urllib.parse.urlencode(params)) if params else ''
    headers = {'User-Agent':'ChicagoCrimeClassProject/1.0'}
    if os.getenv('SOCRATA_APP_TOKEN'): headers['X-App-Token'] = os.environ['SOCRATA_APP_TOKEN']
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=180) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError) as e:
            if isinstance(e, urllib.error.HTTPError) and e.code not in (429,500,502,503,504): raise
            if attempt == 5: raise
            time.sleep(min(60,2**attempt))

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2))
def extract(cfg, raw):
    raw.mkdir(parents=True,exist_ok=False)
    where = f"date >= '{cfg['start']}T00:00:00' AND date < '{cfg['end']}T00:00:00'"
    meta = request(cfg['endpoint'], {'$select':'count(*) as n,max(id) as max_id,max(date) as latest','$where':where})[0]
    high = int(meta['max_id']); last = 0; pages = []; total = 0
    while True:
        params={'$select':FIELDS,'$where':where+f' AND id > {last} AND id <= {high}', '$order':'id ASC','$limit':cfg['page_size']}
        rows=request(cfg['endpoint'],params)
        if not rows: break
        ids=[int(r['id']) for r in rows]
        if ids != sorted(set(ids)) or ids[0] <= last: raise ValueError('Unstable keyset pagination')
        p=raw/f'page-{len(pages):04}.json.gz'
        with gzip.open(p,'wt',encoding='utf-8') as f: json.dump(rows,f,separators=(',',':'))
        pages.append({'file':p.name,'rows':len(rows),'sha256':digest(p),'query':params})
        total += len(rows); last=ids[-1]; print(f'Extracted {total:,}',flush=True)
    if total != int(meta['n']): raise ValueError('API count changed during extraction. Rerun with a new snapshot.')
    boundaries=request(cfg['boundaries'],{'$limit':100})
    if len(boundaries)!=77 or {int(r['area_num_1']) for r in boundaries} != set(range(1,78)) or any('the_geom' not in r for r in boundaries): raise ValueError('Invalid community boundaries')
    dump(raw/'boundaries.json',boundaries)
    manifest={'config':cfg,'retrieved_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'count':total,'source_check':meta,'pages':pages,'boundary_sha256':digest(raw/'boundaries.json'),'consistency_note':'Keyset and count checks do not provide transactional isolation. Source records may be revised during extraction.'}
    dump(raw/'manifest.json',manifest)
    return manifest

def clean(r):
    i=int(r['id']); date=dt.datetime.fromisoformat(r['date']); typ=r['primary_type'].strip()
    if not typ or i<=0: raise ValueError('Missing category or invalid ID')
    for flag in ('arrest','domestic'):
        if not isinstance(r.get(flag),bool): raise ValueError('Missing/invalid boolean: '+flag)
    area=int(r['community_area']) if r.get('community_area') else None
    if area not in range(1,78): area=None
    lat=float(r['latitude']) if r.get('latitude') else None
    lon=float(r['longitude']) if r.get('longitude') else None
    if lat is None or lon is None or not (41.5<=lat<=42.1 and -88<=lon<=-87.4): lat=lon=None
    season=('Winter','Spring','Summer','Autumn')[(date.month%12)//3]
    return (i,date.isoformat(),typ,r.get('description'),int(r['arrest']),int(r['domestic']),area,lat,lon,r.get('updated_on'),date.year,date.month,date.weekday(),date.hour,season)

def load(raw,db,cfg):
    manifest=json.loads((raw/'manifest.json').read_text())
    if 'config' in manifest and manifest['config'] != cfg: raise ValueError('Replay configuration must match snapshot manifest')
    if 'boundary_sha256' in manifest and digest(raw/'boundaries.json') != manifest['boundary_sha256']: raise ValueError('Boundary checksum mismatch')
    stage=db.with_suffix('.building.sqlite'); stage.unlink(missing_ok=True)
    con=sqlite3.connect(stage)
    con.executescript('''CREATE TABLE crimes(id INTEGER PRIMARY KEY,date TEXT NOT NULL,primary_type TEXT NOT NULL,description TEXT,arrest INTEGER NOT NULL CHECK(arrest IN(0,1)),domestic INTEGER NOT NULL CHECK(domestic IN(0,1)),community_area INTEGER,latitude REAL,longitude REAL,updated_on TEXT,year INTEGER,month INTEGER,weekday INTEGER,hour INTEGER,season TEXT); CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);''')
    for page in manifest['pages']:
        p=raw/page['file']
        if digest(p)!=page['sha256']: raise ValueError('Snapshot checksum mismatch')
        with gzip.open(p,'rt') as f: rows=json.load(f)
        values=[clean(r) for r in rows]
        if any(not cfg['start']<=r[1][:10]<cfg['end'] for r in values): raise ValueError('Date outside scope')
        con.executemany('INSERT INTO crimes VALUES('+','.join(['?']*15)+')',values)
    con.execute('INSERT INTO metadata VALUES(?,?)',('manifest',json.dumps(manifest)))
    con.executescript('CREATE INDEX idx_date ON crimes(date); CREATE INDEX idx_category ON crimes(primary_type); CREATE INDEX idx_area ON crimes(community_area);')
    con.commit(); con.close(); os.replace(stage,db)

def validate(db,manifest):
    with sqlite3.connect(db) as c:
        n=c.execute('SELECT count(*) FROM crimes').fetchone()[0]
        assert n==manifest['count'], 'Row reconciliation failed'
        assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        quality=dict(zip(['rows','unknown_area','missing_coordinates'],c.execute('SELECT count(*),sum(community_area IS NULL),sum(latitude IS NULL) FROM crimes').fetchone()))
    dump(ROOT/'reports/quality.json',quality); return quality

def analyze(db,cfg):
    # A fixed exclusive end on month day 01 makes equal Jan..previous-month windows.
    end=dt.date.fromisoformat(cfg['end'])
    if end.day != 1: raise ValueError('Use an exclusive first-of-month cutoff')
    last_year=end.year if end.month>1 else end.year-1
    months=end.month-1 if end.month>1 else 12
    common=f'month <= {months}'
    queries={
      'annual':f'SELECT year,count(*) incidents,sum(arrest) arrests FROM crimes WHERE {common} GROUP BY year ORDER BY year',
      'category_year':f'SELECT year,primary_type,count(*) incidents,sum(arrest) arrests FROM crimes WHERE {common} GROUP BY year,primary_type ORDER BY year,primary_type',
      'monthly':'SELECT year,month,count(*) incidents FROM crimes GROUP BY year,month ORDER BY year,month',
      'time':'SELECT weekday,hour,count(*) incidents FROM crimes GROUP BY weekday,hour ORDER BY weekday,hour',
      'season':f'SELECT season,count(*) incidents FROM crimes WHERE year < {last_year} GROUP BY season ORDER BY season',
      'areas':'SELECT community_area,count(*) incidents,sum(arrest) arrests,1.0*sum(arrest)/count(*) arrest_rate FROM crimes GROUP BY community_area ORDER BY incidents DESC',
      'categories':'SELECT primary_type,count(*) incidents,sum(arrest) arrests,1.0*sum(arrest)/count(*) arrest_rate FROM crimes GROUP BY primary_type ORDER BY incidents DESC'}
    out={}
    with sqlite3.connect(db) as c:
        c.row_factory=sqlite3.Row
        for name,q in queries.items():
            rows=[dict(r) for r in c.execute(q)]; out[name]=rows
            with (ROOT/'reports'/f'{name}.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    # Normalize season counts by actual calendar days in complete years.
    days={s:0 for s in ['Winter','Spring','Summer','Autumn']}
    date=dt.date.fromisoformat(cfg['start'])
    while date<dt.date(last_year,1,1):
        days[('Winter','Spring','Summer','Autumn')[(date.month%12)//3]]+=1; date+=dt.timedelta(days=1)
    for r in out['season']: r['days']=days[r['season']]; r['incidents_per_day']=r['incidents']/r['days']
    out['window']={'start':cfg['start'],'end_exclusive':cfg['end'],'comparison_months':months,'last_year':last_year}
    dump(ROOT/'reports/analysis.json',out)
    return out

def run(args):
    cfg=json.loads((ROOT/'config/project.json').read_text())
    run_id=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:6]
    raw=Path(args.snapshot).resolve() if args.snapshot else ROOT/'data/raw'/run_id
    reports=ROOT/'reports'; reports.mkdir(exist_ok=True)
    db=ROOT/'data/crimes.sqlite'; metrics=[]; results={}
    actions={'extract':lambda:json.loads((raw/'manifest.json').read_text()) if args.snapshot else extract(cfg,raw),'transform_load':lambda:load(raw,db,cfg),'validate':lambda:validate(db,results['extract']),'analyze':lambda:analyze(db,cfg),'visualize':lambda:__import__('visualize').build(results['analyze'],raw)}
    try:
        for task,deps in DAG.items():
            assert all(d in results for d in deps)
            start=time.perf_counter(); status='success'
            try: results[task]=actions[task]()
            except Exception: status='failed'; raise
            finally:
                metrics.append({'task':task,'dependencies':deps,'status':status,'seconds':round(time.perf_counter()-start,3)})
                dump(reports/'run.json',{'run_id':run_id,'snapshot':str(raw.relative_to(ROOT)) if raw.is_relative_to(ROOT) else str(raw),'mode':'offline_replay' if args.snapshot else 'live_api','tasks':metrics})
    finally:
        print(json.dumps(metrics,indent=2))
    print('Complete. Open reports/dashboard.html')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--snapshot',help='Replay a raw snapshot directory without API access'); run(p.parse_args())
