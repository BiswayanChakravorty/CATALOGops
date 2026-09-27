import React, {useMemo, useRef, useState} from "react";
import {createRoot} from "react-dom/client";
import Papa from "papaparse";
import {Activity, ArrowDownToLine, ArrowUpFromLine, BadgeCheck, BarChart3, Check, ChevronDown, CircleAlert, FileSpreadsheet, FileText, Filter, Layers, Search, ShieldCheck, Sparkles, Upload, X} from "lucide-react";
import "./style.css";

const sample = [
 {SKU:"TS-001",Title:"Classic Cotton Tee - Black",Price:"599",Category:"T-shirts",Color:"Black",Size:"M"},
 {SKU:"TS-001",Title:"Classic Cotton Tee - Black",Price:"599",Category:"T-shirts",Color:"Black",Size:"L"},
 {SKU:"TS-003",Title:"Classic Cotton Tee Black",Price:"",Category:"T-shirts",Color:"Black",Size:"S"},
 {SKU:"HD-004",Title:"Oversized Hoodie - Grey",Price:"1499",Category:"Hoodies",Color:"Grey",Size:"L"},
 {SKU:"HD-005",Title:"Oversized Hoodie Grey",Price:"1499",Category:"",Color:"Grey",Size:"M"},
 {SKU:"MG-2001",Title:"Ceramic coffee mug",Price:"399",Category:"Home",Color:"White",Size:""},
 {SKU:"MG-2002",Title:"Ceramic coffee mug",Price:"399",Category:"Home",Color:"White",Size:""},
 {SKU:"BT-008",Title:"Steel Water Bottle 750ml",Price:"799",Category:"Drinkware",Color:"Blue",Size:""},
 {SKU:"",Title:"Premium Canvas Tote",Price:"499",Category:"Accessories",Color:"Natural",Size:""},
 {SKU:"BT-010",Title:"",Price:"699",Category:"Drinkware",Color:"Black",Size:""}
];
const norm=s=>String(s??"").trim().toLowerCase().replace(/[^a-z0-9]/g,"");
const aliases={sku:["sku","skuid","variantsku","productsku","itemsku"],title:["title","producttitle","name","productname"],price:["price","variantprice","saleprice","cost"],category:["category","productcategory","type"],variant:["variant","variants","option1value","size","color"]};
function mapping(headers){const out={};for(const [k,alts] of Object.entries(aliases)){out[k]=headers.find(h=>alts.includes(norm(h)))||null;}return out;}

// Root-cause explanations - ported directly from audit_engine.py (ROOT_CAUSE_EXPLANATIONS)
// so the web tool and the Python/report version stay in agreement.
const ROOT_CAUSE_EXPLANATIONS={
 duplicate_entries:"Duplicate SKUs usually mean the same product was created more than once — often because two systems (e.g. a POS and an online store) both generate product IDs independently, with nothing reconciling them.",
 missing_fields:"Missing required fields typically happen when a product is created quickly (a bulk import, a rushed listing) and the required-fields check for that channel isn't enforced at creation time — the gap only surfaces later, at the point of failed import or listing rejection.",
 title_inconsistency:"Repeated or near-identical titles usually mean the same product is maintained separately in more than one place (e.g. the online store and a marketplace feed) with no single source of truth — small edits drift apart over time.",
 invalid_price:"Invalid prices usually come from a bulk import or spreadsheet formula that produced text, a currency symbol, or a blank instead of a clean number — the source system didn't validate the value before export."
};
const ROOT_CAUSE_LABELS={duplicate_entries:"Duplicate Entries",missing_fields:"Missing Fields",title_inconsistency:"Title Inconsistency",invalid_price:"Invalid Price"};

