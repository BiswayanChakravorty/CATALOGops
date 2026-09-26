"""
CatalogOps Audit Engine
Stage 1 (Ingest) + Stage 2 (Audit Checks) + Stage 3 (Root-cause grouping)

Design principle carried over from the VBA audit business:
deterministic, rule-based checks first. Nothing here silently guesses -
every finding traces back to a specific, explainable rule.
"""

import pandas as pd
from rapidfuzz import fuzz
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import re


# ---------------------------------------------------------------------------
# Stage 1: INGEST
# ---------------------------------------------------------------------------

# Common column name variants across Shopify / Amazon / generic exports.
# This is intentionally simple pattern-matching, not a schema-inference ML
# model - correctness and transparency matter more than cleverness here.
COLUMN_ALIASES = {
    "sku": ["sku", "variant sku", "product sku", "seller-sku", "item sku", "id"],
    "title": ["title", "product title", "name", "item-name", "product name"],
    "price": ["price", "variant price", "your-price", "list-price"],
    "category": ["category", "product category", "product-type", "item-type-keyword"],
    "variant": ["variant", "option1 value", "option2 value", "size", "color", "colour"],
    "inventory": ["inventory", "quantity", "quantity-available", "stock"],
}


def detect_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """Map catalog columns onto canonical fields, ignoring case and outer whitespace.

    Strip outer whitespace from headers first so returned column names also
    match the DataFrame's actual labels. Alias matching remains case-insensitive.
    """
    df.columns = [str(column).strip() for column in df.columns]
    lower_cols = {str(column).strip().lower(): column for column in df.columns}
    mapping = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        found = None
        for alias in aliases:
            if alias in lower_cols:
                found = lower_cols[alias]
                break
        mapping[canonical] = found
    return mapping


def load_catalog(file_path: str) -> pd.DataFrame:
    """Load a CSV or Excel catalog export into a normalized DataFrame."""
    if file_path.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
    df.columns = [str(c).strip() for c in df.columns]
    return df


# ---------------------------------------------------------------------------
# Stage 2: AUDIT CHECKS
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    check: str              # which rule caught this
    severity: str            # "flag" or "verified"
    items: List[str]         # SKUs / row identifiers involved
    description: str         # plain-language description
    root_cause_tag: str      # used later to group findings into root causes


def check_duplicate_skus(df: pd.DataFrame, cols: Dict[str, str]) -> List[Finding]:
    findings = []
    sku_col = cols.get("sku")
    if not sku_col:
        return findings
    dupes = df[df.duplicated(subset=[sku_col], keep=False)]
    for sku, group in dupes.groupby(sku_col):
        if pd.isna(sku) or str(sku).strip() == "":
            continue
        titles = group[cols["title"]].tolist() if cols.get("title") else ["(no title column)"]
        findings.append(Finding(
            check="duplicate_sku",
            severity="flag",
            items=[str(sku)],
            description=f"SKU '{sku}' appears {len(group)} times with titles: {', '.join(str(t) for t in titles[:3])}",
            root_cause_tag="duplicate_entries"
        ))
    return findings


def check_missing_required_fields(df: pd.DataFrame, cols: Dict[str, str],
                                   required: List[str] = None) -> List[Finding]:
    """Flags rows missing fields we'd expect a channel (e.g. Amazon) to require."""
    findings = []
    required = required or ["title", "price", "category"]
    for field_name in required:
        col = cols.get(field_name)
        if not col:
            continue
        missing_mask = df[col].isna() | (df[col].astype(str).str.strip() == "")
        missing_rows = df[missing_mask]
        if len(missing_rows) == 0:
            continue
        sku_col = cols.get("sku")
        ids = missing_rows[sku_col].astype(str).tolist() if sku_col else [str(i) for i in missing_rows.index]
        findings.append(Finding(
            check=f"missing_{field_name}",
            severity="flag",
            items=ids[:20],
            description=f"{len(missing_rows)} row(s) missing '{field_name}' — required for most channel feeds",
            root_cause_tag="missing_fields"
        ))
    return findings


def _base_sku(sku: str) -> str:
    """Strip a trailing variant-style suffix (e.g. '-BLK', '-1001') to group variants of one product."""
    return re.sub(r"[-_]?[A-Za-z0-9]{1,4}$", "", str(sku)) if len(str(sku)) > 4 else str(sku)


def check_inconsistent_titles(df: pd.DataFrame, cols: Dict[str, str],
                               similarity_threshold: int = 85) -> List[Finding]:
    """
    Finds near-duplicate titles that are NOT exact matches - a common sign
    of the same product listed inconsistently across channel exports.

    Deliberately EXCLUDES pairs that share the same base SKU group, because
    "Water Bottle - Small" vs "Water Bottle - Large" is a legitimate variant
    pair, not a data error - flagging that would be exactly the kind of
    confident-but-wrong output this tool exists to avoid.
    """
    findings = []
    title_col = cols.get("title")
    sku_col = cols.get("sku")
    if not title_col:
        return findings

    titles = df[[sku_col, title_col]].dropna() if sku_col else df[[title_col]].dropna()
    flagged_pairs = set()

    title_list = titles[title_col].astype(str).tolist()
    id_list = titles[sku_col].astype(str).tolist() if sku_col else [str(i) for i in titles.index]
    base_list = [_base_sku(s) for s in id_list]

    # O(n^2) is fine at MVP scale (hundreds-low thousands of rows);
    # revisit with blocking/indexing if catalogs grow much larger.
    for i in range(len(title_list)):
        for j in range(i + 1, len(title_list)):
            if title_list[i] == title_list[j]:
                continue  # exact matches aren't the problem here
            if base_list[i] == base_list[j]:
                continue  # same product family (e.g. a size/color variant) - not an error
            score = fuzz.ratio(title_list[i].lower(), title_list[j].lower())
            if score >= similarity_threshold:
                pair_key = tuple(sorted([id_list[i], id_list[j]]))
                if pair_key in flagged_pairs:
                    continue
                flagged_pairs.add(pair_key)
                findings.append(Finding(
                    check="inconsistent_title",
                    severity="flag",
                    items=[id_list[i], id_list[j]],
                    description=f"Near-duplicate titles ({score:.0f}% similar) on different product families: '{title_list[i]}' vs '{title_list[j]}'",
                    root_cause_tag="title_inconsistency"
                ))
    return findings


