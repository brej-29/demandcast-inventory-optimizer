"""Rebuild anonymous daily sales from the CC BY 4.0 UCI source archive."""
import csv
import hashlib
import io
import json
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://archive.ics.uci.edu/static/public/352/online+retail.zip'
CACHE = ROOT / 'data' / 'raw' / 'uci-online-retail.zip'
CACHE.parent.mkdir(parents=True, exist_ok=True)
if not CACHE.exists():
    urllib.request.urlretrieve(URL, CACHE)
blob = CACHE.read_bytes()
start, end = datetime(2010, 12, 1), datetime(2011, 12, 8)
cutoff = start + timedelta(days=120)
daily = defaultdict(Counter)
names, initial = {}, Counter()
with zipfile.ZipFile(io.BytesIO(blob)) as archive:
    book = openpyxl.load_workbook(io.BytesIO(archive.read('Online Retail.xlsx')), read_only=True, data_only=True)
    for invoice, code, description, quantity, date, price, _customer, country in book.active.iter_rows(min_row=2, values_only=True):
        code = str(code)
        if country != 'United Kingdom' or str(invoice).upper().startswith('C') or not code.isdigit() or not quantity or quantity <= 0 or not price or price <= 0 or not isinstance(date, datetime):
            continue
        date = datetime(date.year, date.month, date.day)
        if not start <= date <= end:
            continue
        daily[code][date] += quantity
        if date < cutoff:
            initial[code] += quantity
            names[code] = str(description)
cohort = [code for code, _ in sorted(initial.items(), key=lambda p: (-p[1], p[0]))[:8]]
out = ROOT / 'web' / 'data'
out.mkdir(parents=True, exist_ok=True)
with (out / 'retail.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['date', *cohort])
    for i in range((end - start).days + 1):
        date = start + timedelta(days=i)
        writer.writerow([date.date().isoformat(), *[daily[c][date] for c in cohort]])
metadata = {'source': URL, 'doi': 'https://doi.org/10.24432/C5BW33', 'creator': 'Daqing Chen', 'license': 'CC BY 4.0', 'archive_sha256': hashlib.sha256(blob).hexdigest(), 'selection': 'Eight highest unit-volume numeric item codes in first 120 days; UK, positive sales, non-cancelled, positive price.', 'start': str(start.date()), 'end': str(end.date()), 'items': [{'code': c, 'name': names[c]} for c in cohort]}
(out / 'provenance.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'days': (end - start).days + 1, 'items': cohort, 'sha256': metadata['archive_sha256']}))
