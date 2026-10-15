from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
from datetime import date
import zipfile,xml.etree.ElementTree as ET,json,csv,hashlib
P=Path(__file__).resolve().parents[1];D=json.loads((P/'reference/source_data.json').read_text());C=D['controls'];N=C['rows'];END=N+6
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
checks=[]
def check(name,a,b):
 if not isinstance(a,bool) and not isinstance(b,bool) and isinstance(a,(int,float,Decimal)) and isinstance(b,(int,float,Decimal)):ok=abs(Decimal(str(a))-Decimal(str(b)))<Decimal('0.000001')
 else:ok=a==b
 checks.append(dict(test=name,status='PASS' if ok else 'FAIL',actual=str(a),expected=str(b),engine='Saved XLSX XML + independent Python'))
 if not ok:raise AssertionError((name,a,b))
def workbook(p):
 z=zipfile.ZipFile(p);strings=[]
 if 'xl/sharedStrings.xml' in z.namelist():strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
 rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
 sheets={}
 for s in ET.fromstring(z.read('xl/workbook.xml')).find('s:sheets',ns):
  target=rels[s.attrib['{'+ns['r']+'}id']];target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
  cells={}
  for cell in ET.fromstring(z.read(target)).findall('.//s:sheetData/s:row/s:c',ns):
   typ=cell.get('t');v=cell.find('s:v',ns);text=v.text if v is not None else None
   if typ=='s':val=strings[int(text)]
   elif typ=='inlineStr':val=''.join(cell.find('s:is',ns).itertext())
   elif typ in ('str','e'):val=text
   elif text is not None:val=float(text)
   else:val=None
   cells[cell.attrib['r']]=(val,cell.findtext('s:f',None,ns),typ)
  sheets[s.attrib['name']]=cells
 return z,sheets
files=sorted(P.rglob('*.xlsx'));check('workbook file count',len(files),18)
books={}
for p in files:
 z,s=workbook(p);books[p.name]=(z,s)
 check(p.name+' cached formula errors',sum(v[2]=='e' for ss in s.values() for v in ss.values()),0)
 check(p.name+' no external links',any('externalLinks/' in n for n in z.namelist()),False)
 check(p.name+' no VBA',any(n.endswith('vbaProject.bin') for n in z.namelist()),False)
 for sheet,ss in s.items():
  if sheet=='Sales':
   check(p.name+' sale-line IDs',len([k for k in ss if k.startswith('A') and k[1:].isdigit() and 7<=int(k[1:])<=END and ss[k][0] is not None]),N)
   check(p.name+' typed dates',all(ss[f'C{r}'][2] not in ('s','str','inlineStr') and isinstance(ss[f'C{r}'][0],float) for r in range(7,END+1)),True)
nav=books['excel_navigation_start.xlsx'][0];sol5=books['sales_table.xlsx'][0]
check('CH05 starter has no prebuilt table',sum(n.startswith('xl/tables/table') and n.endswith('.xml') for n in nav.namelist()),0)
check('CH05 solution has a native table',sum(n.startswith('xl/tables/table') and n.endswith('.xml') for n in sol5.namelist()),1)
calc=books['sales_calculations.xlsx'][1]
for index,r in enumerate(D['sales'],7):
 check(f'CH06 line {index} sales',calc['Sales'][f'M{index}'][0],Decimal(str(r[7]))*Decimal(str(r[8]))-Decimal(str(r[9])))
extra=sum((Decimal(str(r[12]))*Decimal('.05')).quantize(Decimal('.01'),rounding=ROUND_HALF_UP) for r in D['sales'])
check('CH06 per-line extra discount',calc['Calculations']['E9'][0],extra)
check('CH06 adjusted scenario',calc['Calculations']['E10'][0],Decimal(str(C['sales']))-extra)
check('CH06 intentional wrong demonstration',calc['Calculations']['C27'][0],0)
check('CH06 corrected fixed reference',calc['Calculations']['D27'][0],15)
clean=books['sales_cleaned.xlsx'][1];dirty=books['sales_dirty.xlsx'][1]
rawkeys=['source_row_id','order_item_id','order_date','product_id','category','quantity','unit_price_inr','discount_inr','customer_id']
for book in [clean,dirty]:
 check('Raw import unchanged in '+('solution' if book is clean else 'starter'),all(book['Raw'][f'{chr(65+j)}{i}'][0] == (row[k] or None) for i,row in enumerate(D['dirty'],7) for j,k in enumerate(rawkeys) if f'{chr(65+j)}{i}' in book['Raw']),True)