def check_broken_variants(df: pd.DataFrame, cols: Dict[str, str]) -> List[Finding]:
    """Flags products where a variant field exists but is empty/malformed for some rows of the same base product."""
    findings = []
    variant_col = cols.get("variant")
    sku_col = cols.get("sku")
    if not variant_col or not sku_col:
        return findings

    # crude "base product" grouping: strip trailing variant-style suffixes from SKU
    df = df.copy()
    df["_base_sku"] = df[sku_col].astype(str).apply(_base_sku)

    for base, group in df.groupby("_base_sku"):
        if len(group) < 2:
            continue
        empty_variants = group[group[variant_col].isna() | (group[variant_col].astype(str).str.strip() == "")]
        if len(empty_variants) > 0 and len(empty_variants) < len(group):
            ids = empty_variants[sku_col].astype(str).tolist()
            findings.append(Finding(
                check="broken_variant",
                severity="flag",
                items=ids,
                description=f"Product group '{base}' has {len(empty_variants)} of {len(group)} variants with a missing variant value",
                root_cause_tag="variant_logic"
            ))
    return findings


def check_verified_clean_sample(df: pd.DataFrame, cols: Dict[str, str], all_findings: List[Finding]) -> List[Finding]:
    """Surface a handful of rows that passed every check, for the report's 'verified' column."""
    flagged_ids = set()
    for f in all_findings:
        flagged_ids.update(f.items)

    sku_col = cols.get("sku")
    if not sku_col:
        return []

    clean_rows = df[~df[sku_col].astype(str).isin(flagged_ids)]
    sample = clean_rows.head(3)
    findings = []
    for _, row in sample.iterrows():
        findings.append(Finding(
            check="clean_row",
            severity="verified",
            items=[str(row[sku_col])],
            description=f"'{row[sku_col]}' passed all checks — no duplicate, complete fields, no title/variant conflicts",
            root_cause_tag="none"
        ))
    return findings


# ---------------------------------------------------------------------------
# Stage 3: ROOT-CAUSE LAYER
# ---------------------------------------------------------------------------

ROOT_CAUSE_EXPLANATIONS = {
    "duplicate_entries": (
        "Duplicate SKUs usually mean the same product was created more than once — "
        "often because two systems (e.g. a POS and an online store) both generate "
        "product IDs independently, with nothing reconciling them."
    ),
    "missing_fields": (
        "Missing required fields typically happen when a product is created quickly "
        "(a bulk import, a rushed listing) and the required-fields check for that "
        "channel isn't enforced at creation time — the gap only surfaces later, at "
        "the point of failed import or listing rejection."
    ),
    "title_inconsistency": (
        "Near-duplicate titles usually mean the same product is maintained separately "
        "in more than one place (e.g. the online store and a marketplace feed) with "
        "no single source of truth — small edits drift apart over time."
    ),
    "variant_logic": (
        "Broken variant groups usually happen when new options (a new size or color) "
        "are added to some listings but not propagated consistently to every channel "
        "or every related SKU in the group."
    ),
}


def group_by_root_cause(findings: List[Finding]) -> Dict[str, Dict]:
    grouped = {}
    for f in findings:
        if f.root_cause_tag == "none":
            continue
        if f.root_cause_tag not in grouped:
            grouped[f.root_cause_tag] = {
                "explanation": ROOT_CAUSE_EXPLANATIONS.get(f.root_cause_tag, "Pattern identified across multiple findings."),
                "findings": []
            }
        grouped[f.root_cause_tag]["findings"].append(f)
    return grouped


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_audit(file_path: str) -> Dict:
    df = load_catalog(file_path)
    cols = detect_columns(df)

    findings: List[Finding] = []
    findings += check_duplicate_skus(df, cols)
    findings += check_missing_required_fields(df, cols)
    findings += check_inconsistent_titles(df, cols)
    findings += check_broken_variants(df, cols)
    findings += check_verified_clean_sample(df, cols, findings)

    root_causes = group_by_root_cause(findings)

    return {
        "row_count": len(df),
        "columns_detected": cols,
        "findings": findings,
        "root_causes": root_causes,
        "flagged_count": len([f for f in findings if f.severity == "flag"]),
        "verified_count": len([f for f in findings if f.severity == "verified"]),
    }


if __name__ == "__main__":
    import sys
    import json
    result = run_audit(sys.argv[1])
    print(f"Rows: {result['row_count']}")
    print(f"Columns detected: {result['columns_detected']}")
    print(f"Flagged: {result['flagged_count']}, Verified sample: {result['verified_count']}")
    for f in result["findings"]:
        print(f"  [{f.severity.upper()}] {f.check}: {f.description}")
    print("\nRoot causes:")
    for tag, data in result["root_causes"].items():
        print(f"  {tag} ({len(data['findings'])} findings): {data['explanation']}")
