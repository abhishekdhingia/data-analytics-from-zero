"""Original synthetic teaching data. Standard-library only; run from any directory.
Money is integer paise. Never run this against an existing published edition.
"""
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict
from random import Random
import csv, json, calendar, sqlite3, shutil

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.1.0'
SEED = 20261012

def write_csv(path, rows, fields=None):
    rows = list(rows)
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or list(rows[0])
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader(); w.writerows(rows)

def write_text(path, text):
    p = ROOT / path; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.strip()+'\n', encoding='utf-8')

def money(paise):
    return f'{paise//100}.{paise%100:02d}'

CATEGORIES = ['Kitchen', 'Home care', 'Stationery', 'Personal care', 'Electronics']
names = [
    ['Steel cup','Lunch box','Storage jar','Serving bowl','Water bottle','Tea strainer','Measuring cup','Spice box','Plate set','Cutting board','Pan','Kettle'],
    ['Cleaning cloth','Scrub pad','Floor brush','Dustpan','Laundry bag','Storage basket','Mop','Waste bin','Hanger set','Shoe rack','Door mat','Laundry stand'],
    ['Notebook','Pen pack','Pencil pack','Eraser pack','Ruler','Folder','Marker pack','Drawing pad','Stapler','Desk tray','Planner','Paper pack'],
    ['Soap pack','Shampoo','Hand wash','Toothbrush pack','Body lotion','Comb','Face towel','Travel pouch','Hair oil','Sunscreen','Grooming kit','Bath towel'],
    ['USB cable','Mouse','Keyboard','USB hub','Desk light','Earphones','Power bank','Speaker','Webcam','Router','Monitor','Tablet']]
base = [18000, 12000, 5000, 14000, 125000]
products = []
for cat in range(5):
    for n, name in enumerate(names[cat]):
        products.append(dict(product_id=f'P{len(products)+1:03}', product_name=name,
            category=CATEGORIES[cat], active=1))
locations = [dict(location_id=f'S{i:02}', location_name=f'Store {i:02}', channel='Store') for i in range(1,7)]
locations.append(dict(location_id='WEB', location_name='Online', channel='Online'))
rng = Random(SEED)
customers = [dict(customer_id=f'C{i:05}', enrollment_date=(date(2022,1,1)+timedelta(days=rng.randrange(700))).isoformat(),
    segment=rng.choice(['Household','Student','Small business'])) for i in range(1,2501)]
P = {p['product_id']:p for p in products}

