"""Validate maintained static pages without regenerating editorial copy."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re, sys, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://picks.pegrio.com'
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.canonical=[];self.links=[];self.scripts=[];self.h1=0;self.active=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1':self.h1+=1
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag=='script':self.active={'attrs':a,'body':''};self.scripts.append(self.active)
    def handle_data(self,data):
        if self.active is not None:self.active['body']+=data
    def handle_endtag(self,tag):
        if tag=='script':self.active=None

errors=[];paths=[ROOT/'index.html',*sorted(ROOT.glob('*/index.html'))]
guide_slugs={p.parent.name for p in paths if p.parent.name.startswith('best-')}
baseline=set(json.loads((ROOT/'scripts/guide-baseline.json').read_text()))
if guide_slugs!=baseline:errors.append('Guide URL set changed; review baseline deliberately, do not silently remove pages.')
urls=[]
for path in paths:
    raw=path.read_text();page=Page();page.feed(raw)
    slug='' if path==ROOT/'index.html' else '/'+path.parent.name
    canonical=ORIGIN+slug;urls.append(canonical)
    if page.canonical!=[canonical]:errors.append(f'{slug or "/"}: wrong/multiple canonical')
    if page.h1!=1:errors.append(f'{slug or "/"}: expected one H1')
    loaders=[s for s in page.scripts if s['attrs'].get('src','').startswith('/assets/analytics.js')]
    if len(loaders)!=1:errors.append(f'{slug}: expected one consent-aware loader')
    if 'googletagmanager.com' in raw or re.search(r'\bgtag\s*\(',raw):errors.append(f'{slug}: direct analytics bypasses consent loader')
    for script in page.scripts:
        if script['attrs'].get('type')=='application/ld+json':
            try:json.loads(script['body'])
            except json.JSONDecodeError:errors.append(f'{slug}: invalid JSON-LD');continue
            if any(k in script['body'] for k in ['aggregateRating','reviewCount','priceCurrency']):errors.append(f'{slug}: product/rating data requires verified evidence')
    for href in page.links:
        parsed=urlsplit(href)
        if parsed.netloc or not parsed.path or not parsed.path.startswith('/'):continue
        target=ROOT/unquote(parsed.path).lstrip('/')
        if not(target.is_file() or (target/'index.html').is_file()):errors.append(f'{slug}: broken internal link {href}')
    if slug.startswith('/best-') and not any(x in raw for x in ['Evidence note','Source check, not a floor test','A source-based comparison']):errors.append(f'{slug}: missing evidence statement')
    cleaned=re.sub(r'<aside class="editorial-note">.*?</aside>','',raw,flags=re.S)
    if re.search(r'We tested \d|In our testing|After testing a dozen|verified buyer feedback|hands-on research|we ran each.{0,80}through',cleaned,re.I):errors.append(f'{slug}: unsupported test wording returned')

ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
listed=[n.text for n in ET.parse(ROOT/'sitemap.xml').getroot().iter(ns+'loc')]
if set(listed)!=set(urls) or len(listed)!=len(urls):errors.append('Sitemap does not match canonical page set')
for message in errors:print('ERROR:',message)
print(f'Validated {len(paths)} pages, {len(guide_slugs)} preserved guide URLs, sitemap, internal links, metadata and consent-loader coverage; {len(errors)} errors.')
sys.exit(bool(errors))
