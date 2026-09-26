"""
CatalogOps — Streamlit MVP
Upload a catalog -> run the audit engine -> download the branded PDF report.

Run locally with:  streamlit run app.py
Deploy free on Streamlit Community Cloud by pushing this repo to GitHub
and connecting it there (see the tech-stack design doc for details).
"""

import streamlit as st
import tempfile
import os
from audit_engine import run_audit
from report_generator import build_report

st.set_page_config(page_title="CatalogOps", page_icon="📋", layout="centered")

# Minimal brand-consistent styling (navy / amber / cream)
st.markdown("""
<style>
    .stApp { background-color: #fdfaf4; }
    h1, h2, h3 { color: #1c2333 !important; font-family: Georgia, serif; }
    .stButton>button {
        background-color: #1c2333; color: white; border-radius: 5px; border: none;
    }
    .stButton>button:hover { background-color: #2a3348; color: white; }
    div[data-testid="stMetricValue"] { color: #1c2333; }
</style>
""", unsafe_allow_html=True)

st.title("CatalogOps")
st.caption("Find out why your product catalog keeps breaking — not just what's wrong today.")

st.divider()

uploaded_file = st.file_uploader(
    "Upload your catalog export",
    type=["csv", "xlsx", "xls"],
    help="Shopify, Amazon Seller Central, or a generic product export"
)

if uploaded_file is not None:
    # Save to a temp file since the audit engine reads from a path
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    with st.spinner("Running audit — mapping columns, checking for duplicates, missing fields, and broken variants..."):
        try:
            result = run_audit(tmp_path)
        except Exception as e:
            st.error(f"Couldn't process this file: {e}")
            st.stop()

    st.success(f"Audit complete — {result['row_count']} rows analyzed.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows analyzed", result["row_count"])
    col2.metric("Flagged for review", result["flagged_count"])
    col3.metric("Root causes found", len(result["root_causes"]))

    st.subheader("Findings")
    for f in result["findings"]:
        icon = "🟢" if f.severity == "verified" else "🟠"
        st.markdown(f"{icon} **{f.check.replace('_',' ').title()}** — {f.description}")

    if result["root_causes"]:
        st.subheader("Root causes")
        for tag, data in result["root_causes"].items():
            with st.expander(f"{tag.replace('_',' ').title()} ({len(data['findings'])} related findings)"):
                st.write(data["explanation"])

    st.divider()

    # Generate the branded PDF for download
    report_path = tmp_path + "_report.pdf"
    build_report(result, report_path, catalog_name=uploaded_file.name)
    with open(report_path, "rb") as f:
        st.download_button(
            "Download full PDF report",
            data=f.read(),
            file_name=f"catalogops_audit_{uploaded_file.name.rsplit('.',1)[0]}.pdf",
            mime="application/pdf"
        )

    st.caption("Your file is processed in memory for this session only and is not stored after you leave this page.")

    os.unlink(tmp_path)
    os.unlink(report_path)

else:
    st.info("Upload a CSV or Excel catalog export to get started. Not sure what to expect? "
            "The audit checks for duplicate SKUs, missing required fields, inconsistent titles, "
            "and broken variant groups — then explains the likely root cause of each pattern.")
