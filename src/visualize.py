"""Offline SVG charts and geographic choropleth without third-party dependencies."""
import html,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def svg(title,body,w=1000,h=560):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}"><rect width="100%" height="100%" fill="#ffffff"/><style>text{{font-family:Arial;fill:#183044;font-size:15px}}</style><text x="30" y="32" style="font-size:23px;font-weight:bold">{html.escape(title)}</text>{body}</svg>'
def bars(title,labels,values,fmt=lambda v:f'{v:,.0f}'):
    body=''; maximum=max(values) or 1
    for i,(label,value) in enumerate(zip(labels,values)):
        y=65+i*39; width=value/maximum*560
        body+=f'<text x="20" y="{y+19}">{html.escape(str(label))}</text><rect x="300" y="{y}" width="{width}" height="26" fill="#167d9a"/><text x="{310+width}" y="{y+19}">{fmt(value)}</text>'
    return svg(title,body,h=max(250,100+len(labels)*39))
def build(a,raw):
    out=ROOT/'reports/figures';out.mkdir(exist_ok=True)
    charts={}; annual=a['annual']; months=a['window']['comparison_months']
    charts['annual']=bars(f'Reported incidents, January–month {months} each year',[r['year'] for r in annual],[r['incidents'] for r in annual])
    top=[r['primary_type'] for r in a['categories'][:5]]
    years=[r['year'] for r in annual]; vals={(r['year'],r['primary_type']):r['incidents'] for r in a['category_year']}
    colors=['#167d9a','#d36b32','#556cb5','#4f8665','#9a5085'];maximum=max(vals.get((y,t),0) for y in years for t in top); body=''
    for j in range(5):
        y=460-j*90;v=maximum*j/4;body+=f'<text x="10" y="{y}">{v/1000:.0f}k</text><path d="M60 {y}H700" stroke="#dde5e8"/>'
    for i,year in enumerate(years):body+=f'<text x="{60+i*100}" y="490">{year}</text>'
    for typ,col in zip(top,colors):
        points=' '.join(f'{80+i*100},{460-vals.get((year,typ),0)/maximum*360}' for i,year in enumerate(years))
        body+=f'<polyline points="{points}" fill="none" stroke="{col}" stroke-width="3"/>'
        j=top.index(typ);body+=f'<text x="730" y="{130+j*45}" style="fill:{col};font-size:13px">{typ}</text>'
    charts['category_trends']=svg('Five largest categories, equal-month annual counts',body)
    charts['category_arrests']=bars('Recorded arrest share, ten largest categories',[r['primary_type'] for r in a['categories'][:10]],[r['arrest_rate'] for r in a['categories'][:10]],lambda v:f'{v:.1%}')
    charts['season']=bars('Seasonal incidents per calendar day, complete years',[r['season'] for r in a['season']],[r['incidents_per_day'] for r in a['season']])
    bounds=json.loads((raw/'boundaries.json').read_text()); names={int(r['area_num_1']):r['community'].title() for r in bounds}
    areas=[r for r in a['areas'] if r['community_area'] is not None]
    charts['areas']=bars('Largest community totals, entire extraction window',[names.get(r['community_area'],str(r['community_area'])) for r in areas[:10]],[r['incidents'] for r in areas[:10]])
    charts['area_arrests']=bars('Recorded arrest share, ten largest communities',[names.get(r['community_area'],str(r['community_area'])) for r in areas[:10]],[r['arrest_rate'] for r in areas[:10]],lambda v:f'{v:.1%}')
    peak=max(r['incidents'] for r in a['time']);body=''
    for h in range(24): body+=f'<text x="{115+h*34}" y="65">{h}</text>'
    for d,name in enumerate(['Mon','Tue','Wed','Thu','Fri','Sat','Sun']): body+=f'<text x="30" y="{100+d*51}">{name}</text>'
    for r in a['time']:
        alpha=.1+.9*r['incidents']/peak;x=110+r['hour']*34;y=78+r['weekday']*51
        body+=f'<rect x="{x}" y="{y}" width="32" height="48" fill="#126b91" fill-opacity="{alpha}"><title>{r["incidents"]:,} incidents</title></rect>'
    body+='<text x="30" y="490">Local incident time. Darker = more reported incidents. Midnight may include estimated times.</text>'
    charts['time']=svg('Day of week × hour of day, all records',body)
    counts={r['community_area']:r['incidents'] for r in areas};maximum=max(counts.values());body=''
    def project(p):return (40+(p[0]+87.95)*1500,70+(42.03-p[1])*1050)
    for r in bounds:
        area=int(r['area_num_1']);n=counts.get(area,0);path=''
        geom=r['the_geom'];polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
        for poly in polys:
            for ring in poly:
                pts=[project(p) for p in ring];path+='M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in pts)+'Z'
        intensity=n/maximum;color=f'rgb({int(225-205*intensity)},{int(241-135*intensity)},{int(246-100*intensity)})'
        body+=f'<path d="{path}" fill="{color}" stroke="white" stroke-width="1" fill-rule="evenodd"><title>{html.escape(names[area])}: {n:,}</title></path>'
    body+='<text x="680" y="110">Reported incident counts</text><text x="680" y="145">Darker = more incidents</text>'
    body+=f'<text x="680" y="180">Range: {min(counts.values()):,}–{maximum:,}</text><text x="680" y="225">77 community areas</text><text x="680" y="260">Hover for names and counts</text><text x="680" y="310">Counts are not population rates</text>'
    charts['community_map']=svg('Chicago community area crime counts',body,h=650)
    for name,content in charts.items(): (out/f'{name}.svg').write_text(content)
    body=''.join(f'<section>{v}</section>' for v in charts.values())
    page=f'<!doctype html><html lang="en"><meta charset="utf-8"><title>Chicago crime analysis</title><style>body{{max-width:1100px;margin:40px auto;font:18px Arial;background:#eef3f5;color:#183044}}section{{margin:30px 0}}svg{{width:100%}}</style><h1>Chicago crime patterns, 2020–2026</h1><p>Coverage: {a["window"]["start"]} through {a["window"]["end_exclusive"]} (exclusive). Equal-month annual comparison. Other charts use the entire window, except seasonality, which uses complete years.</p>{body}<p>Source: City of Chicago Crimes API ijzp-q8t2 and community boundaries igwz-8jzy. Reported crimes exclude unreported events. Arrest flags are neither convictions nor a measure of clearance. Counts are not adjusted for population or exposure. See methodology and snapshot manifest.</p></html>'
    (ROOT/'reports/dashboard.html').write_text(page)
    (ROOT/'reports/area_names.json').write_text(json.dumps(names,indent=2))
