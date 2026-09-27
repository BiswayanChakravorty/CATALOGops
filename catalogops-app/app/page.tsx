import React from 'react';
import Link from 'next/link';
import { ArrowRight, CheckCircle2, FileSpreadsheet, ShieldCheck, Sparkles } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased">
      <div className="bg-gradient-to-r from-blue-700 via-indigo-600 to-blue-700 text-white text-xs md:text-sm font-medium py-2.5 px-4 text-center border-b border-blue-500/30 flex items-center justify-center gap-2">
        <Sparkles className="w-4 h-4 text-amber-300 animate-pulse" />
        <span>As seen in your personalized Loom Video Audit Breakdown — CATALOGops v1.0 is live!</span>
      </div>
      <section className="pt-20 pb-24 px-6 max-w-7xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-blue-500/30 bg-blue-950/40 text-blue-400 text-xs font-semibold uppercase mb-8">
          <ShieldCheck className="w-4 h-4" /> Zero-Code Catalog Intelligence for Shopify & Amazon
        </div>
        <h1 className="text-4xl md:text-6xl font-extrabold text-white max-w-4xl mx-auto leading-tight">
          Stop Band-Aiding Catalog Errors. <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400">
            Fix the Root Cause of Broken SKUs.
          </span>
        </h1>
        <p className="mt-6 text-lg text-slate-300 max-w-2xl mx-auto">
          The automated audit engine built for growing DTC brands. Eliminate duplicate SKUs, missing price fields, and feed import failures — without $45,000/year PIM software or unreliable gig labor.
        </p>
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link href="/dashboard" className="w-full sm:w-auto text-base font-bold bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-xl shadow-xl shadow-blue-600/30 flex items-center justify-center gap-3">
            <FileSpreadsheet className="w-5 h-5" /><span>Upload Catalog CSV (Free 50-SKU Test)</span><ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
      <section id="pricing" className="py-20 px-6 max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl font-bold text-white">Transparent, Flat-Fee Audit Plans</h2>
          <p className="text-slate-400 text-sm mt-2">No long-term contracts. No revenue percentage fees.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-8 flex flex-col justify-between">
            <div><div className="text-xs font-bold text-slate-400 uppercase mb-2">Pilot Audit</div><div className="text-4xl font-extrabold text-white">$0</div>
              <p className="text-sm text-slate-400 mt-4 pb-4 border-b border-slate-800">Free 50-SKU test file audit.</p>
              <ul className="mt-6 space-y-3 text-sm text-slate-300">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Up to 50 SKUs evaluated</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Duplicate SKU detection</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Sample diagnostic summary</li>
              </ul>
            </div><Link href="/dashboard" className="mt-8 w-full py-3.5 rounded-xl border border-slate-700 bg-slate-800 text-white font-semibold text-sm text-center">Run Free Audit</Link>
          </div>
          <div className="bg-slate-900 border-2 border-blue-500 rounded-3xl p-8 flex flex-col justify-between relative shadow-2xl shadow-blue-500/10">
            <div><div className="text-xs font-bold text-blue-400 uppercase mb-2">Growth Audit</div><div className="text-4xl font-extrabold text-white">$99 <span className="text-sm font-normal text-slate-400">/ Flat</span></div>
              <p className="text-sm text-slate-300 mt-4 pb-4 border-b border-slate-800">For scaling DTC brands with up to 1,000 SKUs.</p>
              <ul className="mt-6 space-y-3 text-sm text-slate-200">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-blue-400" /> Up to 1,000 SKUs evaluated</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-blue-400" /> Complete Root-Cause Grouping</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-blue-400" /> Interactive Review Queue</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-blue-400" /> Corrected Ready-To-Upload CSV</li>
              </ul>
            </div><Link href="/dashboard?plan=growth" className="mt-8 w-full py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm text-center shadow-lg shadow-blue-600/30">Audit My Catalog ($99)</Link>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-8 flex flex-col justify-between">
            <div><div className="text-xs font-bold text-purple-400 uppercase mb-2">Scale Audit</div><div className="text-4xl font-extrabold text-white">$249 <span className="text-sm font-normal text-slate-400">/ Flat</span></div>
              <p className="text-sm text-slate-400 mt-4 pb-4 border-b border-slate-800">Multi-channel feeds for up to 5,000 SKUs.</p>
              <ul className="mt-6 space-y-3 text-sm text-slate-300">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-purple-400" /> Up to 5,000 SKUs evaluated</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-purple-400" /> Multi-channel feed mapping</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-purple-400" /> Priority edge-case human check</li>
              </ul>
            </div><Link href="/dashboard?plan=scale" className="mt-8 w-full py-3.5 rounded-xl border border-slate-700 bg-slate-800 text-white font-semibold text-sm text-center">Scale My Catalog ($249)</Link>
          </div>
        </div>
      </section>
    </div>
  );
}
