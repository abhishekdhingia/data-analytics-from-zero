import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const OUT=process.env.DAFZ_OUTPUT_DIR||fileURLToPath(new URL('..',import.meta.url));
const D=JSON.parse(await fs.readFile(path.join(OUT,'reference/source_data.json'),'utf8'));
const C=D.controls,N=D.sales.length,END=N+6,qa=path.join(os.tmpdir(),'dafz_excel_qa');
await fs.mkdir(qa,{recursive:true});
const money='"INR "#,##0.00;[Red]("INR "#,##0.00)';
const dateSerial=s=>Math.round((Date.parse(s+'T00:00:00Z')-Date.UTC(1899,11,30))/86400000);
const col=n=>{let s='';for(n++;n>0;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const log=[];
function assert(name,a,b,tol=0.000001){let ok=typeof a==='number'&&typeof b==='number'?Math.abs(a-b)<=tol:a===b;log.push({test:name,actual:a,expected:b,status:ok?'PASS':'FAIL',engine:'Artifact Tool'});if(!ok)throw Error(`${name}: ${a} != ${b}`);}
function title(s,t,note){s.showGridLines=false;s.getRange('A1:T35').format.font={name:'Arial',size:10,color:'#182738'};s.getRange('A2').values=[[t]];s.getRange('A2').format.font={name:'Arial',size:15,bold:true,color:'#182738'};if(note){s.getRange('A4').values=[[note]];s.getRange('A4').format.font={name:'Arial',size:10,italic:true,color:'#526378'};}}
function grid(s,headers,rows,{table=false,name='DataTable',row=6,widths=[]}={}){
 const end=row+rows.length,k=headers.length,last=col(k-1);
 s.getRange(`A${row}:${last}${end}`).values=[headers,...rows];
 const area=s.getRange(`A${row}:${last}${Math.max(end,row+1)}`);
 area.format.font={name:'Arial',size:10,color:'#182738'};area.format.rowHeight=22;area.format.verticalAlignment='center';
 for(let i=0;i<k;i++)s.getRange(`${col(i)}${row}:${col(i)}${end}`).format.columnWidth=widths[i]||18;
 const h=s.getRange(`A${row}:${last}${row}`);h.format={fill:'#243B53',font:{name:'Arial',size:10,color:'#FFFFFF',bold:true},wrapText:true,rowHeight:34,horizontalAlignment:'center',verticalAlignment:'center'};
 if(table){const t=s.tables.add(`A${row}:${last}${end}`,true,name);t.style='TableStyleMedium2';}
 s.freezePanes.freezeRows(row);return end;
}
function guide(w,ch,mode,rows){const s=w.worksheets.add('Guide');title(s,`Chapter ${ch} — ${mode}`,'All business data is fictional. Amounts are INR, excluding tax.');grid(s,['Exercise','Task','Save as / check'],rows,{widths:[16,74,65]});s.getRange(`B7:C${6+rows.length}`).format.wrapText=true;s.getRange(`A7:C${6+rows.length}`).format.rowHeight=50;return s;}
const headers=['Line ID','Order ID','Sale date','Location','Product ID','Product','Category','Units','Unit price','Line discount','Unit cost','Gross sales','Sales after discount'];
function sales(w,{table=true,calculate=false,blank=false,lookup=false,sol=false,orderFlag=false,extra=false}={}){
 let rows=D.sales.map(r=>r.map((v,i)=>i===2?dateSerial(v):v));
 if(blank)rows=rows.map(r=>r.map((v,i)=>i>=11?null:v));
 if(lookup){rows=rows.map(r=>r.map((v,i)=>[5,6].includes(i)?null:v));rows[0][4]='P999';rows[1][4]=Number(rows[1][4].slice(1));rows=rows.map(r=>[...r,null,null,null,null]);}
 if(orderFlag)rows=rows.map(r=>[...r,null]);if(extra)rows=rows.map(r=>[...r,null,null]);
 const s=w.worksheets.items.find(x=>x.name==='Sales')||w.worksheets.add('Sales');title(s,'Sales sample — 2025',`${N} completed sale lines from 72 selected orders. Sales exclude refunds; sample is not the annual total.`);
 const hh=lookup?[...headers,'Normalized key','Key matches','Lookup status','Fallback category']:orderFlag?[...headers,'First order line']:extra?[...headers,'Extra discount','After extra discount']:headers;
 grid(s,hh,rows,{table,name:'SalesData',widths:[22,21,16,14,16,24,20,12,19,19,19,21,24,22,24,21,22]});
 s.getRange(`C7:C${END}`).setNumberFormat('yyyy-mm-dd');s.getRange(`H7:H${END}`).setNumberFormat('0');s.getRange(`I7:M${END}`).setNumberFormat(money);
 if(calculate){s.getRange('L7').formulas=[['=ROUND(H7*I7,2)']];s.getRange(`L7:L${END}`).fillDown();s.getRange('M7').formulas=[['=L7-J7']];s.getRange(`M7:M${END}`).fillDown();}
 if(blank)s.getRange(`L7:M${END}`).format.fill='#FFF2CD';
 if(orderFlag){s.getRange('N7').formulas=[['=IF(COUNTIFS($B$7:B7,B7)=1,1,0)']];s.getRange(`N7:N${END}`).fillDown();}
 if(extra){s.getRange(`N7:O${END}`).setNumberFormat(money);if(sol){s.getRange('N7:O7').formulas=[['=ROUND(M7*Calculations!$E$7,2)','=M7-N7']];s.getRange(`N7:O${END}`).fillDown();}else s.getRange(`N7:O${END}`).format.fill='#FFF2CD';}
 if(lookup&&sol){
   s.getRange('N7:Q7').formulas=[['=IF(ISNUMBER(E7),"P"&TEXT(E7,"000"),TRIM(E7))',`=COUNTIFS(Products!$A$7:$A$66,N7)`,'=IF(O7=0,"Unmatched",IF(O7>1,"Ambiguous","Matched"))','=IF(O7<>1,P7,INDEX(Products!$C$7:$C$66,MATCH(N7,Products!$A$7:$A$66,0)))']];s.getRange(`N7:Q${END}`).fillDown();
   s.getRange('F7:G7').formulas=[['=IF(O7<>1,P7,_xlfn.XLOOKUP(N7,Products!$A$7:$A$66,Products!$B$7:$B$66,"Unmatched",0))','=IF(O7<>1,P7,_xlfn.XLOOKUP(N7,Products!$A$7:$A$66,Products!$C$7:$C$66,"Unmatched",0))']];s.getRange(`F7:G${END}`).fillDown();
 }
 return s;
}
function products(w){const s=w.worksheets.add('Products');title(s,'Product master','60 unique product keys. Historical unit cost stays on the sale line.');grid(s,['Product ID','Product','Category','Active'],D.products,{table:true,name:'ProductMaster',widths:[18,27,24,14]});return s;}
function summary(w,name='Reference summaries'){
 const s=w.worksheets.add(name);title(s,'Sales reference totals — 2025 sample','Formula-based reference. Build native PivotTables separately using the chapter guide.');
 const cats=Object.keys(C.categories),locs=Object.keys(C.stores);
 grid(s,['Location',...cats,'All categories'],locs.map(x=>[x,...Array(6).fill(null)]),{widths:[18,22,22,22,22,22,22]});
 for(let r=7;r<14;r++){for(let k=1;k<6;k++)s.getRange(`${col(k)}${r}`).formulas=[[`=SUMIFS(Sales!$M$7:$M$${END},Sales!$D$7:$D$${END},$A${r},Sales!$G$7:$G$${END},${col(k)}$6)`]];s.getRange(`G${r}`).formulas=[[`=SUM(B${r}:F${r})`]];}
 s.getRange('A14').values=[['Grand total']];for(let k=1;k<=6;k++)s.getRange(`${col(k)}14`).formulas=[[`=SUM(${col(k)}7:${col(k)}13)`]];s.getRange('B7:G14').setNumberFormat(money);
 s.getRange('A18:B18').values=[['Month','Sales after discount']];s.getRange('A18:B18').format={fill:'#243B53',font:{color:'#FFFFFF',bold:true,size:10}};
 for(let m=1;m<=12;m++){const r=18+m;s.getRange(`A${r}`).values=[[new Date(Date.UTC(2025,m-1,1)).toLocaleString('en-GB',{month:'short',year:'numeric',timeZone:'UTC'})]];s.getRange(`B${r}`).formulas=[[`=SUMIFS(Sales!$M$7:$M$${END},Sales!$C$7:$C$${END},">="&DATE(2025,${m},1),Sales!$C$7:$C$${END},"<"&DATE(2025,${m+1},1))`]];}
 s.getRange('A31').values=[['Grand total']];s.getRange('B31').formulas=[['=SUM(B19:B30)']];s.getRange('B19:B31').setNumberFormat(money);
 s.getRange('I6:K6').values=[['Category','Units','Sales after discount']];s.getRange('I6:K6').format={fill:'#243B53',font:{color:'#FFFFFF',bold:true,size:10},wrapText:true,rowHeight:34};s.getRange('I6:K14').format.columnWidth=24;
 cats.forEach((x,i)=>{const r=i+7;s.getRange(`I${r}`).values=[[x]];s.getRange(`J${r}:K${r}`).formulas=[[`=SUMIFS(Sales!$H$7:$H$${END},Sales!$G$7:$G$${END},I${r})`,`=SUMIFS(Sales!$M$7:$M$${END},Sales!$G$7:$G$${END},I${r})`]];});s.getRange('K7:K11').setNumberFormat(money);return s;
}
function report(w,sol){const s=w.worksheets.items.find(x=>x.name==='Report')||w.worksheets.add('Report');title(s,'Sales report — selected 2025 orders','183 sale lines. INR, after discount, before refunds. This sample cannot establish annual performance.');s.getRange('A6:N40').format.columnWidth=13;s.getRange('A6:N40').format.rowHeight=23;
 if(!sol){s.getRange('A7').values=[['Create a monthly line chart and a ranked category bar chart.']];s.getRange('A9').values=[['Use Summary values. Add units, scope, three findings and one limitation.']];return s;}
 s.getRange('A6:B6').values=[['Metric','Value']];s.getRange('A7:A9').values=[['Sales after discount'],['Sale lines'],['Selected orders']];s.getRange('B7:B9').formulas=[['=SUM(Sales!M7:M'+END+')'],['=COUNTA(Sales!A7:A'+END+')'],['=SUM(Sales!N7:N'+END+')']];
 s.getRange('A6:A21').format.columnWidth=27;s.getRange('B6:B21').format.columnWidth=24;s.getRange('B7').setNumberFormat(money);s.getRange('B8:B9').setNumberFormat('0');
 s.getRange('A12:B12').values=[['Category','Sales after discount']];const cats=Object.entries(C.categories).sort((a,b)=>b[1]-a[1]).map(x=>x[0]);cats.forEach((cat,i)=>{let r=13+i;s.getRange(`A${r}`).values=[[cat]];s.getRange(`B${r}`).formulas=[[`=SUMIFS(Sales!$M$7:$M$${END},Sales!$G$7:$G$${END},A${r})`]];});s.getRange('B13:B17').setNumberFormat(money);
 const monthly=s.charts.add('line',w.worksheets.getItem('Summary').getRange('A18:B30'));monthly.title='Monthly sample sales (INR)';monthly.hasLegend=false;monthly.setPosition('D6','N21');monthly.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};monthly.yAxis={numberFormatCode:'#,##0',numberFormatSourceLinked:false};monthly.series.items[0].line={fill:'#2563A6',style:'solid',width:2};
 const rank=s.charts.add('bar',s.getRange('A12:B17'));rank.title='Category sample sales (INR)';rank.hasLegend=false;rank.setPosition('D23','N38');rank.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};rank.yAxis={numberFormatCode:'#,##0',numberFormatSourceLinked:false};rank.series.items[0].fill='#2563A6';
 for(const chart of [monthly,rank]){chart.titleTextStyle.typeface='Arial';chart.titleTextStyle.fontSize=13;}
 s.getRange('A20').values=[['Interpretation']];s.getRange('A22:B25').merge(true);s.getRange('A22').values=[['Electronics contributes the largest sales value in this sample.']];s.getRange('A23').values=[['December has the highest monthly sample sales.']];s.getRange('A24').values=[['Online is the largest location by sample sales value.']];s.getRange('A25').values=[['Selection is small and non-random. No annual or net-profit conclusion is justified.']];s.getRange('A22:B25').format.wrapText=true;s.getRange('A22:B25').format.rowHeight=48;
 s.getRange('A28:B30').merge(true);s.getRange('A28').values=[['Categories are sorted for the supplied sample. Re-sort after changes.']];s.getRange('A29').values=[['This report uses formula summaries. Native PivotTable-based report remains pending.']];s.getRange('A30').values=[['These summaries cover all source rows; worksheet filters do not change SUMIFS results.']];s.getRange('A28:B30').format.wrapText=true;s.getRange('A28:B30').format.rowHeight=44;
 return s;
}
async function save(w,ch,file,{checks=[],render=true}={}){
 w.recalculate();for(const [name,sheet,cell,expected] of checks)assert(`${file}: ${name}`,w.worksheets.getItem(sheet).getRange(cell).values[0][0],expected);
 const errs=await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Formula errors'});await fs.writeFile(`${qa}/${path.basename(file)}_errors.json`,errs.ndjson);
 const previewRows=[];
 for(let i=0;i<w.worksheets.items.length;i++){
   const s=w.worksheets.items[i];
   const inspected=await w.inspect({kind:'table',range:`'${s.name}'!A6:D10`,include:'values,formulas',tableMaxRows:5,tableMaxCols:4,maxChars:2000});
   previewRows.push({sheet:s.name,inspection:inspected.ndjson});
   if(render){let range=s.name==='Report'?'A1:N39':s.name==='Cleaning log'?'A1:F17':s.name==='Calculations'?'A1:E28':s.name==='Summary'?'A1:K32':s.name==='Guide'?'A1:C12':s.name==='Sales'?(ch===8?'A1:Q13':ch===6?'A1:O13':'A1:N13'):'A1:'+((s.name==='Raw'||s.name==='Working'||s.name==='Accepted'||s.name==='Quarantine')?'K':'D')+'13';
    const blob=await w.render({sheetName:s.name,range,scale:1.3,format:'png'});await fs.writeFile(`${qa}/${path.basename(file,'.xlsx')}_${s.name.replaceAll(' ','_')}.png`,new Uint8Array(await blob.arrayBuffer()));
   }
 }
 await fs.writeFile(`${qa}/${path.basename(file)}_inspect.json`,JSON.stringify(previewRows,null,2));
 const p=path.join(OUT,file);await fs.mkdir(path.dirname(p),{recursive:true});await (await SpreadsheetFile.exportXlsx(w)).save(p);
 console.log('EXPORTED',file);
}
const specs={
5:['excel_navigation_start.xlsx','sales_table.xlsx','table_checkpoint.xlsx'],6:['formulas_start.xlsx','sales_calculations.xlsx','formulas_checkpoint.xlsx'],7:['sales_dirty.xlsx','sales_cleaned.xlsx','cleaning_checkpoint.xlsx'],8:['lookups_start.xlsx','sales_enriched.xlsx','lookup_checkpoint.xlsx'],9:['pivots_start.xlsx','pivot_reference.xlsx','pivot_reference_checkpoint.xlsx'],10:['report_start.xlsx','excel_report_reference.xlsx','report_reference_checkpoint.xlsx']};
for(let ch=5;ch<=10;ch++){
 if(process.env.DAFZ_CHAPTERS&&!process.env.DAFZ_CHAPTERS.split(',').includes(String(ch)))continue;
 const tag=`ch${String(ch).padStart(2,'0')}`;
 for(const sol of [false,true]){
  const w=Workbook.create();const tests=[];const name=specs[ch][sol?1:0];
  if(ch===5){const s=sales(w,{table:sol});if(sol){s.getRange(`C7:C${END}`).setNumberFormat('dd mmm yyyy');tests.push(['sale value','Sales','M7',D.sales[0][12]]);}guide(w,ch,sol?'Worked solution':'Starting workbook',[
   ['CH05-E01',`Create an Excel table from Sales!A6:M${END}; name it SalesData.`,`${N} data rows; save as sales_table.xlsx`],
   ['CH05-E02','Format sale dates and INR amounts; preserve underlying values.','Dates remain sortable and amounts remain numeric.'],
   ['CH05-E03','Filter Location to S01 and Category to Electronics.','Clear filters after recording the visible count and amount.'],
   ['CH05-E04','Sort date newest to oldest, then restore oldest to newest.','Sort the whole table. Row count and total must not change.']]);}
  if(ch===6){const sum=w.worksheets.add('Calculations');title(sum,'Formula practice','Historical sales stay separate from the hypothetical additional discount.');
   const s=sales(w,{table:true,calculate:sol,blank:!sol,extra:true,sol});
   grid(sum,['Measure','Value'],[['Gross sales',null],['Line discounts',null],['Sales after discount',null],['S01 sales',null],['S01 line count',null],['Numeric unit-price cells',null],['Sale line IDs',null]],{widths:[34,24]});
   sum.getRange('D6:E10').values=[['Hypothetical extra discount',null],['Extra rate',0.05],['Base sales',null],['Extra discount',null],['Sales after extra discount',null]];sum.getRange('D6:D10').format.columnWidth=36;sum.getRange('E6:E10').format.columnWidth=23;sum.getRange('E7').format.fill='#FFF2CD';sum.getRange('E7').setNumberFormat('0.0%');sum.getRange('E8:E10').setNumberFormat(money);
   sum.getRange('A17:D20').values=[['Debug case','Numerator','Denominator','Your corrected result'],['Zero denominator',10,0,null],['Positive denominator',10,2,null],['Compare C25:C27 with D25:D27.',null,null,null]];sum.getRange('D17:D20').format.columnWidth=36;
   sum.getRange('C17:C27').format.columnWidth=24;sum.getRange('A17:D17').format.wrapText=true;sum.getRange('A17:D17').format.rowHeight=34;
   sum.getRange('A24:D27').values=[['Demo sales','Fixed rate','Wrong relative copy','Correct absolute copy'],[100,0.05,null,null],[200,null,null,null],[300,null,null,null]];sum.getRange('C24:D24').format.wrapText=true;sum.getRange('A24:D24').format.rowHeight=34;sum.getRange('B25').setNumberFormat('0.0%');sum.getRange('C25').formulas=[['=A25*B25']];sum.getRange('C25:C27').fillDown();if(sol){sum.getRange('D25').formulas=[['=A25*$B$25']];sum.getRange('D25:D27').fillDown();}
   if(sol){sum.getRange('B7:B13').formulas=[[`=SUM(Sales!L7:L${END})`],[`=SUM(Sales!J7:J${END})`],[`=SUM(Sales!M7:M${END})`],[`=SUMIFS(Sales!M7:M${END},Sales!D7:D${END},"S01")`],[`=COUNTIFS(Sales!D7:D${END},"S01")`],[`=COUNT(Sales!I7:I${END})`],[`=COUNTA(Sales!A7:A${END})`]];sum.getRange('E8:E10').formulas=[['=B9'],[`=SUM(Sales!N7:N${END})`],['=E8-E9']];sum.getRange('D18:D19').formulas=[['=IF(C18=0,"Undefined",B18/C18)'],['=IF(C19=0,"Undefined",B19/C19)']];tests.push(['gross','Calculations','B7',C.gross],['discount','Calculations','B8',C.discount],['sales','Calculations','B9',C.sales],['store','Calculations','B10',C.stores.S01],['count','Calculations','B13',N],['zero guard','Calculations','D18','Undefined'],['fixed reference','Calculations','D27',15]);
    w.recalculate();sum.getRange('E7').values=[[0]];assert('CH06 changing rate recalculates',sum.getRange('E10').values[0][0],C.sales);sum.getRange('E7').values=[[0.05]];
   }else{sum.getRange('B7:B13').format.fill='#FFF2CD';sum.getRange('D18:D19').format.fill='#FFF2CD';}
   sum.getRange('B7:B10').setNumberFormat(money);guide(w,ch,sol?'Worked solution':'Starting workbook',[
   ['CH06-E01','Fill Sales L and M: gross = units × price; sales = gross − line discount.','Complete Calculations B7:B9. Save as sales_calculations.xlsx.'],
   ['CH06-E02','Copy Sales N7:O7 down, fixing Calculations!$E$7. Sum the results in E8:E10.','Round each extra line discount to 2 decimals. Test 0%, then restore 5%.'],
   ['CH06-E03','Use SUMIFS, COUNTIFS, COUNT and COUNTA in B10:B13.','Counts refer to sale lines, not orders.'],
   ['CH06-E04','Guard division by zero in D18:D19. Explain why $E$7 is fixed.','Undefined is a meaningful outcome; do not replace with zero.']]);}
  if(ch===7){const hdr=['Source row ID','Line ID','Order date','Product ID','Category','Units','Unit price','Line discount','Customer ID'];const keys=['source_row_id','order_item_id','order_date','product_id','category','quantity','unit_price_inr','discount_inr','customer_id'];
   function cleaningSheet(n,rows,typed){const s=w.worksheets.add(n);title(s,n==='Raw'?'Original import — keep unchanged':n,typed?'Approved records; line amounts in INR.':'Source text is preserved, including intentional defects.');const rr=rows.map(r=>keys.map(k=>typed?(k==='order_date'?dateSerial(r[k]):['quantity','unit_price_inr','discount_inr'].includes(k)?Number(r[k]):r[k]||null):r[k]||null));grid(s,typed?[...hdr,'Sales after discount']:hdr,rr.map(r=>typed?[...r,null]:r),{table:true,name:n+'Data',widths:[20,23,19,18,23,13,19,20,20,25]});if(typed){const end=rows.length+6;s.getRange(`C7:C${end}`).setNumberFormat('yyyy-mm-dd');s.getRange(`G7:H${end}`).setNumberFormat(money);s.getRange('J7').formulas=[['=ROUND(F7*G7-H7,2)']];s.getRange(`J7:J${end}`).fillDown();s.getRange(`J7:J${end}`).setNumberFormat(money);}return s;}
   if(sol){cleaningSheet('Accepted',D.accepted,true);cleaningSheet('Quarantine',D.quarantine,false);const s=w.worksheets.add('Cleaning log');title(s,'Cleaning decisions','A blank customer ID is legitimate; missing price is unresolved.');grid(s,['Source row ID','Field','Before','After','Decision','Evidence'],D.defects.map(r=>[r.source_row_id,r.field,r.dirty_value||'(blank)',r.handling.includes('quarantine')?'Quarantined':r.handling==='retain'?'(blank retained)':r.canonical_value,r.handling,r.evidence]),{widths:[22,24,24,24,28,80]});s.getRange('F7:F16').format.wrapText=true;s.getRange('A7:F16').format.rowHeight=42;}
   else cleaningSheet('Working',D.dirty,false);
   cleaningSheet('Raw',D.dirty,false);products(w);guide(w,ch,sol?'Worked solution':'Starting workbook',[
   ['CH07-E01','Record the 202 raw rows. Profile values before calculating a total.','Raw sales total is unavailable while invalid inputs remain.'],
   ['CH07-E02','Trim spaces and map case variants with Products.','Preserve all legitimate business records.'],
   ['CH07-E03','Use DD/MM/YYYY for the slash-formatted date; ISO dates are YYYY-MM-DD.','Do not infer the convention from your computer locale.'],
   ['CH07-E04','Quarantine duplicate imports and unresolved price, quantity or product IDs.','197 accepted + 5 quarantined = 202. Keep guest IDs blank.'],
   ['CH07-E05','Calculate accepted sales; log every repair or quarantine decision.','Save as sales_cleaned.xlsx; compare the separate answer ledger.']]);
  }
  if(ch===8){products(w);const s=sales(w,{lookup:true,sol});const a=w.worksheets.add('Duplicate case');title(a,'Ambiguous master-key exercise','This isolated fixture is not the approved product master.');grid(a,['Product ID','Category','Key count','Decision'],[['P001','Kitchen',null,null],['P001','Electronics',null,null]],{widths:[22,24,20,30]});if(sol){a.getRange('C7:D7').formulas=[['=COUNTIFS($A$7:$A$8,A7)','=IF(C7>1,"Ambiguous","Unique")']];a.getRange('C7:D8').fillDown();tests.push(['unmatched','Sales','P7','Unmatched'],['numeric key normalized','Sales','N8',D.sales[1][4]],['ambiguous fixture','Duplicate case','D7','Ambiguous']);w.recalculate();for(let r=8;r<=END;r++)assert(`CH08 lookup ${r}`,s.getRange(`G${r}`).values[0][0],D.sales[r-7][6]);}
   guide(w,ch,sol?'Worked solution':'Starting workbook',[
   ['CH08-E01','Check Products keys are unique. Inspect Duplicate case separately.','Never accept an arbitrary first match for ambiguous keys.'],
   ['CH08-E02','Normalize E into N; count matches in O; return labels in F/G.','Use exact-match XLOOKUP; INDEX/MATCH fallback goes in Q.'],
   ['CH08-E03','Flag the unknown P999 in the first sale row.','Keep the row and amount; do not invent its category.'],
   ['CH08-E04','Supplier numeric codes map to P + three digits: 25 means P025.','Repair numeric E8 using this documented rule; keep K historical cost.']]);}
  if(ch===9){w.worksheets.add('Sales');if(sol)summary(w,'Summary');sales(w,{calculate:true,orderFlag:true});guide(w,ch,sol?'Reference answers — native PivotTables pending':'Starting workbook',[
   ['CH09-E01','Insert a PivotTable from SalesData: Location rows, Category columns, Sales after discount values.','Use SUM. Compare the formula-based reference workbook.'],
   ['CH09-E02','Create a monthly sales pivot; group Sale date by Years and Months.','All 12 months and the same grand total.'],
   ['CH09-E03','Create a category pivot with Sum of Units and Sum of Sales after discount.','Different units need separate labels.'],
   ['CH09-E04','In a copy, append refresh_test_row.csv to SalesData and refresh pivots.','Exactly +1 line and +INR 324 sales.'],
   ['CH09-E05','Compare 183 line rows with 72 unique Order IDs.','COUNT of lines is not an order count.']]);if(sol)tests.push(['matrix total','Summary','G14',C.sales],['monthly total','Summary','B31',C.sales]);}
  if(ch===10){w.worksheets.add('Report');w.worksheets.add('Sales');summary(w,'Summary');sales(w,{calculate:true,orderFlag:true});report(w,sol);guide(w,ch,sol?'Formula-based report reference':'Starting workbook',[
   ['CH10-E01','Create a monthly line chart and ranked category bar chart.','Use supplied Summary; native pivot-based variant remains pending.'],
   ['CH10-E02','State 2025 selected orders, INR, after discount and before refunds.','Do not label these sample figures annual net sales.'],
   ['CH10-E03','Write three numerical findings and one limitation.','Every number must trace to Sales or Summary.'],
   ['CH10-E04','Check chart ranges, totals, category order and readable labels.','Save as excel_business_report.xlsx. This reference summarizes all rows.']]);if(sol){tests.push(['report sales','Report','B7',C.sales],['report rows','Report','B8',N],['distinct orders','Report','B9',72]);w.recalculate();const src=w.worksheets.getItem('Sales');src.getRange('H7').values=[[D.sales[0][7]+1]];w.recalculate();assert('CH10 changed quantity reaches report',w.worksheets.getItem('Report').getRange('B7').values[0][0],C.sales+D.sales[0][8]);assert('CH10 changed quantity reaches monthly chart source',w.worksheets.getItem('Summary').getRange('B19').values[0][0],C.monthly['2025-01']+D.sales[0][8]);src.getRange('H7').values=[[D.sales[0][7]]];}}
  await save(w,ch,`${sol?'solutions':'chapters'}/${tag}/${name}`,{checks:tests});
  if(sol){const source=path.join(OUT,'solutions',tag,name),dest=path.join(OUT,'checkpoints',tag,specs[ch][2]);await fs.mkdir(path.dirname(dest),{recursive:true});await fs.copyFile(source,dest);}
 }
}
await fs.writeFile(path.join(OUT,'reference/artifact_checks.json'),JSON.stringify(log,null,2));
console.log('CHECKS',log.length,'all passed');
