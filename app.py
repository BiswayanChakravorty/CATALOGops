"""
CATALOGops — Client-facing catalog audit workspace.
Run locally: streamlit run app.py
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from audit_engine import run_audit
from report_generator import build_report

st.set_page_config(
    page_title="CATALOGops | Catalog Intelligence",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#172235"
INK = "#202B3C"
AMBER = "#D18A45"
PAPER = "#F7F5F0"
MUTED = "#667085"

st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
      :root {{ --navy:{NAVY}; --amber:{AMBER}; --paper:{PAPER}; }}
      .stApp {{ background:var(--paper); color:{INK}; font-family:'DM Sans',sans-serif; }}
      [data-testid="stHeader"] {{ background:rgba(247,245,240,.92); }}
      [data-testid="stSidebar"] {{ background:{NAVY}; }}
      [data-testid="stSidebar"] * {{ color:#F7F5F0 !important; }}
      h1,h2,h3 {{ color:{NAVY}; font-family:'Playfair Display',Georgia,serif !important; letter-spacing:-.02em; }}
      .brand-kicker {{ text-transform:uppercase; letter-spacing:.18em; font-size:.72rem; font-weight:700; color:{AMBER}; }}
      .hero {{ background:{NAVY}; color:#F7F5F0; padding:2.1rem 2.2rem; border-radius:18px; margin:0 0 1.4rem 0; }}
      .hero h1 {{ color:#fff !important; font-size:2.6rem; margin:.35rem 0 .5rem 0; }}
      .hero p {{ color:#D7DCE5; font-size:1.02rem; max-width:760px; line-height:1.65; }}
      .hero .eyebrow {{ color:#E9B16E; font-size:.72rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; }}
      .panel {{ background:#fff; border:1px solid #E7E2D8; border-radius:14px; padding:1.15rem 1.3rem; }}
      .small-label {{ color:{MUTED}; font-size:.75rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }}
      div[data-testid="stMetric"] {{ background:#fff; border:1px solid #E7E2D8; padding:1rem 1.1rem; border-radius:13px; }}
      div[data-testid="stMetricLabel"] {{ color:{MUTED}; }}
      div[data-testid="stMetricValue"] {{ color:{NAVY}; font-weight:700; }}
      .stButton>button, .stDownloadButton>button {{ background:{NAVY}; color:white; border:1px solid {NAVY}; border-radius:9px; padding:.65rem 1.1rem; font-weight:600; }}
      .stButton>button:hover, .stDownloadButton>button:hover {{ background:#293951; color:white; border-color:#293951; }}
      div[data-testid="stFileUploader"] {{ background:#fff; border:1px dashed #C9C2B5; border-radius:12px; padding:.7rem; }}
      .note {{ color:{MUTED}; font-size:.84rem; line-height:1.55; }}
      hr {{ border-color:#E7E2D8; }}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(f"<div style='font-size:1.35rem;font-weight:800;letter-spacing:.06em'>CATALOG<span style='color:{AMBER}'>ops</span></div>", unsafe_allow_html=True)
    st.caption("CATALOG INTELLIGENCE")
    st.divider()
    st.markdown("**Workspace**")
    st.markdown("01  ·  Catalog audit")
    st.markdown("02  ·  Findings & root causes")
    st.markdown("03  ·  Audit report")
    st.divider()
    st.markdown("**Designed for**")
    st.markdown("Shopify · Amazon · Multichannel exports")
    st.divider()
    st.markdown("<div class='note'>File-based audit workspace. No live store connection or continuous sync is enabled in this MVP.</div>", unsafe_allow_html=True)

st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">Catalog quality • Root-cause diagnostics</div>
      <h1>Find the errors.<br/>Understand why they recur.</h1>
      <p>CATALOGops audits exported product data, surfaces explainable catalog issues, and organizes findings into practical root-cause groups—so your team can move from cleanup to a more reliable catalog process.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.45, 1], gap="large")
with left:
    st.subheader("Start a catalog audit")
    st.markdown("Upload a product export to analyze it, or use the sample catalog to explore the workflow.")
    uploaded_file = st.file_uploader(
        "Choose a catalog export",
        type=["csv", "xlsx", "xls"],
        help="Supported formats: CSV and Excel. Use a product-catalog export with SKU, title, price, category, and variant fields where available.",
    )
    action_col, info_col = st.columns([1, 1])
    with action_col:
        run_demo = st.button("Run sample audit", use_container_width=True)
    with info_col:
        st.download_button(
            "Download sample CSV",
            data=Path(__file__).with_name("sample_catalog.csv").read_bytes(),
            file_name="catalogops_sample_catalog.csv",
            mime="text/csv",
            use_container_width=True,
        )
with right:
    st.markdown(
        """
        <div class="panel">
          <div class="small-label">What this audit checks</div>
          <br/>
          <b>01 · Duplicate SKUs</b><br/><span class="note">Repeated identifiers that may create catalog conflicts.</span><br/><br/>
          <b>02 · Missing fields</b><br/><span class="note">Blank title, price, or category values where those columns exist.</span><br/><br/>
          <b>03 · Similar titles</b><br/><span class="note">Potentially inconsistent product titles, based on a transparent similarity rule.</span><br/><br/>
          <b>04 · Variant gaps</b><br/><span class="note">Product groups with a mix of populated and missing variant values.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<p class='note'>For client confidentiality, use a sanitized export during demonstrations. This MVP is file-based and does not connect directly to store accounts.</p>", unsafe_allow_html=True)

