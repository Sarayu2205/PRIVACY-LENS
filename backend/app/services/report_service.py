"""
PrivacyLens – PDF Security Report Generator.
Uses ReportLab to create a professional security report PDF.
Sensitive values are never written to the report — only masked values are used.
"""
import os
import logging
from datetime import datetime
from typing import List

from app.config import settings
from app.models.scan import Scan
from app.models.finding import Finding
from app.models.report import Report
from app.services.risk_analyzer import build_recommendations, get_finding_severity

logger = logging.getLogger(__name__)


def _get_risk_color(level: str):
    """Return (R, G, B) tuple for a risk level."""
    colors = {
        "CRITICAL": (0.8, 0.1, 0.1),
        "HIGH":     (0.9, 0.4, 0.0),
        "MEDIUM":   (0.9, 0.7, 0.0),
        "LOW":      (0.2, 0.6, 0.2),
    }
    return colors.get(level, (0.3, 0.3, 0.3))


def generate_pdf_report(scan: Scan, findings: List[Finding], db) -> str:
    """
    Generate a PDF security report for a scan.
    Returns the file path of the generated PDF.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, KeepTogether
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        raise ImportError("reportlab not installed. Run: pip install reportlab")

    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    filename = f"report_scan_{scan.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(settings.REPORTS_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Header ────────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=22,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER,
        spaceAfter=2,
    )

    story.append(Paragraph("🔒 PrivacyLens Security Report", title_style))
    story.append(Paragraph("AI-Based Sensitive Data Exposure Detection", subtitle_style))
    story.append(Paragraph(
        f"Generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e")))
    story.append(Spacer(1, 0.4 * cm))

    # ── Scan Info ─────────────────────────────────────────────────────────
    info_style = ParagraphStyle("InfoKey", parent=styles["Normal"], fontSize=10, spaceAfter=3)
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=10,
        spaceAfter=6,
    )

    story.append(Paragraph("Scan Information", section_style))

    r, g, b = _get_risk_color(scan.risk_level)
    risk_color = colors.Color(r, g, b)

    info_data = [
        ["File Name:", scan.file_name],
        ["Scan Type:", scan.scan_type.upper()],
        ["Scan Date:", scan.scan_date.strftime("%Y-%m-%d %H:%M UTC") if scan.scan_date else "N/A"],
        ["Total Findings:", str(scan.finding_count)],
        ["Risk Score:", f"{scan.risk_score:.1f} / 100"],
        ["Risk Level:", scan.risk_level],
        ["Masking Applied:", "Yes" if scan.is_masked else "No"],
    ]

    info_table = Table(info_data, colWidths=[5 * cm, 12 * cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",   (1, 5), (1, 5), risk_color),
        ("FONTNAME",    (1, 5), (1, 5), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("PADDING",     (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.4 * cm))

    # ── Risk Summary ──────────────────────────────────────────────────────
    story.append(Paragraph("Risk Summary", section_style))
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=6
    )

    from app.services.risk_analyzer import build_risk_summary
    from app.detectors.base import RawFinding

    # Build a lightweight summary without full RawFinding objects
    risk_summary = _build_summary_text(scan)
    story.append(Paragraph(risk_summary, body_style))
    story.append(Spacer(1, 0.3 * cm))

    # ── Category Breakdown ────────────────────────────────────────────────
    if scan.categories:
        story.append(Paragraph("Findings by Category", section_style))
        cat_data = [["Category", "Count", "Severity"]]
        for cat_type, count in sorted(scan.categories.items()):
            severity = get_finding_severity(cat_type)
            cat_data.append([
                cat_type.replace("_", " "),
                str(count),
                severity,
            ])

        cat_table = Table(cat_data, colWidths=[8 * cm, 3 * cm, 6 * cm])
        cat_table.setStyle(TableStyle([
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",      (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("PADDING",       (0, 0), (-1, -1), 7),
            ("ALIGN",         (1, 0), (1, -1), "CENTER"),
        ]))
        story.append(cat_table)
        story.append(Spacer(1, 0.4 * cm))

    # ── Findings Detail ───────────────────────────────────────────────────
    if findings:
        story.append(Paragraph("Detailed Findings", section_style))
        story.append(Paragraph(
            "<i>Note: All sensitive values have been masked in this report.</i>",
            ParagraphStyle("note", parent=styles["Normal"], fontSize=9,
                           textColor=colors.HexColor("#888888"), spaceAfter=8)
        ))

        findings_data = [["#", "Type", "Masked Value", "Location", "Confidence", "Severity"]]
        for idx, f in enumerate(findings, 1):
            findings_data.append([
                str(idx),
                f.type.replace("_", " "),
                f.masked_value[:40] if f.masked_value else "N/A",
                f.location or "N/A",
                f"{f.confidence * 100:.0f}%",
                f.severity,
            ])

        findings_table = Table(
            findings_data,
            colWidths=[1 * cm, 4 * cm, 5 * cm, 3.5 * cm, 2 * cm, 2.5 * cm],
        )
        findings_table.setStyle(TableStyle([
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#16213e")),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
            ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
            ("PADDING",       (0, 0), (-1, -1), 5),
            ("ALIGN",         (4, 0), (4, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("WORDWRAP",      (2, 1), (2, -1), True),
        ]))
        story.append(findings_table)
        story.append(Spacer(1, 0.4 * cm))

    # ── Recommendations ───────────────────────────────────────────────────
    story.append(Paragraph("Recommended Actions", section_style))
    from app.detectors.base import RawFinding as RF

    # Reconstruct minimal finding-type list for recommendations
    class _MinFinding:
        def __init__(self, t): self.type = t
    min_findings = [_MinFinding(f.type) for f in findings]
    recs = build_recommendations(min_findings)

    for rec in recs:
        story.append(Paragraph(f"• {rec}", body_style))

    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))

    # ── Footer ────────────────────────────────────────────────────────────
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#999999"),
        alignment=TA_CENTER,
        spaceBefore=6,
    )
    story.append(Paragraph(
        "This report was generated by PrivacyLens — AI-Based Sensitive Data Exposure Detection System. "
        "For educational and demonstration purposes.",
        footer_style
    ))

    doc.build(story)
    logger.info(f"PDF report generated: {filepath}")
    return filepath


def _build_summary_text(scan: Scan) -> str:
    level = scan.risk_level
    count = scan.finding_count
    score = scan.risk_score

    if level == "CRITICAL":
        return (
            f"This scan identified {count} sensitive data finding(s) with a risk score of "
            f"{score:.1f}/100, classified as CRITICAL. The document contains highly sensitive "
            f"credentials or financial information that must be redacted immediately before sharing."
        )
    elif level == "HIGH":
        return (
            f"This scan identified {count} sensitive data finding(s) with a risk score of "
            f"{score:.1f}/100, classified as HIGH. Government-issued identifiers or financial "
            f"data were detected. Redact before sharing."
        )
    elif level == "MEDIUM":
        return (
            f"This scan identified {count} finding(s) with a risk score of {score:.1f}/100, "
            f"classified as MEDIUM. Personal contact information was detected. "
            f"Review findings before sharing externally."
        )
    else:
        return (
            f"This scan identified {count} finding(s) with a risk score of {score:.1f}/100, "
            f"classified as LOW. Minor personal information detected. Review before sharing."
        )
