"""Regression tests for the current CatalogOps audit rules."""
import unittest
from pathlib import Path

import pandas as pd

from audit_engine import (
    check_duplicate_skus,
    check_missing_required_fields,
    detect_columns,
    run_audit,
)


class AuditEngineTests(unittest.TestCase):
    def test_detect_columns_is_case_and_whitespace_tolerant(self):
        df = pd.DataFrame(columns=[" SKU ", "Product Title", "Price", "Category"])
        mapping = detect_columns(df)
        self.assertEqual(mapping["sku"], "SKU")
        self.assertEqual(mapping["title"], "Product Title")
        self.assertEqual(mapping["price"], "Price")
        self.assertEqual(mapping["category"], "Category")

    def test_duplicate_skus_are_flagged(self):
        df = pd.DataFrame({"SKU": ["A-1", "A-1"], "Title": ["Mug", "Mug 12oz"]})
        findings = check_duplicate_skus(df, detect_columns(df))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].check, "duplicate_sku")
        self.assertIn("A-1", findings[0].items)

    def test_missing_required_values_are_flagged(self):
        df = pd.DataFrame({
            "SKU": ["A-1", "A-2"],
            "Title": ["Mug", "Notebook"],
            "Price": [10.0, None],
            "Category": ["Home", ""],
        })
        findings = check_missing_required_fields(df, detect_columns(df))
        checks = {f.check for f in findings}
        self.assertIn("missing_price", checks)
        self.assertIn("missing_category", checks)

    def test_sample_catalog_runs_end_to_end(self):
        sample = Path(__file__).resolve().parents[1] / "sample_catalog.csv"
        result = run_audit(str(sample))
        self.assertGreater(result["row_count"], 0)
        self.assertGreater(result["flagged_count"], 0)
        self.assertGreater(len(result["root_causes"]), 0)
        self.assertIn("sku", result["columns_detected"])


if __name__ == "__main__":
    unittest.main()
