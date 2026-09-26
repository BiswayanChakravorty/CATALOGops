"""
CatalogOps Report Generator
Reuses the branded reportlab pipeline established for the VBA-audit business
(same navy/amber/cream identity) so both products read as one company.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("Serif-Bold", f"{FONT_DIR}/DejaVuSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono", f"{FONT_DIR}/DejaVuSansMono.ttf"))

NAVY = colors.HexColor("#1c2333")
MUTED = colors.HexColor("#6b7180")
AMBER = colors.HexColor("#c9702f")
GREEN = colors.HexColor("#2f5e42")
GREEN_BG = colors.HexColor("#e2ece5")
RED = colors.HexColor("#8a3b32")
RED_BG = colors.HexColor("#f2ded9")
LINE = colors.HexColor("#d8d4c6")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("ReportTitle", fontName="Serif-Bold", fontSize=22, textColor=NAVY))
styles.add(ParagraphStyle("SubMeta", fontName="Sans", fontSize=9.5, textColor=MUTED))
styles.add(ParagraphStyle("SectionHead", fontName="Serif-Bold", fontSize=13.5, textColor=NAVY, spaceBefore=14, spaceAfter=6))
styles.add(ParagraphStyle("Body", fontName="Sans", fontSize=9.7, textColor=colors.HexColor("#2b2f3a"), leading=14))
styles.add(ParagraphStyle("BodyItalic", fontName="Sans", fontSize=9.2, textColor=MUTED, leading=13))
styles.add(ParagraphStyle("StatLabel", fontName="Sans", fontSize=7.8, textColor=MUTED))
styles.add(ParagraphStyle("StatValue", fontName="Serif-Bold", fontSize=20, textColor=NAVY))
styles.add(ParagraphStyle("CellBody", fontName="Sans", fontSize=8.6, textColor=colors.HexColor("#2b2f3a"), leading=11.5))
styles.add(ParagraphStyle("FindingTitle", fontName="Sans-Bold", fontSize=10.5, textColor=NAVY, spaceBefore=8, spaceAfter=2))


def _header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, letter[1] - 0.28*inch, letter[0], 0.28*inch, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Sans-Bold", 8.5)
    canvas.drawString(0.6*inch, letter[1] - 0.19*inch, "CATALOGOPS")
    canvas.setFillColor(AMBER)
    canvas.drawRightString(letter[0] - 0.6*inch, letter[1] - 0.19*inch, "CATALOG AUDIT REPORT")
    canvas.setFillColor(MUTED)
    canvas.setFont("Sans", 7.7)
    canvas.drawString(0.6*inch, 0.45*inch, "Every flagged item traces to a specific rule. Nothing here is guessed.")
    canvas.drawRightString(letter[0] - 0.6*inch, 0.45*inch, f"Page {doc.page}")
    canvas.restoreState()


def build_report(audit_result: dict, output_path: str, catalog_name: str = "Uploaded catalog"):
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        topMargin=0.65*inch, bottomMargin=0.7*inch, leftMargin=0.6*inch, rightMargin=0.6*inch,
    )
    story = []

    # --- Title ---
    story.append(Paragraph("Catalog Audit Report", styles["ReportTitle"]))
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        f"Prepared for: {catalog_name} &nbsp;\u00b7&nbsp; {audit_result['row_count']} rows analyzed "
        f"&nbsp;\u00b7&nbsp; {datetime.now().strftime('%B %d, %Y')}",
        styles["SubMeta"]
    ))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=LINE))
    story.append(Spacer(1, 12))

    # --- Summary stats ---
    flagged = audit_result["flagged_count"]
    verified = audit_result["verified_count"]
    root_cause_count = len(audit_result["root_causes"])

    label_row = [Paragraph(t, styles["StatLabel"]) for t in
                 ["ROWS ANALYZED", "FLAGGED FOR REVIEW", "VERIFIED SAMPLE", "ROOT CAUSES IDENTIFIED"]]
    vals = [str(audit_result["row_count"]), str(flagged), str(verified), str(root_cause_count)]
    vcolors = ["#1c2333", "#c9702f", "#2f5e42", "#1c2333"]
    value_row = []
    for v, c in zip(vals, vcolors):
        st = ParagraphStyle(f"v_{v}_{c}", parent=styles["StatValue"], textColor=colors.HexColor(c))
        value_row.append(Paragraph(v, st))
    stat_table = Table([label_row, value_row], colWidths=[1.7*inch]*4, rowHeights=[13, 28])
    stat_table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),0),
                                     ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),2)]))
    story.append(stat_table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=LINE))

    # --- Findings table ---
    story.append(Paragraph("Findings", styles["SectionHead"]))
    header = [Paragraph(h, styles["StatLabel"]) for h in ["CHECK", "ITEMS", "DESCRIPTION", "STATUS"]]
    data = [header]
    for f in audit_result["findings"]:
        status_color = "#2f5e42" if f.severity == "verified" else "#8a3b32"
        status_label = "Verified" if f.severity == "verified" else "Flagged"
        data.append([
            Paragraph(f.check.replace("_", " ").title(), styles["CellBody"]),
            Paragraph(", ".join(f.items[:3]), styles["CellBody"]),
            Paragraph(f.description, styles["CellBody"]),
            Paragraph(f"<font color='{status_color}'>&#9679;</font> {status_label}", styles["CellBody"]),
        ])
    t = Table(data, colWidths=[1.1*inch, 1.1*inch, 3.4*inch, 0.95*inch], repeatRows=1)
    t.setStyle(TableStyle([
        ("LINEBELOW",(0,0),(-1,0),1,LINE), ("LINEBELOW",(0,1),(-1,-1),0.5,LINE),
        ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6), ("VALIGN",(0,0),(-1,-1),"TOP"),
    ]))
    story.append(t)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=LINE))

    # --- Root causes ---
    story.append(Paragraph("Root Causes", styles["SectionHead"]))
    if audit_result["root_causes"]:
        for tag, data_rc in audit_result["root_causes"].items():
            title = tag.replace("_", " ").title()
            story.append(Paragraph(f"{title} ({len(data_rc['findings'])} related findings)", styles["FindingTitle"]))
            story.append(Paragraph(data_rc["explanation"], styles["Body"]))
    else:
        story.append(Paragraph("No recurring structural pattern identified across findings.", styles["BodyItalic"]))

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=LINE))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "This audit uses deterministic, rule-based checks. Every finding above traces to a specific, "
        "explainable rule — nothing is silently inferred. Items not flagged were checked and passed, "
        "not skipped.",
        styles["BodyItalic"]
    ))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return output_path
