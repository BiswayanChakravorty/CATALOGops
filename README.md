# CATALOGops

**Catalog intelligence for growing e-commerce teams.** CATALOGops audits exported product data, surfaces explainable data-quality findings, and groups patterns into likely root causes.

> **MVP scope:** file-based catalog audits. This is not a live PIM, store integration, compliance certification, or automatic catalog-editing system.

## Who it's for

DTC and multichannel e-commerce operators managing product catalogs across platforms such as Shopify and Amazon—especially teams that need a structured diagnosis before committing to a cleanup project.

## What the MVP checks

- Duplicate SKUs
- Missing title, price, or category values when those columns are present
- Potential near-duplicate titles using fuzzy similarity
- Variant groups with a mixture of populated and missing variant values
- Root-cause grouping and a branded PDF audit report

Checks are deterministic and explainable. A flagged item should be reviewed before changing a live listing. A clean result only means the row passed the checks currently implemented.

## Run locally

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit. Use **Run sample audit** to see the workflow, or upload a sanitized CSV/Excel export.

## Run regression tests

```bash
python -m unittest discover -s tests -v
```

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create an app from this repository and select `app.py`.
3. Deploy using `requirements.txt` at the repository root.
4. Test the deployed app with a non-sensitive sample export before linking it from your business website.

## Client-data handling

The app temporarily writes the uploaded file and generated PDF to the server's temporary directory while processing, then attempts to remove those temporary files. Hosting providers may have their own logging, storage, and retention behavior. Do not upload personal customer data, credentials, or confidential information without an appropriate privacy and security review.

## Current limitations — disclose during pilots

- Column matching uses a known alias list and may not recognize custom export headers.
- Required-field checks are generic; marketplace-specific rules and category-level requirements are not implemented.
- Title similarity can miss genuine duplicates or flag unrelated titles. It is a review signal, not a definitive match.
- Variant-family detection uses a heuristic based on SKU suffixes and can mis-group unusual SKU formats.
- No live store API, ongoing monitoring, cross-channel reconciliation, stale/orphaned listing detection, automated correction, or change history is included.
- Root-cause groups are heuristic explanations, not proven causal diagnoses. Validate them with the client's workflow and source systems.

## Pilot validation goals

1. Audit 3–5 real pilot catalogs with client permission.
2. Compare findings against a manually reviewed reference set and record false positives / false negatives.
3. Confirm that clients understand the difference between a rule-based flag and a confirmed catalog defect.
4. Validate willingness to pay for an audit and separately scoped remediation.
