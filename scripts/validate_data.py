"""Independent checks of persisted files using Decimal and SQL, not generator functions."""
from pathlib import Path
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
import csv, sqlite3, json, hashlib, sys, platform

ROOT=Path(__file__).resolve().parents[1]
def read(path):
    with (ROOT/path).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def write(path,rows):
    with (ROOT/path).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def text(path,s): (ROOT/path).write_text(s.strip()+'\n',encoding='utf-8')
checks=[]
def check(name,actual,expected,method='SQLite / persisted CSV'):
    ok=actual==expected
    checks.append(dict(test_id=f'T{len(checks)+1:03}',test=name,status='PASS' if ok else 'FAIL',actual=str(actual),expected=str(expected),method=method))
    if not ok: print('FAILED',name,actual,expected)

table_names=['products','customers','locations','orders','order_items','returns','inventory','targets','calendar','historical_monthly_summary']
data={n:read(f'core/{n}.csv') for n in table_names}
dbpath=ROOT/'reference/validation.sqlite'
dbpath.unlink(missing_ok=True)
c=sqlite3.connect(dbpath);c.execute('PRAGMA foreign_keys=ON')
c.executescript((ROOT/'reference/validation_schema.sql').read_text())
for n,rows in data.items():
    fields=list(rows[0]);numeric={r[1] for r in c.execute(f'PRAGMA table_info({n})') if r[2] in ('INTEGER','BIGINT')}
    records=[[None if v=='' else int(v) if k in numeric else v for k,v in row.items()] for row in rows]
    c.executemany(f'INSERT INTO {n} VALUES ({",".join("?" for _ in fields)})',records)