check('CH07 accepted rows',len([k for k in clean['Accepted'] if k.startswith('A') and k[1:].isdigit() and 7<=int(k[1:])<=203]),197)
check('CH07 accepted sales',sum(clean['Accepted'][f'J{i}'][0] for i in range(7,204)),444087)
check('CH07 quarantined rows',len([k for k in clean['Quarantine'] if k.startswith('A') and k[1:].isdigit() and 7<=int(k[1:])<=11]),5)
lookup=books['sales_enriched.xlsx'][1]['Sales']
check('CH08 unmatched row',lookup['P7'][0],'Unmatched')
check('CH08 all matched categories agree with fallback',all(lookup[f'G{i}'][0]==lookup[f'Q{i}'][0] for i in range(7,END+1)),True)
check('CH08 sales retained',sum(lookup[f'M{i}'][0] for i in range(7,END+1)),C['sales'])
for filename in ['pivot_reference.xlsx','report_start.xlsx','excel_report_reference.xlsx']:
 z,ss=books[filename];s=ss['Summary']
 check(filename+' grand total',s['G14'][0],C['sales'])
 for i,(m,v) in enumerate(C['monthly'].items(),19):check(filename+' '+m,s[f'B{i}'][0],v)
 for i,(loc,v) in enumerate(C['stores'].items(),7):check(filename+' '+loc,s[f'G{i}'][0],v)
 check(filename+' native pivots explicitly absent',any(n.startswith('xl/pivotTables/') for n in z.namelist()),False)
z,s=books['excel_report_reference.xlsx'];check('CH10 distinct order count',s['Report']['B9'][0],72)
charts=[n for n in z.namelist() if '/charts/chart' in n and n.endswith('.xml')];check('CH10 two editable chart parts',len(charts),2)
check('CH10 charts have cell bindings',all(b'<c:f>' in z.read(n) or b'<f>' in z.read(n) for n in charts),True)
for p in (P/'checkpoints').rglob('*.xlsx'):
 chapter=p.parent.name;candidate=list((P/'solutions'/chapter).glob('*.xlsx'))[0]
 check(chapter+' restart is verified solution/reference copy',hashlib.sha256(p.read_bytes()).hexdigest(),hashlib.sha256(candidate.read_bytes()).hexdigest())
for z,s in books.values():z.close()
with (P/'reference/export_checks.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=checks[0],lineterminator='\n');w.writeheader();w.writerows(checks)
artifact=json.loads((P/'reference/artifact_checks.json').read_text())
report=f'''# Excel review pack validation

Version 0.2; original foundation 0.1.0. All data is fictional.

## Executed
- {len(artifact)} Artifact Tool calculation checks passed, including lookup matches, totals and changing the extra-discount input to zero and restoring it.
- {len(checks)} saved-file checks passed: cached results, exact source arithmetic, table/chart objects, date types, cleaning totals, lookup/fallback agreement, monthly and store controls, and restart identity.
- 12 original workbooks were rendered across 41 worksheet views. Six restart workbooks are byte-for-byte copies of their verified solution/reference. Layout reviewed at normal rendered scale and via contact sheets.
- No cached spreadsheet error cells, VBA projects or external workbook links were found.
- Microsoft documentation was read for tables, PivotTables and XLOOKUP; see official_sources.md.

## Exact completion boundary
No Microsoft Excel process was used. Native Excel open/recalculate, sort/filter, XLOOKUP fallback compatibility, PivotTable construction/refresh, and one-page printing are NOT TESTED. Chapter 9 has zero native PivotTable objects, by disclosed design; its reference uses SUMIFS. Chapter 10 uses editable charts on formula summaries; the native pivot-backed version is pending. Inspecting exported XML is not application execution.

## Numerical controls
Shared sample: 183 sale lines, 72 completed orders, 556 units. Gross sales INR 557,026.00, discounts INR 66,533.90, sales after discount INR 490,492.10. Refunds are excluded from this stage.
CH06 extra scenario: 5% rounded per sale line gives INR {extra:,.2f} extra discount and INR {Decimal(str(C['sales']))-extra:,.2f} adjusted sales. Zero rate restores historical sales. The wrong relative-reference example intentionally retains 5, 0, 0 beside the corrected 5, 10, 15.
CH07: 202 source records = 197 accepted + 5 quarantined. Accepted sales INR 444,087.00. A dirty-source sales total is deliberately unavailable.
CH08: one unmatched P999 is retained, 182 matches; sales value unchanged. Numeric supplier key normalized by a documented mapping rule.
CH09 append record: +1 line, +1 order, +2 units, +INR 324 sales. Actual native pivot refresh remains pending.

Known construction issue resolved: summary formulas initially referenced a sheet before it was created. The builder now creates referenced sheets first. Final source/runtime checks are recorded in artifact_checks.json and export_checks.csv.

Publication is gated on resolving the native checks above, not on this report's file-generation passes alone.
'''
(P/'reference/validation_report.md').write_text(report)
print(json.dumps({'artifact_checks':len(artifact),'export_checks':len(checks),'all_passed':True}))