function analyze(rows){
 const headers=Object.keys(rows[0]||{}), map=mapping(headers), findings=[];
 const add=(kind,row,detail,rootCause,severity="Review")=>findings.push({id:findings.length+1,kind,sku:map.sku?String(row[map.sku]||"").trim():"",row:row.__row,detail,severity,rootCause});
 const seen=new Map();
 rows.forEach((r,i)=>{r.__row=i+2;const sku=map.sku?String(r[map.sku]||"").trim():"";
  if(map.sku&&!sku)add("Missing SKU",r,"SKU is blank.","missing_fields");
  if(sku){if(seen.has(sku)){add("Duplicate SKU",r,"SKU appears more than once.","duplicate_entries");add("Duplicate SKU",rows[seen.get(sku)],"SKU appears more than once.","duplicate_entries");}else seen.set(sku,i);}
  for(const key of ["title","price","category"]){if(map[key]&&!String(r[map[key]]??"").trim())add("Missing "+key[0].toUpperCase()+key.slice(1),r,key+" is blank.","missing_fields");}
  if(map.price&&String(r[map.price]||"").trim()&&(!Number.isFinite(Number(String(r[map.price]).replace(/[$,₹£€]/g,"")))||Number(String(r[map.price]).replace(/[$,₹£€]/g,""))<0))add("Invalid price",r,"Price is not a valid non-negative number.","invalid_price");
 });
 if(map.title){const titles=new Map();rows.forEach(r=>{const t=String(r[map.title]||"").trim().toLowerCase().replace(/[^a-z0-9]+/g," ").trim();if(t){if(titles.has(t))add("Repeated title",r,"Exact normalized title is shared by another row.","title_inconsistency");else titles.set(t,r);}});}

 // Group findings into root causes - same grouping approach as group_by_root_cause() in audit_engine.py
 const rootCauses={};
 for(const f of findings){
   if(!f.rootCause) continue;
   if(!rootCauses[f.rootCause]) rootCauses[f.rootCause]={tag:f.rootCause,label:ROOT_CAUSE_LABELS[f.rootCause]||f.rootCause,explanation:ROOT_CAUSE_EXPLANATIONS[f.rootCause]||"Pattern identified across multiple findings.",findings:[]};
   rootCauses[f.rootCause].findings.push(f);
 }
 return {headers,map,findings,rootCauses:Object.values(rootCauses)};
}
function App(){
 const [rows,setRows]=useState(null),[filename,setFilename]=useState(""),[filter,setFilter]=useState("All issues"),[query,setQuery]=useState(""),[drag,setDrag]=useState(false);
 const input=useRef(null);
 const load=(file)=>{if(!file)return;setFilename(file.name);Papa.parse(file,{header:true,skipEmptyLines:"greedy",complete:r=>{const clean=r.data.filter(x=>Object.values(x).some(v=>String(v??"").trim()));setRows(clean);setFilter("All issues");},error:()=>alert("Could not read this file. Please upload a valid CSV.")});};
 const result=useMemo(()=>rows?.length?analyze(rows):null,[rows]);
 const demo=()=>{setRows(sample.map(x=>({...x})));setFilename("catalogops_sample.csv");setFilter("All issues");};
 const visible=(result?.findings||[]).filter(f=>(filter==="All issues"||f.kind===filter)&&(!query||[f.kind,f.sku,f.detail,String(f.row)].join(" ").toLowerCase().includes(query.toLowerCase())));
 const exportIssues=()=>{const csv=Papa.unparse(visible.map(({id,...x})=>x));const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));a.download="catalogops_findings.csv";a.click();URL.revokeObjectURL(a.href);};
 const exportReport=()=>window.print();
 return <div className="app">
  <aside className="sidebar"><div className="brand"><span className="brand-mark">C</span><span>CATALOG<span className="gold">ops</span><small>CATALOG INTELLIGENCE</small></span></div>
   <div className="nav-label">WORKSPACE</div><div className="nav-item active"><Layers size={17}/> Catalog audit</div><div className="nav-item"><Activity size={17}/> Findings & root causes</div><div className="nav-item"><FileText size={17}/> Audit reports</div>
   <div className="side-bottom"><div className="side-icon"><ShieldCheck size={18}/></div><b>Private by design</b><p>Files are analyzed in your browser in this MVP. Your catalog is not uploaded to a server.</p><span className="status"><i/> Local processing enabled</span></div>
  </aside>
  <main className="main">
   <header className="topbar"><div><span className="crumb">Workspace</span><span className="slash">/</span><b>Catalog audit</b></div><div className="top-right"><span className="pilot"><i/> MVP WORKSPACE</span><div className="avatar">CO</div></div></header>
   <section className="landing-hero">
    <div className="landing-announcement"><Sparkles size={14}/> CATALOGops · PRODUCT CATALOG QUALITY</div>
    <div className="landing-hero-grid">
      <div className="landing-copy">
        <div className="landing-kicker"><ShieldCheck size={15}/> CATALOG INTELLIGENCE FOR GROWING BRANDS</div>
        <h1>Make your product catalog <span>work better.</span></h1>
        <p>Find duplicate SKUs, missing product details, and inconsistent catalog data. Understand recurring issues and give your team a clearer path to review.</p>
        <div className="landing-ctas">
          <button className="btn landing-primary" onClick={()=>document.getElementById("audit-workspace")?.scrollIntoView({behavior:"smooth"})}>Start a free catalog audit <ArrowDownToLine size={16}/></button>
          <button className="btn landing-secondary" onClick={demo}>Explore sample results</button>
        </div>
        <div className="landing-trust"><span><Check size={14}/> Browser-based CSV analysis</span><span><Check size={14}/> No account required</span><span><Check size={14}/> Review before making changes</span></div>
      </div>
      <div className="landing-visual">
        <div className="landing-visual-label"><span className="visual-pulse"/> CATALOG AUDIT PREVIEW</div>
        <div className="landing-visual-title">One catalog. A clearer picture.</div>
        <div className="visual-stat-row"><div><small>Sample rows</small><b>1,240</b></div><div><small>Review flags</small><b className="visual-warn">38</b></div></div>
        <div className="visual-bars"><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/></div>
        <div className="visual-issue"><span className="visual-issue-dot"/> Duplicate SKU <b>12</b></div>
        <div className="visual-issue"><span className="visual-issue-dot amber-dot"/> Missing fields <b>18</b></div>
        <div className="visual-issue"><span className="visual-issue-dot blue-dot"/> Price validation <b>8</b></div>
        <p className="visual-footnote">Illustrative preview · Actual findings depend on your uploaded file.</p>
      </div>
    </div>
  </section>
  <section className="pricing-section" id="pricing">
    <div className="pricing-heading"><div className="eyebrow dark">STRAIGHTFORWARD PRICING</div><h2>Start free. Choose the audit that fits.</h2><p>Transparent, one-time audit pricing. No subscriptions or revenue-share fees.</p></div>
    <div className="pricing-grid">
      <article className="price-card">
        <div className="price-tier">PILOT AUDIT</div><div className="price-amount">$0 <span>/ free</span></div><p className="price-description">Try the workflow with a small catalog sample.</p>
        <ul><li><Check size={15}/> Up to 50 SKUs</li><li><Check size={15}/> Basic catalog checks</li><li><Check size={15}/> Sample findings summary</li></ul>
        <button className="price-button price-button-light" onClick={()=>document.getElementById("audit-workspace")?.scrollIntoView({behavior:"smooth"})}>Run free audit <ArrowDownToLine size={15}/></button>
      </article>
      <article className="price-card price-featured">
        <div className="price-badge">MOST POPULAR</div><div className="price-tier">GROWTH AUDIT</div><div className="price-amount">$99 <span>/ one-time</span></div><p className="price-description">For growing brands reviewing a larger catalog.</p>
        <ul><li><Check size={15}/> Up to 1,000 SKUs</li><li><Check size={15}/> Root-cause grouping</li><li><Check size={15}/> Findings review queue</li><li><Check size={15}/> Exportable findings CSV</li></ul>
        <button className="price-button price-button-primary" onClick={()=>document.getElementById("audit-workspace")?.scrollIntoView({behavior:"smooth"})}>Choose Growth <ArrowDownToLine size={15}/></button>
      </article>
      <article className="price-card">
        <div className="price-tier">SCALE AUDIT</div><div className="price-amount">$249 <span>/ one-time</span></div><p className="price-description">For larger catalogs and multi-channel workflows.</p>
        <ul><li><Check size={15}/> Up to 5,000 SKUs</li><li><Check size={15}/> Root-cause grouping</li><li><Check size={15}/> Multi-channel feed review</li><li><Check size={15}/> Priority review scope</li></ul>
        <button className="price-button price-button-light" onClick={()=>document.getElementById("audit-workspace")?.scrollIntoView({behavior:"smooth"})}>Choose Scale <ArrowDownToLine size={15}/></button>
      </article>
    </div>
    <p className="pricing-note">Pricing is displayed for plan selection. Online payment and paid-plan fulfillment are not connected in this MVP.</p>
  </section>
   <input ref={input} type="file" accept=".csv,text/csv" hidden onChange={e=>load(e.target.files?.[0])}/>
   <section className="section-head" id="audit-workspace"><div><div className="eyebrow dark">AUDIT WORKSPACE</div><h2>Catalog overview</h2><p>Upload a catalog export or explore the sample data to see how the audit works.</p></div>{rows&&<button className="btn subtle" onClick={()=>{setRows(null);setFilename("");}}>Reset audit <X size={15}/></button>}</section>
   {!rows?<div className={"upload-zone "+(drag?"drag":"")} onDragOver={e=>{e.preventDefault();setDrag(true)}} onDragLeave={()=>setDrag(false)} onDrop={e=>{e.preventDefault();setDrag(false);load(e.dataTransfer.files?.[0]);}}><div className="upload-icon"><FileSpreadsheet size={26}/></div><h3>Upload your product catalog</h3><p>Drag and drop a CSV file here, or browse from your device.</p><button className="btn dark-btn" onClick={()=>input.current?.click()}><ArrowUpFromLine size={16}/> Browse CSV file</button><div className="upload-meta">CSV format <span>·</span> Processed in your browser <span>·</span> No account required</div><div className="sample-link">Not ready? <button onClick={demo}>Run a sample audit <span>→</span></button></div></div>:<><div className="file-banner"><div className="file-icon"><FileSpreadsheet size={20}/></div><div className="file-info"><b>{filename}</b><span>{rows.length.toLocaleString()} rows · {result?.headers.length||0} columns detected</span></div><BadgeCheck size={18} className="file-check"/><button className="btn subtle" onClick={()=>input.current?.click()}>Replace file</button></div>
   <div className="metrics"><div className="metric"><span className="metric-icon blue"><FileSpreadsheet size={18}/></span><span className="metric-label">ROWS ANALYZED</span><strong>{rows.length.toLocaleString()}</strong><small>Product records</small></div><div className="metric"><span className="metric-icon red"><CircleAlert size={18}/></span><span className="metric-label">FINDINGS</span><strong>{result.findings.length.toLocaleString()}</strong><small>Items flagged for review</small></div><div className="metric"><span className="metric-icon amber"><Filter size={18}/></span><span className="metric-label">ISSUE TYPES</span><strong>{new Set(result.findings.map(f=>f.kind)).size}</strong><small>Distinct check categories</small></div><div className="metric"><span className="metric-icon green"><Check size={18}/></span><span className="metric-label">NO FLAGS</span><strong>{Math.max(0,rows.length-new Set(result.findings.map(f=>f.row)).size).toLocaleString()}</strong><small>Rows without detected flags</small></div></div>
   <div className="results-card"><div className="results-head"><div><div className="eyebrow dark">AUDIT RESULTS</div><h3>Findings & review queue</h3><p>Rule-based signals for human review—not automatic catalog corrections.</p></div><div className="export-actions"><button className="btn subtle" onClick={exportIssues}><ArrowDownToLine size={15}/> Export CSV</button><button className="btn dark-btn" onClick={exportReport}><FileText size={15}/> Print / Save report</button></div></div>
   <div className="toolbar"><div className="search"><Search size={16}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search findings, SKU, or row..."/></div><div className="filter-wrap"><Filter size={15}/><select value={filter} onChange={e=>setFilter(e.target.value)}><option>All issues</option>{[...new Set(result.findings.map(f=>f.kind))].map(k=><option key={k}>{k}</option>)}</select><ChevronDown size={14}/></div></div>
   <div className="table-wrap"><table><thead><tr><th>ISSUE TYPE</th><th>SKU / IDENTIFIER</th><th>ROW</th><th>FINDING</th><th>STATUS</th></tr></thead><tbody>{visible.map(f=><tr key={f.id}><td><span className="issue-type"><span className="issue-dot"/> {f.kind}</span></td><td className="sku">{f.sku||"—"}</td><td className="row-num">{f.row}</td><td className="detail">{f.detail}</td><td><span className="review-badge">Review</span></td></tr>)}</tbody></table>{visible.length===0&&<div className="empty"><BadgeCheck size={22}/><b>No findings match this filter</b><span>Try a different search or issue type.</span></div>}</div><div className="table-foot">Showing {visible.length} of {result.findings.length} findings <span>•</span> {rows.length} rows analyzed</div></div>
   <div className="disclaimer"><ShieldCheck size={17}/><span><b>Interpretation note</b> Findings are based on the checks included in this MVP. Review each flag against your source system before changing a live listing. A clean result does not guarantee a defect-free catalog.</span></div>
   {result.rootCauses.length>0&&<div className="root-causes"><div className="section-head" style={{padding:"0 0 14px 0"}}><div><div className="eyebrow dark">ROOT-CAUSE ANALYSIS</div><h3>Why these keep happening</h3><p>Findings above grouped into the underlying pattern — not just a symptom list.</p></div></div>
    {result.rootCauses.map(rc=><div className="rc-block" key={rc.tag}><div className="rc-block-head"><b>{rc.label}</b><span className="rc-count">{rc.findings.length} related finding{rc.findings.length===1?"":"s"}</span></div><p className="rc-explain">{rc.explanation}</p></div>)}
   </div>}</>}
   <section className="checks"><div className="eyebrow dark">AUDIT COVERAGE</div><h3>What this audit checks</h3><div className="check-grid"><div><span className="check-num">01</span><b>Duplicate SKUs</b><p>Repeated identifiers that may create catalog conflicts.</p></div><div><span className="check-num">02</span><b>Missing fields</b><p>Blank SKU, title, price, or category values where columns are detected.</p></div><div><span className="check-num">03</span><b>Repeated titles</b><p>Exact normalized title matches that may need a closer look.</p></div><div><span className="check-num">04</span><b>Price validation</b><p>Prices that are not valid non-negative numeric values.</p></div></div></section>
   <footer><span>© 2026 CATALOGops</span><span>Catalog quality workspace <b>·</b> MVP 0.1</span></footer>
  </main>
 </div>
}
createRoot(document.getElementById("root")).render(<App/>);