audit_source = None
catalog_name = None
if uploaded_file is not None:
    audit_source = uploaded_file.getvalue()
    catalog_name = uploaded_file.name
elif run_demo:
    sample_path = Path(__file__).with_name("sample_catalog.csv")
    audit_source = sample_path.read_bytes()
    catalog_name = sample_path.name

if audit_source is not None:
    st.divider()
    st.subheader("Audit results")
    tmp_path = None
    report_path = None
    try:
        suffix = Path(catalog_name or "catalog.csv").suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audit_source)
            tmp_path = tmp.name

        with st.spinner("Analyzing catalog rows and grouping findings…"):
            result = run_audit(tmp_path)

        if result["row_count"] == 0:
            st.warning("The uploaded file has no data rows. Please choose a catalog export with at least one product.")
            st.stop()

        metric_cols = st.columns(4)
        metric_cols[0].metric("Rows analyzed", f"{result['row_count']:,}")
        metric_cols[1].metric("Flagged findings", f"{result['flagged_count']:,}")
        metric_cols[2].metric("Root-cause groups", f"{len(result['root_causes']):,}")
        metric_cols[3].metric("Verified sample", f"{result['verified_count']:,}")

        st.caption(f"Source file: {catalog_name}  ·  Fields detected: {sum(v is not None for v in result['columns_detected'].values())} of {len(result['columns_detected'])}")
        with st.expander("View detected field mapping"):
            mapping_df = pd.DataFrame(
                [{"Canonical field": key.replace("_", " ").title(), "Matched column": value or "Not detected"} for key, value in result["columns_detected"].items()]
            )
            st.dataframe(mapping_df, use_container_width=True, hide_index=True)

        tab_findings, tab_causes, tab_clean = st.tabs(["Findings", "Root-cause analysis", "Verified sample"])
        with tab_findings:
            flagged = [f for f in result["findings"] if f.severity == "flag"]
            if flagged:
                findings_df = pd.DataFrame([
                    {
                        "Check": f.check.replace("_", " ").title(),
                        "Affected item(s)": ", ".join(f.items),
                        "Finding": f.description,
                        "Root-cause group": f.root_cause_tag.replace("_", " ").title(),
                    } for f in flagged
                ])
                st.dataframe(findings_df, use_container_width=True, hide_index=True)
            else:
                st.success("No issues were flagged by the checks included in this audit.")
        with tab_causes:
            if result["root_causes"]:
                for tag, group in result["root_causes"].items():
                    with st.expander(f"{tag.replace('_', ' ').title()} · {len(group['findings'])} finding(s)", expanded=True):
                        st.write(group["explanation"])
                        for finding in group["findings"]:
                            st.markdown(f"- **{finding.check.replace('_', ' ').title()}:** {finding.description}")
            else:
                st.info("No root-cause groups were identified in this audit.")
        with tab_clean:
            clean = [f for f in result["findings"] if f.severity == "verified"]
            if clean:
                st.dataframe(pd.DataFrame([{"SKU / ID": ", ".join(f.items), "Status": "Verified sample", "Details": f.description} for f in clean]), use_container_width=True, hide_index=True)
                st.caption("This is a small sample of rows that passed the checks—not a guarantee that every possible catalog issue is absent.")
            else:
                st.info("No verified sample rows were available. A SKU column may be required for this view.")

        st.divider()
        st.subheader("Export your audit")
        st.markdown("Generate a shareable PDF summary of the current findings and root-cause groups.")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as report_tmp:
            report_path = report_tmp.name
        build_report(result, report_path, catalog_name=catalog_name or "Uploaded catalog")
        with open(report_path, "rb") as report_file:
            pdf_bytes = report_file.read()
        st.download_button(
            "Download audit report (PDF)",
            data=pdf_bytes,
            file_name=f"catalogops_audit_{Path(catalog_name or 'catalog').stem}.pdf",
            mime="application/pdf",
            type="primary",
        )
        st.caption("Audit output is based on the checks currently implemented. Findings are prompts for review, not automatic catalog edits.")
    except Exception as exc:
        st.error(f"Unable to complete this audit. Check that the file is a valid CSV or Excel export and try again.")
        with st.expander("Technical details"):
            st.code(str(exc))
    finally:
        for path in (tmp_path, report_path):
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except OSError:
                    pass