c.commit()
check('SQLite integrity',c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
check('Foreign key violations',len(c.execute('PRAGMA foreign_key_check').fetchall()),0)
expected_counts=[60,2500,7,12000,30000,3272,5040,84,1096,420]
# Return count is seed dependent: validate against actual unique inputs, never fixed after edits.
expected_counts[5]=len(data['returns'])
for n,expected in zip(table_names,expected_counts):check(f'{n}: imported row count',c.execute(f'SELECT COUNT(*) FROM {n}').fetchone()[0],expected)
for n,rows in data.items():
    required=[r[1] for r in c.execute(f'PRAGMA table_info({n})') if r[3] or r[5]]
    check(f'{n}: required values present',sum(any(row[k]=='' for k in required) for row in rows),0,'CSV required-field scan')
check('Six stores and one online member',c.execute("SELECT SUM(channel='Store'),SUM(channel='Online') FROM locations").fetchone(),(6,1))
check('Orders stay in core year',c.execute("SELECT COUNT(*) FROM orders WHERE order_date<'2025-01-01' OR order_date>'2025-12-31'").fetchone()[0],0)
check('Customer enrollment precedes order',c.execute('SELECT COUNT(*) FROM orders o JOIN customers x USING(customer_id) WHERE x.enrollment_date>o.order_date').fetchone()[0],0)
check('No cancelled order receives a return',c.execute("SELECT COUNT(*) FROM returns r JOIN order_items i USING(order_item_id) JOIN orders o USING(order_id) WHERE o.status<>'Completed'").fetchone()[0],0)
check('Return dates valid relative to sale and cutoff',c.execute("SELECT COUNT(*) FROM returns r JOIN order_items i USING(order_item_id) JOIN orders o USING(order_id) WHERE r.return_date<o.order_date OR r.return_date>'2026-01-31'").fetchone()[0],0)
check('Partial refund pricing is exact',c.execute('SELECT COUNT(*) FROM returns r JOIN order_items i USING(order_item_id) WHERE r.refund_paise*i.quantity<>r.returned_quantity*(i.quantity*i.unit_price_paise-i.discount_paise)').fetchone()[0],0)
check('Recovered cost follows documented damage policy',c.execute("SELECT COUNT(*) FROM returns r JOIN order_items i USING(order_item_id) WHERE r.recovered_cost_paise<>CASE WHEN r.reason='Damaged' THEN 0 ELSE r.returned_quantity*i.unit_cost_paise END").fetchone()[0],0)
check('Cumulative quantity/refund/cost caps',c.execute('''SELECT COUNT(*) FROM
 (SELECT r.order_item_id FROM returns r JOIN order_items i USING(order_item_id)
 GROUP BY r.order_item_id,i.quantity,i.unit_price_paise,i.discount_paise,i.unit_cost_paise
 HAVING SUM(r.returned_quantity)>i.quantity OR SUM(r.refund_paise)>i.quantity*i.unit_price_paise-i.discount_paise
 OR SUM(r.recovered_cost_paise)>i.quantity*i.unit_cost_paise) t''').fetchone()[0],0)
check('Multiple-return lines exist',c.execute('SELECT COUNT(*) FROM (SELECT order_item_id FROM returns GROUP BY order_item_id HAVING COUNT(*)>1)').fetchone()[0]>0,True)
check('Guest orders exist',c.execute('SELECT COUNT(*) FROM orders WHERE customer_id IS NULL').fetchone()[0]>0,True)
check('Historical first-of-month grain',all(r['month_start'].endswith('-01') and r['month_start'].startswith('2024') for r in data['historical_monthly_summary']),True,'CSV date scan')
check('Targets first-of-month grain',all(r['month_start'].endswith('-01') and r['month_start'].startswith('2025') for r in data['targets']),True,'CSV date scan')
cal=[date.fromisoformat(r['calendar_date']) for r in data['calendar']]
check('Calendar continuous through 2024–2026',cal,[date(2024,1,1)+timedelta(days=i) for i in range(1096)],'Python date sequence')
# Avoid long date lists in the report after the equality is checked.
checks[-1]['actual']=f'{len(cal)} continuous dates, {cal[0]} to {cal[-1]}'
checks[-1]['expected']='1096 continuous dates, 2024-01-01 to 2026-12-31'
check('Calendar attributes correct',all((int(r['year']),int(r['month']),r['month_start'],int(r['quarter']),int(r['iso_weekday']))==(d.year,d.month,d.replace(day=1).isoformat(),(d.month-1)//3+1,d.isoweekday()) for r,d in zip(data['calendar'],cal)),True,'Python date attributes')
check('Inventory dates are month ends',all((date.fromisoformat(r['snapshot_date'])+timedelta(days=1)).day==1 for r in data['inventory']),True,'Python date check')

# Independent event ledger. UNION ALL preserves returns without a matching in-period sale.
c.executescript('''CREATE VIEW validation_events AS
 SELECT o.order_date AS event_date,o.location_id,p.category,i.quantity*i.unit_price_paise AS gross_sales_paise,
 i.discount_paise AS discount_paise,i.quantity*i.unit_price_paise-i.discount_paise AS sales_after_discount_paise,
 0 AS refunds_paise,i.quantity*i.unit_cost_paise AS sale_cost_paise,0 AS recovered_cost_paise
 FROM order_items i JOIN orders o USING(order_id) JOIN products p USING(product_id) WHERE o.status='Completed'
 UNION ALL
 SELECT r.return_date,o.location_id,p.category,0,0,0,r.refund_paise,0,r.recovered_cost_paise
 FROM returns r JOIN order_items i USING(order_item_id) JOIN orders o USING(order_id) JOIN products p USING(product_id);
''')
metric_cols=['gross_sales_paise','discount_paise','sales_after_discount_paise','refunds_paise','sale_cost_paise','recovered_cost_paise']
sum_sql=','.join(f'SUM({k})' for k in metric_cols)
totals=dict(zip(metric_cols,c.execute(f"SELECT {sum_sql} FROM validation_events WHERE event_date>='2025-01-01' AND event_date<'2026-01-01'").fetchone()))
totals['net_sales_paise']=totals['sales_after_discount_paise']-totals['refunds_paise']
totals['net_cogs_paise']=totals['sale_cost_paise']-totals['recovered_cost_paise']
totals['gross_profit_paise']=totals['net_sales_paise']-totals['net_cogs_paise']
O={r['order_id']:r for r in data['orders']};I={r['order_item_id']:r for r in data['order_items']};P={r['product_id']:r for r in data['products']}

def independent_decimal(orders,items,returns,year):
    om={r['order_id']:r for r in orders};im={r['order_item_id']:r for r in items}
    groups=defaultdict(lambda:[Decimal(0)]*6)
    for r in items:
        o=om[r['order_id']]
        if o['status']!='Completed' or not o['order_date'].startswith(str(year)):continue
        key=(o['order_date'][:7]+'-01',o['location_id'],P[r['product_id']]['category'])
        q=Decimal(r['quantity']);price=Decimal(r['unit_price_paise'])/100;discount=Decimal(r['discount_paise'])/100;cost=Decimal(r['unit_cost_paise'])/100
        vector=[q*price,discount,q*price-discount,Decimal(0),q*cost,Decimal(0)]
        groups[key]=[a+b for a,b in zip(groups[key],vector)]
    for r in returns:
        if not r['return_date'].startswith(str(year)):continue
        i=im[r['order_item_id']];o=om[i['order_id']]
        key=(r['return_date'][:7]+'-01',o['location_id'],P[i['product_id']]['category'])
        groups[key][3]+=Decimal(r['refund_paise'])/100;groups[key][5]+=Decimal(r['recovered_cost_paise'])/100
    return groups

independent=independent_decimal(data['orders'],data['order_items'],data['returns'],2025)
for pos,k in enumerate(metric_cols):check(f'Independent Decimal INR reconciles {k}',sum(v[pos] for v in independent.values())*100,Decimal(totals[k]),'Decimal rupees vs SQL integer paise')
sql_groups={tuple(r[:3]):tuple(r[3:]) for r in c.execute(f"SELECT substr(event_date,1,7)||'-01',location_id,category,{sum_sql} FROM validation_events WHERE event_date<'2026-01-01' GROUP BY 1,2,3")}
controls=read('reference/monthly_2025_controls.csv')
check('All 420 monthly-location-category slices reconcile',sum(tuple(int(row[k]) for k in metric_cols)!=sql_groups.get((row['month_start'],row['location_id'],row['category']),(0,)*6) for row in controls),0)
check('Decimal slice reconciliation',sum(tuple(int(v*100) for v in values)!=sql_groups.get(key,(0,)*6) for key,values in independent.items()),0,'Decimal vs SQL by month, location, category')
old=independent_decimal(*[read(f'reference/build_inputs/historical_{n}.csv') for n in ['orders','order_items','returns']],2024)
check('All 420 historical controls independently reconstruct',sum(tuple(int(row[k]) for k in metric_cols)!=tuple(int(v*100) for v in old.get((row['month_start'],row['location_id'],row['category']),[Decimal(0)]*6)) for row in data['historical_monthly_summary']),0,'Independent Decimal from author-only 2024 generation inputs')
for row in data['targets']:
    month='2024'+row['month_start'][4:];group=[r for r in data['historical_monthly_summary'] if r['month_start']==month and r['location_id']==row['location_id']]
    net=sum(int(r['sales_after_discount_paise'])-int(r['refunds_paise']) for r in group)
    gp=sum(int(r['sales_after_discount_paise'])-int(r['refunds_paise'])-int(r['sale_cost_paise'])+int(r['recovered_cost_paise']) for r in group)
    assert int(row['net_sales_target_paise'])==(net*110+50)//100
    assert int(row['gross_profit_target_paise'])==(gp*108+50)//100
check('All 84 targets match documented policy',84,84,'Exact integer target reconstruction')
completed_count=c.execute("SELECT COUNT(*) FROM orders WHERE status='Completed'").fetchone()[0]
line_count=c.execute("SELECT COUNT(*) FROM order_items JOIN orders USING(order_id) WHERE status='Completed'").fetchone()[0]
enriched=c.execute("SELECT COUNT(*),SUM(quantity*unit_price_paise-discount_paise) FROM order_items JOIN orders USING(order_id) JOIN products USING(product_id) WHERE status='Completed'").fetchone()
check('Product enrichment preserves count and sales',enriched,(line_count,totals['sales_after_discount_paise']))
sf=read('core/derived/fact_sales.csv');rf=read('core/derived/fact_returns.csv')
check('Derived fact sales rows',len(sf),line_count,'CSV vs SQL')
check('Derived fact refunds total',sum(int(r['refund_paise']) for r in rf),sum(int(r['refund_paise']) for r in data['returns']),'CSV vs canonical source')
check('Derived fact sales total',sum(int(r['sales_after_discount_paise']) for r in sf),totals['sales_after_discount_paise'],'CSV vs SQL')
check('Derived fact sales details match source',all(r['order_id']==I[r['order_item_id']]['order_id'] and r['product_id']==I[r['order_item_id']]['product_id'] and r['location_id']==O[r['order_id']]['location_id'] and r['sale_date']==O[r['order_id']]['order_date'] and int(r['quantity'])==int(I[r['order_item_id']]['quantity']) and int(r['sale_cost_paise'])==int(I[r['order_item_id']]['quantity'])*int(I[r['order_item_id']]['unit_cost_paise']) for r in sf),True,'CSV detail check')
jan=c.execute("SELECT COUNT(*),COALESCE(SUM(sales_after_discount_paise),0),COALESCE(SUM(refunds_paise),0) FROM validation_events WHERE event_date>='2026-01-01' AND event_date<'2026-02-01'").fetchone()
check('Return-only January has refunds but no sales',jan[0]>0 and jan[1]==0 and jan[2]>0,True)
boundary=c.execute("SELECT event_date,SUM(sales_after_discount_paise),SUM(refunds_paise) FROM validation_events WHERE event_date IN ('2025-01-31','2025-02-01','2025-12-31','2026-01-01') GROUP BY event_date ORDER BY event_date").fetchall()
write('reference/month_boundary_controls.csv',[dict(event_date=r[0],sales_after_discount_paise=r[1],refunds_paise=r[2]) for r in boundary])

# First assignment, cleaning, and join fixtures are verified from saved starting files.
small=read('chapters/ch01/first_assignment.csv');answer=read('solutions/ch01/first_assignment_answer.csv')
small_total=sum(Decimal(r['quantity'])*Decimal(r['unit_price_inr']) for r in small)
check('CH01 row count',len(small),12,'CSV')
check('CH01 answer calculation',sum(Decimal(r['line_sales_inr']) for r in answer),small_total,'Independent Decimal arithmetic')
check('CH01 each answer line matches its source',all(a['order_item_id']==r['order_item_id'] and Decimal(a['line_sales_inr'])==Decimal(r['quantity'])*Decimal(r['unit_price_inr']) for r,a in zip(small,answer)),True,'Independent per-line calculation')
cats=read('solutions/ch01/category_answer.csv')
check('CH01 highest-unit category differs from highest sales',max(cats,key=lambda r:int(r['units']))['category']!=max(cats,key=lambda r:Decimal(r['sales_inr']))['category'],True,'Categorical comparison')
dirty=read('chapters/ch07/sales_dirty_source.csv');accepted=read('solutions/ch07/accepted.csv');quarantine=read('solutions/ch07/quarantine.csv');defects=read('reference/defect_ledger.csv')
check('CH07 row bridge',(len(dirty),len(accepted),len(quarantine)),(202,197,5),'CSV row accounting')
check('CH07 row IDs form exact partition',sorted(r['source_row_id'] for r in accepted+quarantine),sorted(r['source_row_id'] for r in dirty),'Set partition')
checks[-1]['actual']='202 IDs across accepted and quarantine';checks[-1]['expected']='202 source IDs, once each'
check('CH07 accepted keys unique',len({r['order_item_id'] for r in accepted}),197,'Business key count')
check('CH07 legitimate lookalikes survive',sum(r['product_id']=='P025' and r['quantity']=='2' and r['order_date']=='2025-01-01' and r['unit_price_inr']=='50.00' for r in accepted)>=2,True,'Known distinct business IDs')
clean_total=sum(Decimal(r['quantity'])*Decimal(r['unit_price_inr'])-Decimal(r['discount_inr']) for r in accepted)
canonical_accepted=sum(int(I[r['order_item_id']]['quantity'])*int(I[r['order_item_id']]['unit_price_paise'])-int(I[r['order_item_id']]['discount_paise']) for r in accepted)
check('CH07 accepted amounts reconcile to canonical subset',clean_total*100,Decimal(canonical_accepted),'Independent source comparison')
check('CH07 documented decisions cover every injected change',len(defects),10,'Defect ledger')
check('CH07 missing guest remains null',next(r['customer_id'] for r in accepted if r['source_row_id']=='SRC0017'),'','Null semantics')
original_ids={r['order_item_id'] for r in dirty}
original_value=sum(int(I[k]['quantity'])*int(I[k]['unit_price_paise'])-int(I[k]['discount_paise']) for k in original_ids)
unresolved_ids={r['order_item_id'] for r in quarantine if r['source_row_id'] not in ('SRC0201','SRC0202')}
unresolved_value=sum(int(I[k]['quantity'])*int(I[k]['unit_price_paise'])-int(I[k]['discount_paise']) for k in unresolved_ids)
check('CH07 canonical value bridge',canonical_accepted+unresolved_value,original_value,'Author truth only; not recoverable from dirty source alone')
write('reference/cleaning_reconciliation.csv',[
 dict(population='Original unique business lines',rows=200,known_canonical_sales_paise=original_value,meaning='Author control, not a valid raw dirty-file sum'),
 dict(population='Accepted lines',rows=197,known_canonical_sales_paise=canonical_accepted,meaning='Repaired valid learner output'),
 dict(population='Unresolved original lines',rows=3,known_canonical_sales_paise=unresolved_value,meaning='Excluded from learner financial output; values known only to author'),
 dict(population='Duplicate imports',rows=2,known_canonical_sales_paise='',meaning='No additional business sales')])
c.executescript((ROOT/'chapters/ch18/join_cases.sql').read_text())
faulty=c.execute('SELECT COUNT(*),SUM(s.sales_paise),SUM(r.refund_paise) FROM join_sales s LEFT JOIN join_returns r USING(line_id)').fetchone()
fixed=c.execute('WITH r AS (SELECT line_id,SUM(refund_paise) AS refund_paise FROM join_returns GROUP BY line_id) SELECT COUNT(*),SUM(s.sales_paise),SUM(COALESCE(r.refund_paise,0)) FROM join_sales s LEFT JOIN r USING(line_id)').fetchone()
check('CH18 faulty join reproduces inflation',faulty,(4,450000,60000))
check('CH18 pre-aggregated join fixes inflation',fixed,(3,350000,60000))
check('CH18 unmatched audit',c.execute('SELECT a.line_id FROM audit_input a LEFT JOIN products p USING(product_id) WHERE p.product_id IS NULL ORDER BY a.line_id').fetchall(),[('A2',),('A3',)])

# Refresh is executed on SQL source copies via a savepoint, then fully rolled back.
c.execute('SAVEPOINT refresh_test')
for table in ['orders','order_items']:
    rows=read(f'chapters/ch26/refresh_pack/{table}.csv')
    c.executemany(f'INSERT INTO {table} VALUES ({",".join("?" for _ in rows[0])})',[[v or None for v in row.values()] for row in rows])
refresh=c.execute("SELECT COUNT(DISTINCT o.order_id),COUNT(*),SUM(i.quantity*i.unit_price_paise-i.discount_paise),SUM(i.quantity*i.unit_cost_paise) FROM orders o JOIN order_items i USING(order_id) WHERE o.order_date='2026-02-01' AND o.status='Completed'").fetchone()
check('SQL refresh known additions',refresh,(1,1,32400,21600))
try:
    c.execute("INSERT INTO orders VALUES ('O2026-B0001','2026-02-01',NULL,'WEB','Completed')")
    duplicate_rejected=False
except sqlite3.IntegrityError:duplicate_rejected=True
check('Repeated batch rejected by primary key',duplicate_rejected,True)
c.execute('ROLLBACK TO refresh_test');c.execute('RELEASE refresh_test')
check('Canonical order count restored after refresh test',c.execute('SELECT COUNT(*) FROM orders').fetchone()[0],12000)

# Check the emitted setup script carries the same data, using only a compatibility adaptation.
# This deliberately does NOT count as PostgreSQL execution.
dump=(ROOT/'core/retail_database_setup.sql').read_text().replace('CREATE SCHEMA dafz_v01;','').replace('SET search_path TO dafz_v01;','')
scratch=sqlite3.connect(':memory:');scratch.execute('PRAGMA foreign_keys=ON');scratch.executescript(dump)
check('Setup SQL payload matches canonical tables',all(sorted(scratch.execute(f'SELECT * FROM {n}').fetchall(),key=repr)==sorted(c.execute(f'SELECT * FROM {n}').fetchall(),key=repr) for n in table_names),True,'SQLite compatibility adaptation; PostgreSQL NOT executed')
scratch.close()

# Sanity of annual story claims: amounts shown, no causal conclusion.
old_totals={k:sum(int(r[k]) for r in data['historical_monthly_summary']) for k in metric_cols}
for t in [old_totals]:
    t['net_sales_paise']=t['sales_after_discount_paise']-t['refunds_paise'];t['net_cogs_paise']=t['sale_cost_paise']-t['recovered_cost_paise'];t['gross_profit_paise']=t['net_sales_paise']-t['net_cogs_paise']
write('reference/annual_control_totals.csv',[dict(year=y,**t) for y,t in [(2024,old_totals),(2025,totals)]])
check('Story: 2025 net sales exceed 2024',totals['net_sales_paise']>old_totals['net_sales_paise'],True,'Executed annual totals')
check('Story: 2025 gross profit below 2024',totals['gross_profit_paise']<old_totals['gross_profit_paise'],True,'Executed annual totals')
check('Story: 2025 weighted discount rate higher',Decimal(totals['discount_paise'])/totals['gross_sales_paise']>Decimal(old_totals['discount_paise'])/old_totals['gross_sales_paise'],True,'Ratio of totals')
old_e=sum(int(r['sales_after_discount_paise']) for r in data['historical_monthly_summary'] if r['category']=='Electronics')
new_e=c.execute("SELECT SUM(sales_after_discount_paise) FROM validation_events WHERE category='Electronics' AND event_date<'2026-01-01'").fetchone()[0]
check('Story: electronics sales share higher',Decimal(new_e)/totals['sales_after_discount_paise']>Decimal(old_e)/old_totals['sales_after_discount_paise'],True,'Category sales mix')

ledger=[]
def entry(ex,metric,value,unit,source,filters,meaning):
    ledger.append(dict(exercise_id=ex,source_revision='0.1.0; see reference/manifest.json',source=source,filters=filters,metric=metric,expected_value=str(value),unit=unit,tolerance='0 paise / exact counts; INR rounded to 2 decimals',interpretation=meaning,execution_status='EXECUTED: Python/SQLite only'))
entry('CH01-E01','line_count',12,'rows','chapters/ch01/first_assignment.csv','all rows','Keep all 12 original lines')
entry('CH01-E01','sales',small_total,'INR','chapters/ch01/first_assignment.csv','all rows','No discounts in this subset')
for r in cats:
    entry('CH01-E02',r['category']+' units',r['units'],'units','chapters/ch01/first_assignment.csv',r['category'],'Units are distinct from revenue')
    entry('CH01-E02',r['category']+' sales',r['sales_inr'],'INR','chapters/ch01/first_assignment.csv',r['category'],'Sample only')
entry('CH07-E01','input_rows',202,'rows','chapters/ch07/sales_dirty_source.csv','all input rows','Raw financial total is undefined until missing price/text quantity are handled')
entry('CH07-E04','accepted_rows',197,'rows','solutions/ch07/accepted.csv','approved repairs; unresolved rows quarantined','Do not discard legitimate repeated business events')
entry('CH07-E04','quarantined_rows',5,'rows','solutions/ch07/quarantine.csv','3 unresolved plus 2 duplicate imports','Account for every source row')
entry('CH07-E05','accepted_sales_after_discount',clean_total,'INR','solutions/ch07/accepted.csv','accepted subset only','Not the total of all 200 original lines')
entry('CH18-E01','completed_sale_lines',line_count,'rows','core/order_items.csv','Completed orders only','Dimension enrichment must preserve count')
entry('CH18-E01','sales_after_discount',totals['sales_after_discount_paise'],'paise','core/order_items.csv','Completed orders only','Dimension enrichment must preserve sales')
entry('CH18-E02','unmatched_rows',2,'rows','chapters/ch18/join_cases.sql','audit_input','A2 unknown and A3 missing')
for ex,values in [('CH18-E03',faulty),('CH18-E04',fixed)]:
    for key,val,unit in zip(['joined_rows','sales','refunds'],values,['rows','paise','paise']):entry(ex,key,val,unit,'chapters/ch18/join_cases.sql','temporary teaching fixture','E03 deliberately wrong; E04 reconciled')
entry('CH26-E03','refresh_sales_delta',32400,'paise','chapters/ch26/refresh_pack','append once','SQL source append tested; native report refresh pending')
entry('CH26-E03','refresh_gross_profit_delta',10800,'paise','chapters/ch26/refresh_pack','append once','SQL arithmetic only')
for key,val in totals.items():entry('CORE-2025',key,val,'paise','core','2025 event dates; completed sales','2026 late refunds excluded from 2025 event period')
entry('CORE-RETURN-ONLY','January_2026_refunds',jan[2],'paise','core/returns.csv','2026-01-01 <= date < 2026-02-01','Sales AOV and gross margin undefined in this return-only slice')
write('reference/answer_ledger.csv',ledger)
write('reference/validation_checks.csv',checks)
c.commit();c.close()
failed=[t for t in checks if t['status']=='FAIL']
fmt=lambda n:f'INR {Decimal(n)/100:,.2f}'
lines=['# Data foundation validation report','',f'Dataset version 0.1.0. Seed 20261012. Checks run using Python {platform.python_version()} and SQLite {sqlite3.sqlite_version}.',
    '',f'Executed checks: {len(checks)}. Passed: {len(checks)-len(failed)}. Failed: {len(failed)}. Full evidence: validation_checks.csv.',
    '', '## Core records','', '|Table|Rows|','|---|---:|']
lines += [f'|{n}|{len(rows):,}|' for n,rows in data.items()]
lines += ['',f'Completed orders: {completed_count:,}; eligible sale lines: {line_count:,}. Cancelled orders remain in the source but contribute no sales.', '', '## Annual comparison (event-period rules)','', '|Metric|2024|2025|','|---|---:|---:|']
for key in ['gross_sales_paise','discount_paise','sales_after_discount_paise','refunds_paise','net_sales_paise','net_cogs_paise','gross_profit_paise']:
    lines.append(f'|{key.removesuffix("_paise").replace("_"," ")}|{fmt(old_totals[key])}|{fmt(totals[key])}|')
lines += ['',f'2025 gross margin: {Decimal(totals["gross_profit_paise"])/totals["net_sales_paise"]*100:.2f}%. Basic sales AOV: {fmt(Decimal(totals["sales_after_discount_paise"])/completed_count)}.',
    '', 'Higher sales, lower gross profit, deeper discounting and higher electronics share are verified features of this constructed dataset. They support investigation; they do not prove a causal effect of promotions. See the exact checks and metric rules.',
    '', '## Teaching cases', '',f'First assignment: 12 rows, {fmt(int(small_total*100))} sales.',
    f'Cleaning source: 202 inputs = 197 accepted + 3 unresolved originals + 2 duplicate imports. Accepted sales after discount: {fmt(canonical_accepted)}. Raw financial totals must be labeled unavailable because missing price and text quantity cannot be summed reliably.',
    'Join fixture: 3 sale lines become 4 joined rows; apparent sales rise from INR 3,500 to INR 4,500. Pre-aggregation restores INR 3,500 sales and INR 600 refunds.',
    f'January 2026: no new core sales, {fmt(jan[2])} refunds. The date spine must preserve this return-only period.',
    'Refresh fixture: +1 completed order, +1 line, +INR 324 sales and +INR 108 gross profit. Duplicate reapplication is rejected. SQL test changes were rolled back.',
    '', '## Execution limits and next gates', '',
    'Executed: Python generation, independent Decimal calculations, SQLite schema/import constraints, relationships, return limits, 420 current slices, 420 historical slices, chapter numeric fixtures and controlled source append. Monetary equality is exact in paise.',
    'NOT executed: PostgreSQL application/database setup, Excel formulas/PivotTables, Power Query/DAX/PBIX refresh, desktop UI steps, platform/licensing checks or GitHub download tests. No application pass is inferred from this report.',
    'The archive is a data foundation. Native XLSX/PBIX chapter files, remaining exercises and answer ledger entries, Q1 2026 and service-desk projects, publication downloads and manuscript remain pending.',
    '', '## Reproduction and integrity', '',
    'Use scripts/build_data.py followed by scripts/validate_data.py in a copy of the edition folder. Manifest lists SHA-256 hashes for all included files except the manifest itself. validation.sqlite is an author QA database. Historical build_inputs are author QA evidence for the distributed 2024 summary, not a substitute for a future learner project.']
if failed:lines+=['','## Unresolved failures']+[f'- {x["test"]}: actual {x["actual"]}; expected {x["expected"]}' for x in failed]
text('reference/validation_report.md','\n'.join(lines))
manifest=dict(dataset_version='0.1.0',seed=20261012,python=platform.python_version(),sqlite=sqlite3.sqlite_version,core_counts={n:len(r) for n,r in data.items()},validation=dict(executed=len(checks),passed=len(checks)-len(failed),failed=len(failed)),files=[])
for p in sorted(ROOT.rglob('*')):
    if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts:
        manifest['files'].append(dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
text('reference/manifest.json',json.dumps(manifest,indent=2))
print(json.dumps({'checks':len(checks),'failed':len(failed),'totals_2025_paise':totals,'first_assignment_inr':str(small_total),'file_count':len(manifest['files'])},indent=2))
sys.exit(1 if failed else 0)
