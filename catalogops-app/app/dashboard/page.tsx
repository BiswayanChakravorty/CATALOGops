'use client';

import React, { useState } from 'react';
import { FileUp, Layers, Download } from 'lucide-react';

export default function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [isAuditing, setIsAuditing] = useState<boolean>(false);
  const [auditComplete, setAuditComplete] = useState<boolean>(true);
  const [filterType, setFilterType] = useState<string>('ALL');

  const findings = [
    { id: '1', issueType: 'Duplicate SKU', sku: 'MG-2001', row: 7, finding: 'SKU appears more than once in catalog export.', status: 'Review Needed' },
    { id: '2', issueType: 'Duplicate SKU', sku: 'MG-2001', row: 8, finding: 'SKU appears more than once in catalog export.', status: 'Review Needed' },
    { id: '3', issueType: 'Missing Price', sku: 'BT-3001-L', row: 10, finding: 'Price attribute is completely blank.', status: 'Review Needed' },
    { id: '4', issueType: 'Missing Price', sku: 'NB-4001', row: 11, finding: 'Price attribute is completely blank.', status: 'Review Needed' },
    { id: '5', issueType: 'Missing Category', sku: 'NB-4001', row: 11, finding: 'Category field is blank for channel feed.', status: 'Review Needed' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-10 font-sans">
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 pb-8 border-b border-slate-800">
        <div><h1 className="text-2xl font-bold text-white">CATALOGops Audit Workspace</h1><p className="text-slate-400 text-sm mt-1">Rule-based catalog intelligence and root-cause pattern diagnosis</p></div>
        <label className="cursor-pointer bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold px-5 py-2.5 rounded-xl flex items-center gap-2">
          <FileUp className="w-4 h-4" /><span>Upload Catalog CSV</span><input type="file" accept=".csv" className="hidden" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        </label>
      </header>
      <main className="max-w-7xl mx-auto py-8 space-y-8">
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl"><div className="text-xs text-slate-400 uppercase">Rows Analyzed</div><div className="text-3xl font-bold text-white mt-2">16</div></div>
          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl border-l-4 border-l-amber-500"><div className="text-xs text-amber-400 uppercase">Findings Flagged</div><div className="text-3xl font-bold text-amber-400 mt-2">5</div></div>
          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl"><div className="text-xs text-blue-400 uppercase">Issue Categories</div><div className="text-3xl font-bold text-blue-400 mt-2">3</div></div>
          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl"><div className="text-xs text-emerald-400 uppercase">Clean Rows</div><div className="text-3xl font-bold text-emerald-400 mt-2">12</div></div>
        </section>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <section className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800"><h2 className="text-lg font-bold text-white">Findings & Review Queue</h2><button className="text-xs font-semibold bg-emerald-600 text-white px-3.5 py-2 rounded-lg flex items-center gap-1.5"><Download className="w-3.5 h-3.5" /> Export Corrected CSV</button></div>
            <table className="w-full text-left border-collapse text-xs"><thead><tr className="border-b border-slate-800 text-slate-400 uppercase"><th className="py-3 px-3">Issue Type</th><th className="py-3 px-3">SKU</th><th className="py-3 px-3 text-center">Row</th><th className="py-3 px-3">Details</th></tr></thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">{findings.map((item) => (<tr key={item.id} className="hover:bg-slate-800/40"><td className="py-3.5 px-3"><span className="bg-amber-500/10 text-amber-400 px-2.5 py-0.5 rounded font-semibold border border-amber-500/20">{item.issueType}</span></td><td className="py-3.5 px-3 font-mono font-bold text-white">{item.sku}</td><td className="py-3.5 px-3 text-center">Row {item.row}</td><td className="py-3.5 px-3">{item.finding}</td></tr>))}</tbody>
            </table>
          </section>
          <section className="lg:col-span-4 bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center gap-2 text-white font-bold border-b border-slate-800 pb-3"><Layers className="w-5 h-5 text-blue-400" /><span>Root-Cause Diagnostics</span></div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs space-y-2"><div className="font-bold text-amber-400">Duplicate Entries Pattern</div><p className="text-slate-300 leading-relaxed">Duplicate SKUs (<code className="text-amber-300">MG-2001</code>) stem from independent POS and Shopify ID generation with no central reconciliation layer.</p></div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs space-y-2"><div className="font-bold text-blue-400">Missing Fields Pattern</div><p className="text-slate-300 leading-relaxed">Blank attributes (<code className="text-blue-300">BT-3001-L</code>) occur when bulk imports bypass required field validation at creation time.</p></div>
          </section>
        </div>
      </main>
    </div>
  );
}