def transactions(year, count, seed):
    rng = Random(seed); orders=[]; items=[]; returns=[]
    for i in range(count):
        year_days=(date(year+1,1,1)-date(year,1,1)).days
        day = date(year,1,1)+timedelta(days=(i*year_days)//count)
        order_id=f'O{year}-{i+1:05}'
        order = dict(order_id=order_id, order_date=day.isoformat(),
            customer_id=None if i%9==0 else rng.choice(customers)['customer_id'],
            location_id=rng.choices([x['location_id'] for x in locations], weights=[13,13,12,12,12,12,26])[0],
            status='Cancelled' if i%41==0 else 'Completed')
        # Exactly two or three lines per order; guarantees 30,000 for 12,000 orders.
        orders.append(order)
        for j in range(2+i%2):
            # A higher electronics share and deeper discounting in 2025 are hypotheses to test.
            cat=rng.choices(range(5),weights=[22,21,22,23,12] if year==2024 else [18,18,20,20,24])[0]
            n=rng.randrange(12); pid=f'P{cat*12+n+1:03}'
            qty=rng.randint(1,5)
            if i in (2,3) and j==0:
                cat=2;n=0;pid='P025';qty=2
                order['location_id']='S01';order['customer_id']=None
            if i==123 and j==0: qty=80
            price=(base[cat]+n*base[cat]//5)//100*100
            # Per-unit discount and refund stay exact in paise, including partial returns.
            rate=rng.choice([0,0,0,5,10]) if year==2024 else rng.choice([0,5,10,15,20])
            if year==2025 and day.month in [10,11]: rate=min(30,rate+10)
            if i in (2,3) and j==0:rate=0
            unit_discount=price*rate//100
            cost_rate=[58,60,50,62,82][cat]+(2 if year==2025 else 0)
            unit_cost=price*cost_rate//100
            item=dict(order_item_id=f'L{year}-{len(items)+1:06}',order_id=order_id,product_id=pid,
                quantity=qty,unit_price_paise=price,discount_paise=unit_discount*qty,unit_cost_paise=unit_cost)
            items.append(item)
            if order['status']=='Completed' and (rng.random()<(0.05 if year==2024 else 0.09) or (i==1 and j==0)):
                # Force one known repeated-return example without exceeding sold quantity.
                if i==1 and j==0: item['quantity']=max(qty,3); item['discount_paise']=unit_discount*item['quantity']; qty=item['quantity']
                total=rng.randint(1,qty)
                if i==1 and j==0: total=2
                chunks=[1,total-1] if total>=2 and (rng.random()<0.45 or (i==1 and j==0)) else [total]
                for k,q in enumerate(chunks):
                    rd=day+timedelta(days=rng.randint(1,14)+k*15)
                    reason=rng.choice(['Changed mind','Damaged','Wrong item'])
                    returns.append(dict(return_id=f'R{year}-{len(returns)+1:05}', order_item_id=item['order_item_id'],
                        return_date=rd.isoformat(),returned_quantity=q,refund_paise=q*(price-unit_discount),
                        reason=reason,recovered_cost_paise=0 if reason=='Damaged' else q*unit_cost))
    return orders,items,returns

orders,items,returns=transactions(2025,12000,SEED+2025)
O={r['order_id']:r for r in orders}; I={r['order_item_id']:r for r in items}

def summarize(orders,items,returns,year):
    O={x['order_id']:x for x in orders}; I={x['order_item_id']:x for x in items}
    buckets={}
    for month in range(1,13):
        for loc in locations:
            for cat in CATEGORIES:
                key=(f'{year}-{month:02}-01',loc['location_id'],cat)
                buckets[key]=dict(month_start=key[0],location_id=key[1],category=cat,
                    gross_sales_paise=0,discount_paise=0,sales_after_discount_paise=0,
                    refunds_paise=0,sale_cost_paise=0,recovered_cost_paise=0)
    for i in items:
        o=O[i['order_id']]
        if o['status']!='Completed' or not o['order_date'].startswith(str(year)):continue
        b=buckets[(o['order_date'][:7]+'-01',o['location_id'],P[i['product_id']]['category'])]
        gross=i['quantity']*i['unit_price_paise']; disc=i['discount_paise']
        b['gross_sales_paise']+=gross; b['discount_paise']+=disc
        b['sales_after_discount_paise']+=gross-disc; b['sale_cost_paise']+=i['quantity']*i['unit_cost_paise']
    for r in returns:
        if not r['return_date'].startswith(str(year)):continue
        i=I[r['order_item_id']]; o=O[i['order_id']]
        b=buckets[(r['return_date'][:7]+'-01',o['location_id'],P[i['product_id']]['category'])]
        b['refunds_paise']+=r['refund_paise'];b['recovered_cost_paise']+=r['recovered_cost_paise']
    return list(buckets.values())

old_orders,old_items,old_returns=transactions(2024,10800,SEED+2024)
for name, rows in [('orders',old_orders),('order_items',old_items),('returns',old_returns)]:
    write_csv(f'reference/build_inputs/historical_{name}.csv',rows)
historical=summarize(old_orders,old_items,old_returns,2024)
current=summarize(orders,items,returns,2025)
targets=[]
for month in range(1,13):
    for loc in locations:
        subset=[b for b in historical if b['month_start']==f'2024-{month:02}-01' and b['location_id']==loc['location_id']]
        net=sum(b['sales_after_discount_paise']-b['refunds_paise'] for b in subset)
        gp=sum(b['sales_after_discount_paise']-b['refunds_paise']-b['sale_cost_paise']+b['recovered_cost_paise'] for b in subset)
        targets.append(dict(month_start=f'2025-{month:02}-01',location_id=loc['location_id'],net_sales_target_paise=(net*110+50)//100,gross_profit_target_paise=(gp*108+50)//100))
inventory=[]
for month in range(1,13):
    d=date(2025,month,calendar.monthrange(2025,month)[1]).isoformat()
    for loc in locations:
        for p in products:
            inventory.append(dict(snapshot_date=d,location_id=loc['location_id'],product_id=p['product_id'],stock_quantity=rng.choice([0,0,5,12,25,40,65,100])))
dates=[]
d=date(2024,1,1)
while d<=date(2026,12,31):
    dates.append(dict(calendar_date=d.isoformat(),year=d.year,month=d.month,month_start=d.replace(day=1).isoformat(),quarter=(d.month-1)//3+1,iso_weekday=d.isoweekday()));d+=timedelta(days=1)
tables=dict(products=products,customers=customers,locations=locations,orders=orders,order_items=items,returns=returns,inventory=inventory,targets=targets,calendar=dates,historical_monthly_summary=historical)
for name, rows in tables.items():write_csv(f'core/{name}.csv',rows)
write_csv('reference/monthly_2025_controls.csv',current)

# Consistent separate facts for Power BI preparation. These are derived exports, not additional sales.
sales_fact=[]; returns_fact=[]
for i in items:
    o=O[i['order_id']]
    if o['status']=='Completed':
        sales_fact.append(dict(order_item_id=i['order_item_id'],order_id=i['order_id'],sale_date=o['order_date'],
            product_id=i['product_id'],location_id=o['location_id'],customer_id=o['customer_id'],quantity=i['quantity'],
            gross_sales_paise=i['quantity']*i['unit_price_paise'],discount_paise=i['discount_paise'],
            sales_after_discount_paise=i['quantity']*i['unit_price_paise']-i['discount_paise'],sale_cost_paise=i['quantity']*i['unit_cost_paise']))
for r in returns:
    i=I[r['order_item_id']];o=O[i['order_id']]
    returns_fact.append(dict(**r,product_id=i['product_id'],location_id=o['location_id'],original_sale_date=o['order_date']))
write_csv('core/derived/fact_sales.csv',sales_fact);write_csv('core/derived/fact_returns.csv',returns_fact)

# Small original first assignment, drawn from undiscouted completed core lines.
selected=[]
for cat in CATEGORIES:
    selected.extend([i for i in items if i['discount_paise']==0 and O[i['order_id']]['status']=='Completed' and P[i['product_id']]['category']==cat][:2])
selected.extend([i for i in items if i['discount_paise']==0 and O[i['order_id']]['status']=='Completed' and P[i['product_id']]['category']=='Stationery'][2:4])
small=[dict(order_item_id=i['order_item_id'],order_date=O[i['order_id']]['order_date'],product=P[i['product_id']]['product_name'],category=P[i['product_id']]['category'],quantity=i['quantity'],unit_price_inr=money(i['unit_price_paise'])) for i in selected]
write_csv('chapters/ch01/first_assignment.csv',small)
write_csv('solutions/ch01/first_assignment_answer.csv',[dict(**r,line_sales_inr=money(i['quantity']*i['unit_price_paise'])) for r,i in zip(small,selected)])
write_text('chapters/ch01/assignment_brief.md','''# First assignment
All records are fictional. This is a selected 12-line sample, not a representative annual sample. Prices exclude tax. These selected lines have no discount and this task does not deduct refunds.

CH01-E01: Open first_assignment.csv. Calculate quantity × unit_price_inr for every line. Save as first_sales_calculations.csv. Pass: 12 lines and the total in solutions/ch01/first_assignment_answer.csv.
CH01-E02: Group units and line sales by category. Save as category_comparison.csv. Pass: category totals match solutions/ch01/category_answer.csv and reconcile to E01.
CH01-E03: Save first_observation.md. Write one finding with numbers, one sample limitation, and one follow-up question. Pass: the claim follows from this sample, labels units and INR correctly, and makes no claim about net profit.
''')
group=defaultdict(lambda:[0,0])
for i in selected:
    v=group[P[i['product_id']]['category']];v[0]+=i['quantity'];v[1]+=i['quantity']*i['unit_price_paise']
write_csv('solutions/ch01/category_answer.csv',[dict(category=k,units=v[0],sales_inr=money(v[1])) for k,v in group.items()])
write_csv('checkpoints/ch01/first_assignment.csv',small)
sample_ids={i['order_id'] for i in items[:12]}
for name,rows in [('orders', [o for o in orders if o['order_id'] in sample_ids]),('order_items',items[:12]),('returns',[r for r in returns if r['order_item_id'] in {i['order_item_id'] for i in items[:12]}])]:
    write_csv(f'chapters/ch03/{name}_sample.csv',rows,fields=list(tables[name][0]))

# Cleaning source: 200 original sale lines, one legitimate lookalike, two duplicated import rows.
clean=[]
for i in [x for x in items if O[x['order_id']]['status']=='Completed'][:200]:
    o=O[i['order_id']];p=P[i['product_id']]
    clean.append(dict(source_row_id=f'SRC{len(clean)+1:04}',order_item_id=i['order_item_id'],order_date=o['order_date'],
        product_id=i['product_id'],category=p['category'],quantity=str(i['quantity']),unit_price_inr=money(i['unit_price_paise']),
        discount_inr=money(i['discount_paise']),customer_id=o['customer_id'] or ''))
dirty=[dict(x) for x in clean];defects=[]
def defect(idx,field,value,action,evidence):
    row=dirty[idx];old=row[field];row[field]=value
    defects.append(dict(defect_id=f'D{len(defects)+1:03}',source_row_id=row['source_row_id'],order_item_id=row['order_item_id'],field=field,dirty_value=value,canonical_value=old,handling=action,evidence=evidence))
defect(2,'category','  '+dirty[2]['category']+'  ','repair','Trim leading/trailing spaces; product master confirms category.')
defect(4,'category',dirty[4]['category'].upper(),'repair','Case-insensitive approved category mapping.')
defect(6,'order_date','02/01/2025','repair','Source convention is DD/MM/YYYY; compare provided source correction note.')
# Provide exact date correction from canonical record rather than infer an invented date.
dirty[6]['order_date']=date.fromisoformat(clean[6]['order_date']).strftime('%d/%m/%Y');defects[-1]['dirty_value']=dirty[6]['order_date']
defect(8,'quantity',' '+dirty[8]['quantity']+' ','repair','Trim text, then parse an integer.')
defect(10,'unit_price_inr','','quarantine','Price unavailable in learner extract; never impute catalog or mean price.')
defect(12,'quantity','two','quarantine','Unapproved textual quantity. No authenticated correction supplied.')
defect(14,'product_id','P999','quarantine','No match in supplied product master. Do not invent a category.')
defect(16,'customer_id','','retain','Guest customer is a legitimate null; customer identity is not needed for line sales.')
for idx in [20,30]:
    row=dict(dirty[idx]);row['source_row_id']=f'SRC{len(dirty)+1:04}';dirty.append(row)
    defects.append(dict(defect_id=f'D{len(defects)+1:03}',source_row_id=row['source_row_id'],order_item_id=row['order_item_id'],field='record',dirty_value='duplicate import',canonical_value='one original row',handling='duplicate quarantine',evidence=f'Exact duplicate of {dirty[idx]["source_row_id"]}, apart from import row ID.'))
write_csv('chapters/ch07/sales_dirty_source.csv',dirty)
write_csv('chapters/ch07/products.csv',products)
write_csv('reference/defect_ledger.csv',defects)
quarantine_ids={dirty[i]['source_row_id'] for i in [10,12,14]}|{'SRC0201','SRC0202'}
accepted=[dict(x) for x in clean if x['source_row_id'] not in quarantine_ids]
for x in accepted:
    if x['source_row_id']=='SRC0017':x['customer_id']=''
write_csv('solutions/ch07/accepted.csv',accepted)
write_csv('solutions/ch07/quarantine.csv',[r for r in dirty if r['source_row_id'] in quarantine_ids])
write_csv('checkpoints/ch07/accepted.csv',accepted)
write_text('chapters/ch07/source_notes.md','''# Controlled cleaning exercise source
This CSV is the source for the planned sales_dirty.xlsx, which is not yet authored. Keep the raw file unchanged. Dates use ISO YYYY-MM-DD or explicitly documented DD/MM/YYYY. Blank customer IDs are legitimate guests. Category mapping is supplied in products.csv. Source row IDs identify imported rows; order_item_id identifies a business sale line. Duplicate imports may be quarantined only after comparing the business key and full record.

Blank prices, unapproved quantities, and unknown product keys must be quarantined, not guessed. There is no authority in this learner pack to recover them from the full database. The author-only defect ledger retains canonical truth for verification.

Starting file: sales_dirty_source.csv. Save outputs as accepted.csv, quarantine.csv and cleaning_log.csv. Pass: 202 = 197 accepted + 3 unresolved original rows + 2 duplicate imports. Blank customer IDs stay blank. Accepted total must match the answer ledger. Full XLSX starting file and UI walkthrough remain pending.
''')
write_csv('chapters/ch07/cleaning_log_template.csv',[],['source_row_id','field','observed_issue','decision','evidence','old_value','new_value'])

# Join exercise has isolated temporary cases; canonical foreign keys remain valid.
join_sql='''-- CH18: Run after core/retail_database_setup.sql, using the edition schema.
-- E01: Compare line count and sales before/after enriching completed lines with products.
-- E02: LEFT JOIN the temporary audit input; list unmatched keys.
-- E03: Run the intentionally faulty query. Record row count and inflated sales.
-- E04: Aggregate return events by sale line, LEFT JOIN, and reconcile again.
-- Save as validated_joins.sql. Compare solutions/ch18 and join_control_totals.csv.
CREATE TEMP TABLE join_sales (line_id TEXT PRIMARY KEY, product_id TEXT, sales_paise INTEGER);
INSERT INTO join_sales VALUES ('J1','P001',100000),('J2','P002',200000),('J3','P003',50000);
CREATE TEMP TABLE join_returns (return_id TEXT PRIMARY KEY,line_id TEXT,refund_paise INTEGER);
INSERT INTO join_returns VALUES ('JR1','J1',20000),('JR2','J1',30000),('JR3','J3',10000);
CREATE TEMP TABLE audit_input (line_id TEXT PRIMARY KEY,product_id TEXT);
INSERT INTO audit_input VALUES ('A1','P001'),('A2','P999'),('A3',NULL);
-- Intentionally faulty: one sales amount is counted once per return event.
SELECT COUNT(*) AS joined_rows,SUM(s.sales_paise) AS sales_paise,
       SUM(r.refund_paise) AS refund_paise
FROM join_sales s LEFT JOIN join_returns r ON r.line_id=s.line_id;
'''
write_text('chapters/ch18/join_cases.sql',join_sql)
solution='''-- Run join_cases.sql in this same session first. No DISTINCT used to hide duplication.
-- E01: Many completed lines to one unique product.
SELECT COUNT(*) AS sale_lines, SUM(i.quantity*i.unit_price_paise-i.discount_paise) AS sales_paise
FROM order_items i JOIN orders o ON o.order_id=i.order_id WHERE o.status='Completed';
SELECT COUNT(*) AS sale_lines, SUM(i.quantity*i.unit_price_paise-i.discount_paise) AS sales_paise
FROM order_items i JOIN orders o ON o.order_id=i.order_id
JOIN products p ON p.product_id=i.product_id WHERE o.status='Completed';
-- E02: One missing identifier and one unknown identifier, separately visible.
SELECT a.line_id,a.product_id,
 CASE WHEN a.product_id IS NULL THEN 'Missing identifier' ELSE 'Unknown identifier' END AS issue
FROM audit_input a LEFT JOIN products p ON p.product_id=a.product_id
WHERE p.product_id IS NULL ORDER BY a.line_id;
-- E04: One row per sale line after pre-aggregation; all three sales survive.
WITH return_totals AS (
 SELECT line_id,SUM(refund_paise) AS refund_paise FROM join_returns GROUP BY line_id
)
SELECT COUNT(*) AS joined_rows,SUM(s.sales_paise) AS sales_paise,
       SUM(COALESCE(r.refund_paise,0)) AS refund_paise
FROM join_sales s LEFT JOIN return_totals r ON r.line_id=s.line_id;
'''
write_text('solutions/ch18/validated_joins.sql',solution)
write_csv('chapters/ch18/join_control_totals.csv',[
    dict(case='base',row_count=3,sales_paise=350000,refund_paise=60000),
    dict(case='faulty_left_join',row_count=4,sales_paise=450000,refund_paise=60000),
    dict(case='corrected_left_join',row_count=3,sales_paise=350000,refund_paise=60000)])
write_text('solutions/ch18/explanation.md','''# Why the totals change
J1 has two return events. Joining events directly repeats its 100,000 paise sale, adding INR 1,000 to the apparent revenue. Four joined rows do not mean four sales. Aggregating returns by line first restores three rows, INR 3,500 sales and INR 600 refunds. A LEFT JOIN retains J2 even though it has no return. This fixture demonstrates one-to-many multiplication; joining two repeated event tables would create a many-to-many multiplication risk.
E01 uses completed core sales only; enrichment must preserve count and amount. E02 returns A2 (unknown key) and A3 (missing key). The canonical core has no unmatched product keys.
''')
write_text('checkpoints/ch18/restart.md','''# Restart Chapter 18
Use a fresh session against the unchanged core database, then execute chapters/ch18/join_cases.sql. Temporary fixtures are session-local; closing the session removes them. Do not rerun their CREATE statements in the same session. PostgreSQL execution of these files remains pending in this foundation release. The numeric cases were executed in SQLite for independent validation.
''')
write_csv('chapters/ch15/import_sample.csv',products[:6])

# Known append-only batch: completely separate from the frozen core.
refresh_order=dict(order_id='O2026-B0001',order_date='2026-02-01',customer_id=None,location_id='WEB',status='Completed')
refresh_item=dict(order_item_id='L2026-B000001',order_id=refresh_order['order_id'],product_id='P001',quantity=2,unit_price_paise=18000,discount_paise=3600,unit_cost_paise=10800)
write_csv('chapters/ch26/refresh_pack/orders.csv',[refresh_order]);write_csv('chapters/ch26/refresh_pack/order_items.csv',[refresh_item])
write_csv('chapters/ch26/refresh_pack/expected_delta.csv',[dict(order_count=1,line_count=1,gross_sales_paise=36000,discount_paise=3600,sales_after_discount_paise=32400,refunds_paise=0,sale_cost_paise=21600,gross_profit_paise=10800)])
write_text('chapters/ch26/refresh_pack/README.md','''# Controlled refresh source
Append these two files once to separate copies of orders and order_items. Do not append to the canonical files. The new order and line IDs must not already exist. Rebuild completed sales from the changed source, then refresh the consuming report. Reapplying the batch must be rejected as duplicate keys. February 2026 is a new-sale period; January 2026 stays the return-only test period. This relational batch is preparation for the later XLSX/PBIX refresh pack, not a tested native report refresh.
''')

SCHEMA = '''CREATE TABLE products(product_id TEXT PRIMARY KEY,product_name TEXT NOT NULL,category TEXT NOT NULL,active INTEGER NOT NULL CHECK(active IN(0,1)));
CREATE TABLE customers(customer_id TEXT PRIMARY KEY,enrollment_date DATE NOT NULL,segment TEXT NOT NULL);
CREATE TABLE locations(location_id TEXT PRIMARY KEY,location_name TEXT NOT NULL,channel TEXT NOT NULL CHECK(channel IN('Store','Online')));
CREATE TABLE orders(order_id TEXT PRIMARY KEY,order_date DATE NOT NULL,customer_id TEXT REFERENCES customers(customer_id),location_id TEXT NOT NULL REFERENCES locations(location_id),status TEXT NOT NULL CHECK(status IN('Completed','Cancelled')));
CREATE TABLE order_items(order_item_id TEXT PRIMARY KEY,order_id TEXT NOT NULL REFERENCES orders(order_id),product_id TEXT NOT NULL REFERENCES products(product_id),quantity INTEGER NOT NULL CHECK(quantity>0),unit_price_paise BIGINT NOT NULL CHECK(unit_price_paise>=0),discount_paise BIGINT NOT NULL CHECK(discount_paise>=0 AND discount_paise<=quantity*unit_price_paise),unit_cost_paise BIGINT NOT NULL CHECK(unit_cost_paise>=0));
CREATE TABLE returns(return_id TEXT PRIMARY KEY,order_item_id TEXT NOT NULL REFERENCES order_items(order_item_id),return_date DATE NOT NULL,returned_quantity INTEGER NOT NULL CHECK(returned_quantity>0),refund_paise BIGINT NOT NULL CHECK(refund_paise>=0),reason TEXT NOT NULL CHECK(reason IN('Changed mind','Damaged','Wrong item')),recovered_cost_paise BIGINT NOT NULL CHECK(recovered_cost_paise>=0));
CREATE TABLE inventory(snapshot_date DATE NOT NULL,location_id TEXT NOT NULL REFERENCES locations(location_id),product_id TEXT NOT NULL REFERENCES products(product_id),stock_quantity INTEGER NOT NULL CHECK(stock_quantity>=0),PRIMARY KEY(snapshot_date,location_id,product_id));
CREATE TABLE targets(month_start DATE NOT NULL,location_id TEXT NOT NULL REFERENCES locations(location_id),net_sales_target_paise BIGINT NOT NULL,gross_profit_target_paise BIGINT NOT NULL,PRIMARY KEY(month_start,location_id));
CREATE TABLE calendar(calendar_date DATE PRIMARY KEY,year INTEGER NOT NULL,month INTEGER NOT NULL,month_start DATE NOT NULL,quarter INTEGER NOT NULL,iso_weekday INTEGER NOT NULL);
CREATE TABLE historical_monthly_summary(month_start DATE NOT NULL,location_id TEXT NOT NULL REFERENCES locations(location_id),category TEXT NOT NULL,gross_sales_paise BIGINT NOT NULL,discount_paise BIGINT NOT NULL,sales_after_discount_paise BIGINT NOT NULL,refunds_paise BIGINT NOT NULL,sale_cost_paise BIGINT NOT NULL,recovered_cost_paise BIGINT NOT NULL,PRIMARY KEY(month_start,location_id,category));
'''
def lit(v):
    if v is None:return 'NULL'
    if isinstance(v,int):return str(v)
    return "'"+v.replace("'","''")+"'"
sql=['-- Generated original synthetic data. PostgreSQL script: native execution PENDING.\nBEGIN;\nCREATE SCHEMA dafz_v01;\nSET search_path TO dafz_v01;\n',SCHEMA]
for name,rows in tables.items():
    for offset in range(0,len(rows),250):
        chunk=rows[offset:offset+250]
        sql.append(f'INSERT INTO {name} ({",".join(chunk[0])}) VALUES\n'+',\n'.join('('+','.join(lit(v) for v in row.values())+')' for row in chunk)+';\n')
sql.append('COMMIT;\n')
write_text('core/retail_database_setup.sql',''.join(sql))
write_text('reference/validation_schema.sql',SCHEMA)
write_text('reference/sql_setup.md','''# Database implementation status
Teaching dialect: PostgreSQL, as specified in the blueprint. core/retail_database_setup.sql creates schema dafz_v01 in a database chosen by the reader, loads all ten canonical tables, and commits atomically. It contains no DROP statements. Use a dedicated empty training database. Existing schema dafz_v01 causes failure instead of silent overwrite. In later sessions set search_path TO dafz_v01 before querying. Installation, permissions and interface instructions must be verified before publication.

Native PostgreSQL execution has NOT been tested in this environment. Independent SQL validation uses Python's bundled SQLite on the exact integer-paise CSV contents. That validates the tested arithmetic and relationships, not PostgreSQL installation or dialect compatibility. reference/validation.sqlite is an author QA artifact, not a substitute for the planned PostgreSQL training environment.
''')
write_text('reference/metric_rules.md','''# Metric rules, version 0.1.0
All businesses, records, identifiers, amounts and outcomes are fictional and generated specifically for this project. No real customer names, contacts, or addresses are included. Retailer naming remains undecided.

## Units and rounding
Canonical money columns end in _paise and contain integer paise: INR 1 = 100 paise. Convert to INR by dividing by 100.0, not by relabeling the column. CSV files are UTF-8 with headers, comma delimiters, ISO dates and empty fields for nulls. There are no thousands separators. INR teaching exports have exactly two decimal places. Reconcile canonical money exactly (tolerance 0 paise); after conversion to INR compare rounded values to two decimals. Calculated percentages use the full ratio, displayed to two decimal percentage points. Half-up applies when generating target paise. Do not sum rounded margin percentages.

## Eligibility and grain
Orders have one row per order; order_items one row per line; returns one row per return event. Only Completed orders contribute sales, sold quantity, order counts and sale costs. Cancelled orders and their lines are retained for status exercises but contribute zero recognized sales/cost. Customer null means guest or unidentified, not a failed numeric conversion. No anonymous identity is inferred. Missing product/location keys are forbidden in core.

Gross sales = SUM(quantity × unit_price_paise) on eligible sale lines.
Discount = SUM(discount_paise), a LINE total, not a per-unit amount.
Sales after discount = gross sales − discount.
Refunds = SUM(refund_paise) by return event date.
Net sales = eligible sales after discount posted in the period − refunds posted in the period.
Sale cost = SUM(quantity × transaction-time unit_cost_paise).
Net COGS = sale cost − recovered inventory cost posted on return dates.
Gross profit = net sales − net COGS.
Gross margin = gross profit / net sales only when net sales > 0; otherwise undefined/blank, with the amounts still shown.
Basic sales AOV = sales after discount / distinct completed orders in the sale period. Under product/category filters, count distinct orders containing eligible lines in the selected slice. Slice order counts are not additive across categories. With no completed orders AOV is undefined, including a return-only period.
Return-adjusted cohort AOV = (sales after discount for chosen original orders − their refunds up to an explicit as-of date) / distinct chosen completed orders. Never label event-period net sales divided by new orders as basic sales AOV.

## Returns and reporting cutoff
Each event references its original line. Per-unit discounted selling price is (quantity × unit price − discount) / quantity. Generation ensures this is an integer number of paise. Partial refund = returned quantity × that original discounted unit price. Cumulative returns cannot exceed sold quantity or line sales. Recovered cost is explicitly recorded: damaged goods recover zero, other modeled returns recover their original unit cost. This simplified policy is fictional, not a claim about real accounting practice.
Core sale dates: 2025-01-01 through 2025-12-31. Core event cutoff: 2026-01-31. Thus late returns are available for cohort analysis but excluded from 2025 event-period totals. January 2026 is a return-only period in this frozen dataset. Calendar extends through 2026 for the future quarter and refresh exercises; future calendar rows are not sales records. Returns are attributed to the original sale location/product, not a separately modeled processing location. No pre-2025-origin returns enter 2025: the simulation explicitly excludes opening return obligations. The 2024 comparator also excludes opening obligations and includes only events posted in 2024.

## Comparison, targets and scope
2024 summary is a separate seeded synthetic scenario aggregated to month-location-category, with matching currency and metric definitions. No 2024 customer-level inference is supported by the distributed summary. Targets are 110% of prior-year net sales and 108% of prior-year gross profit per month-location, rounded half-up to one paise. Targets have no category breakdown. Never multiply monthly targets by joining them to sale lines.
Inventory snapshots are end-of-month point-in-time values; do not sum them across months or infer lost sales from a zero stock observation. Snapshot movements are not a modeled stock ledger.
All sale values exclude tax. Shipping, payroll, rent, and other operating expenses are absent. Gross profit is available; net profit is not.
Discount depth and product mix vary by scenario. These are deliberately designed teaching patterns. Observed associations do not establish promotional causation or forecast real performance.
''')

# Complete field-level dictionary from explicit schema conventions.
descriptions={
 'product_id':'Unique product identifier; FK where repeated', 'product_name':'Approved product label', 'category':'One of five approved categories', 'active':'1 active, 0 inactive',
 'customer_id':'Synthetic customer identifier; null allowed only on orders / derived sales', 'enrollment_date':'Customer enrollment date', 'segment':'Broad synthetic segment',
 'location_id':'Reporting location: six stores or WEB', 'location_name':'Human-readable location label', 'channel':'Store or Online',
 'order_id':'Unique order identifier; FK on order_items', 'order_date':'Sale/posting date if Completed', 'status':'Completed or Cancelled',
 'order_item_id':'Unique sale line identifier; FK on returns', 'quantity':'Positive units on sale line', 'unit_price_paise':'Pre-discount unit selling price, paise',
 'discount_paise':'Total discount on the entire line or aggregate, paise', 'unit_cost_paise':'Original transaction-time cost per unit, paise',
 'return_id':'Unique return-event identifier', 'return_date':'Refund/recovery posting date', 'returned_quantity':'Positive returned units for this event',
 'refund_paise':'Refund for this event, paise', 'reason':'Changed mind, Damaged, or Wrong item', 'recovered_cost_paise':'Inventory cost recovered, paise',
 'snapshot_date':'End-of-month inventory snapshot date', 'stock_quantity':'Nonnegative units in this snapshot only',
 'month_start':'First date of reporting month', 'net_sales_target_paise':'Month-location net-sales target, paise', 'gross_profit_target_paise':'Month-location gross-profit target, paise',
 'calendar_date':'Unique continuous calendar date', 'year':'Calendar year', 'month':'Month number 1–12','quarter':'Quarter 1–4','iso_weekday':'Monday=1 through Sunday=7',
 'gross_sales_paise':'Eligible pre-discount sales, paise','sales_after_discount_paise':'Eligible sales less discounts, before refunds, paise','refunds_paise':'Refund events posted in month, paise','sale_cost_paise':'Original cost on eligible sales, paise'}
dictionary=[]
for table,rows in tables.items():
    for key in rows[0]:
        value=next((r[key] for r in rows if r[key] is not None),None)
        dictionary.append(dict(table=table,field=key,type='integer' if isinstance(value,int) else ('ISO date' if key.endswith('date') or key=='month_start' else 'text'),nullable='yes' if table=='orders' and key=='customer_id' else 'no',meaning=descriptions[key]))
write_csv('reference/data_dictionary.csv',dictionary)
write_text('reference/schema_dictionary.md','''# Schema and relationships
See data_dictionary.csv for every field, and metric_rules.md for units and financial definitions.

|Table|Grain / unique key|
|---|---|
|products|One product / product_id|
|customers|One customer / customer_id|
|locations|One reporting location-channel member / location_id|
|orders|One order / order_id|
|order_items|One sale line / order_item_id|
|returns|One return event / return_id|
|inventory|One snapshot-date/location/product combination|
|targets|One month/location combination|
|calendar|One date / calendar_date|
|historical_monthly_summary|One 2024 month/location/category combination|

orders → order_items is one-to-many; products → order_items is one-to-many; order_items → returns is one-to-many. Customers may be null on orders. Every other foreign key must match. For Power BI use separate derived sales and returns facts with shared dimensions; do not directly relate the two facts many-to-many. Use sale_date for sales and return_date for returns, with separate role-playing dates or explicit cohort logic when needed. Monthly targets require separate monthly-grain modeling; suppress unsupported category breakdowns.
''')
write_text('reference/environment_matrix.md','''# Execution status
Python standard-library generator: executed, exact integer paise.
SQLite independent validation: see generated validation_report.md and validation_checks.csv.
PostgreSQL native setup and query execution: NOT TESTED; executable setup supplied for later verification.
Microsoft Excel desktop, formulas and PivotTables: NOT TESTED; chapter XLSX files pending.
Power BI Desktop, Power Query, DAX and refresh: NOT TESTED; PBIX files pending.
Software platform/version/licensing instructions: NOT YET VERIFIED against official documentation.
GitHub contents, write access, release upload and anonymous downloads: NOT VERIFIED in this milestone.

Publication requires actual application execution records with version, platform, input revision, steps and results. Script inspection or SQLite execution is not evidence of PostgreSQL, Excel or Power BI execution. No paid-sharing requirement is introduced by the dataset.
''')
write_text('reference/provenance.md',f'''# Provenance
Dataset version: {VERSION}. Seed: {SEED}. Generation date: 12 October 2026.
All source records were generated from newly written code for DATA ANALYTICS FROM ZERO by Abhishek Dhingia. No other book or external dataset supplied records, exercise prose, or solutions. Standard analytics concepts and SQL syntax are shared knowledge; universal uniqueness is not claimed.
2025 seed = base + 2025. The 2024 scenario uses base + 2024 and 10,800 generated orders. Its monthly summary is the learner-facing comparator; reference/build_inputs retains the transaction sources solely as author QA evidence. Runtime details are recorded in validation_report.md. Python Random algorithms are deterministic for the recorded runtime; the published CSV bytes and their hashes remain the authoritative frozen inputs. Rebuilding in another runtime must be compared to the manifest.
Originality is a production requirement. Final retailer name remains undecided. This package is a data foundation, not the manuscript, native workbook/report release, or full chapter practice bundle.
''')
write_text('README.md','''# DATA ANALYTICS FROM ZERO — Original data foundation v0.1.0
Author: Abhishek Dhingia. All records and business results are fictional.

## Start here
Read reference/validation_report.md for executed checks and exact totals. Read reference/metric_rules.md before using financial figures. Monetary columns ending _paise are integer paise; divide by 100 for INR. Open chapters/ch01/assignment_brief.md for the first 12-row exercise or chapters/ch18/join_cases.sql for the join fixture.

## Included
Ten canonical CSV tables; two derived fact exports; reproducible original generator; PostgreSQL schema/data setup; field dictionary; metric rules; validation code and executed report; control totals; defect ledger; partial answer ledger; first-assignment, table-grain, cleaning-source and join teaching samples; a controlled refresh batch; solutions and restart sources for the implemented samples.

## Rebuild and validate
From this folder run `python3 scripts/build_data.py` then `python3 scripts/validate_data.py`. These commands replace generated files within this edition folder, so rebuild a COPY if preserving the distributed version. They use only Python's standard library. They do not access the internet, modify an external database or upload to GitHub. Review scripts before running. The validation database is a SQLite author QA artifact; it is not the PostgreSQL learner database. For PostgreSQL use core/retail_database_setup.sql in a dedicated training database after native verification.

## Release status
This is the first data-foundation milestone. Chapter XLSX/PBIX deliverables, all remaining chapter exercises and answer keys, the Q1 2026 capstone, the independent service-desk dataset, application walkthroughs, GitHub release and the book remain to be produced. No claim of native Excel/PostgreSQL/Power BI testing is made. The 2026 calendar is provided but does not imply the capstone data exists. The full book PDF requires author review; Kindle preparation follows approval.

This author review archive is not a replacement for the book's promised adjacent direct-download links. Published exercise links will be created only after resources have been uploaded, pinned and anonymously tested.
''')
write_text('projects/README.md','''# Planned next project datasets
The quarterly-review dataset (January–March 2026) and independent service-desk dataset are pending. Do not use the controlled February refresh batch as a complete quarterly-review dataset. Their briefs, full input packs, defects, controls and separate solutions must be built and verified against Chapters 28–29 before drafting those walkthroughs.
''')
write_text('reference/chapter_coverage.md','''# Coverage at data-foundation milestone 0.1.0
CH01: CSV start, brief, computed solutions and restart source implemented.
CH03: relational sample CSVs implemented; dictionary template and issue exercise pending.
CH07: controlled dirty CSV source, source notes, defect ledger, accepted/quarantine solutions and restart source implemented. Planned XLSX presentation and full lesson pending.
CH15: product import sample and PostgreSQL setup supplied. Native database execution and UI setup pending.
CH18: isolated join fixtures, solution queries, controls and restart instructions implemented. SQLite numeric checks executed; native PostgreSQL execution pending.
CH26: relational append batch and expected deltas implemented; actual native report refresh pending.
All other chapter-specific starters, checkpoints, solutions and UI walkthroughs are pending. Core tables support subsequent work but are not proof that those chapters are complete. Answer ledger covers implemented numeric cases only.
''')
print(json.dumps({'version':VERSION,'counts':{k:len(v) for k,v in tables.items()},'core_return_max':max(r['return_date'] for r in returns)}))
