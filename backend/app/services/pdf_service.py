"""Renders a student's application profile as a PDF (ReportLab, in memory)."""

from datetime import datetime, timezone
from io import BytesIO
from typing import List, Optional, Sequence, Tuple
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.student_profile import StudentProfile

_BRAND = colors.HexColor("#1d4ed8")
_MUTED = colors.HexColor("#64748b")
_RULE = colors.HexColor("#e2e8f0")
_LABEL_BG = colors.HexColor("#f8fafc")

_styles = getSampleStyleSheet()
_TITLE = ParagraphStyle("AppTitle", parent=_styles["Title"], alignment=TA_LEFT, fontSize=20, leading=24, textColor=_BRAND, spaceAfter=2)
_SUBTITLE = ParagraphStyle("AppSubtitle", parent=_styles["Normal"], fontSize=10, textColor=_MUTED, spaceAfter=10)
_HEADING = ParagraphStyle("AppHeading", parent=_styles["Heading2"], fontSize=13, leading=16, textColor=_BRAND, spaceBefore=12, spaceAfter=6)
_LABEL = ParagraphStyle("AppLabel", parent=_styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#334155"))
_VALUE = ParagraphStyle("AppValue", parent=_styles["Normal"], fontSize=10, leading=14)
_BODY = ParagraphStyle("AppBody", parent=_VALUE, spaceAfter=6)

Row = Tuple[str, Optional[str]]


def _text(value: Optional[str]) -> str:
    """Escapes user input for ReportLab's mini-markup and keeps line breaks."""
    return escape(value.strip()).replace("\r\n", "\n").replace("\n", "<br/>")


def _value(value: Optional[str], link: bool = False) -> Paragraph:
    if value is None or not value.strip():
        return Paragraph('<font color="#64748b">Not provided</font>', _VALUE)
    text = _text(value)
    if link and value.strip().lower().startswith(("http://", "https://")):
        href = escape(value.strip(), {'"': "&quot;"})
        text = f'<link href="{href}" color="#1d4ed8"><u>{text}</u></link>'
    return Paragraph(text, _VALUE)


def _table(rows: Sequence[Tuple[str, Paragraph]]) -> Table:
    data = [[Paragraph(escape(label), _LABEL), value] for label, value in rows]
    table = Table(data, colWidths=[52 * mm, None], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), _LABEL_BG),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, _RULE),
        ("BOX", (0, 0), (-1, -1), 0.5, _RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def _section(title: str, rows: Sequence[Row], links: Sequence[str] = ()) -> List:
    cells = [(label, _value(value, link=label in links)) for label, value in rows]
    return [KeepTogether([Paragraph(escape(title), _HEADING), _table(cells)])]


def _long_text(title: str, value: Optional[str]) -> List:
    if value is None or not value.strip():
        return []
    return [Paragraph(escape(title), _LABEL), Spacer(1, 2), Paragraph(_text(value), _BODY)]


def _applicant_name(profile: StudentProfile) -> str:
    parts = [p.strip() for p in (profile.first_name, profile.last_name) if p and p.strip()]
    return " ".join(parts) or (profile.full_name or "").strip() or "Applicant"


def _footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(_MUTED)
    canvas.drawString(doc.leftMargin, 12 * mm, f"ApplyCM application profile: {doc.applicant_name}")
    canvas.drawRightString(A4[0] - doc.rightMargin, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_application_pdf(profile: StudentProfile, generated_at: Optional[datetime] = None) -> bytes:
    generated_at = generated_at or datetime.now(timezone.utc)
    name = _applicant_name(profile)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=22 * mm,
        title=f"Application profile - {name}",
        author="ApplyCM",
        subject="Student application profile",
    )
    doc.applicant_name = name

    story: List = [
        Paragraph("ApplyCM - Student Application Profile", _TITLE),
        Paragraph(f"{escape(name)} &nbsp;|&nbsp; Generated {generated_at.strftime('%d %B %Y, %H:%M UTC')}", _SUBTITLE),
    ]

    story += _section("Personal details", [
        ("First name", profile.first_name),
        ("Last name", profile.last_name),
        ("Email", profile.email),
        ("Phone", profile.phone),
        ("Region of origin", profile.declared_state),
    ])
    story += _section("Contact", [
        ("Address", profile.address),
        ("City", profile.city),
        ("Region", profile.region),
        ("Emergency contact", profile.emergency_contact_name),
        ("Emergency contact phone", profile.emergency_contact_phone),
    ])
    story += _section("Education", [
        ("Secondary school", profile.secondary_school),
        ("O-Level result slip", profile.o_level_slip_url),
        ("A-Level result slip", profile.a_level_slip_url),
    ], links=("O-Level result slip", "A-Level result slip"))

    testing = [profile.o_level_passes, profile.a_level_points, profile.english_test_type, profile.english_test_score]
    if any(v and v.strip() for v in testing):
        story += _section("Testing", [
            ("O-Level passes", profile.o_level_passes),
            ("A-Level points", profile.a_level_points),
            ("English test", profile.english_test_type),
            ("English test score", profile.english_test_score),
        ])

    story += _section("Activities and experiences", [
        ("Activity", profile.activity_name),
        ("Role", profile.activity_role),
        ("Description", profile.activity_description),
        ("Honors and awards", profile.honors_awards),
    ])

    story.append(Paragraph("Writing", _HEADING))
    story.append(_table([("Essay prompt", _value(profile.essay_prompt))]))
    story.append(Spacer(1, 8))
    story += _long_text("Personal statement", profile.writing_sample)
    story += _long_text("Additional information", profile.additional_info)

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()


def application_pdf_filename(profile: StudentProfile) -> str:
    safe = "".join(c if c.isascii() and c.isalnum() else "_" for c in _applicant_name(profile)).strip("_") or "applicant"
    return f"ApplyCM_Application_{safe}.pdf"
