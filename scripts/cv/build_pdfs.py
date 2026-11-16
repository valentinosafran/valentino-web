#!/usr/bin/env python3
"""Build the three static CV downloads. Requires reportlab and pypdf.

Run from the repository root: python scripts/cv/build_pdfs.py
Use --font-dir for a directory containing Segoe UI or DejaVu Sans TTFs.
Publication titles, journals and DOIs are read from the current website.
"""
import argparse
import io
import json
import os
from html import escape
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf"
SITE = "https://valentino-web.netlify.app/"
EMAIL = "valentino.safran@gmail.com"
INK = colors.HexColor("#263646")
MUTED = colors.HexColor("#526372")
ACCENT = colors.HexColor("#305d7b")
LINE = colors.HexColor("#dce2e7")
W, H = A4
MARGIN = 18 * mm
WIDTH = W - MARGIN * 2


class PublicationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_publications = False
        self.capture = None
        self.publications = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "ol" and attrs.get("class") == "publications":
            self.in_publications = True
        if not self.in_publications:
            return
        if tag == "li":
            self.current = {}
        if tag == "p" and attrs.get("class") == "publication-meta":
            self.capture = "meta"
        if tag == "a" and self.current is not None and attrs.get("href", "").startswith("https://doi.org/"):
            self.current["url"] = attrs["href"]
            self.capture = "title"

    def handle_data(self, data):
        if self.in_publications and self.capture and self.current is not None:
            self.current[self.capture] = self.current.get(self.capture, "") + data

    def handle_endtag(self, tag):
        if tag in ("p", "a"):
            self.capture = None
        if self.in_publications and tag == "li" and self.current:
            self.current["title"] = self.current["title"].replace("\u2197", "").strip()
            self.current["meta"] = self.current["meta"].strip()
            self.publications.append(self.current)
            self.current = None
        if tag == "ol":
            self.in_publications = False


def register_fonts(font_dir=None):
    candidates = [
        Path(font_dir) if font_dir else Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
        Path("/usr/share/fonts/truetype/dejavu"),
    ]
    for directory in candidates:
        for regular, bold in (("segoeui.ttf", "segoeuib.ttf"), ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf")):
            if (directory / regular).exists() and (directory / bold).exists():
                pdfmetrics.registerFont(TTFont("CV", str(directory / regular)))
                pdfmetrics.registerFont(TTFont("CV-Bold", str(directory / bold)))
                pdfmetrics.registerFontFamily("CV", normal="CV", bold="CV-Bold", italic="CV", boldItalic="CV-Bold")
                return
    raise SystemExit("Supply --font-dir with Segoe UI or DejaVu Sans regular/bold TTF files.")


def style(name, size, leading, **kwargs):
    return ParagraphStyle(name, fontName="CV", fontSize=size, leading=leading,
                          textColor=INK, alignment=TA_LEFT, **kwargs)


STYLES = {
    "body": style("body", 9.4, 13.4, spaceAfter=7),
    "project": style("project", 9.25, 13.1, spaceAfter=0),
    "role": style("role", 11.5, 16, spaceAfter=3),
    "small": style("small", 8.4, 12, spaceAfter=3),
    "skill": style("skill", 9, 12.8, spaceAfter=8),
    "pubTitle": style("pubTitle", 9.6, 13.5, spaceAfter=3),
    "pubMeta": style("pubMeta", 8.1, 11.3, spaceAfter=3),
    "doi": style("doi", 8.2, 11.3),
}
STYLES["projectTitle"] = style("projectTitle", 10, 14, spaceAfter=3)
STYLES["projectTitle"].textColor = ACCENT
STYLES["small"].textColor = MUTED
STYLES["pubMeta"].textColor = MUTED
STYLES["doi"].textColor = ACCENT


def p(text, key="body", raw=False):
    return Paragraph(text if raw else escape(text), STYLES[key])


def heading(text):
    s = style("heading", 10, 14, spaceBefore=0, spaceAfter=6)
    return [
        Paragraph("<b>" + escape(text.upper()) + "</b>", s),
        HRFlowable(width="100%", thickness=.6, color=LINE, spaceAfter=10),
    ]


def link(label, url):
    return '<a href="' + escape(url, quote=True) + '" color="#305d7b">' + escape(label) + "</a>"


def header(canvas, doc):
    d = doc.cv_data
    canvas.saveState()
    canvas.setTitle("Valentino Šafran | CV | " + d["language"])
    canvas.setAuthor("Valentino Šafran")
    canvas.setSubject(d["subtitle"])
    if doc.page == 1:
        x, y = MARGIN, H - 20 * mm
        canvas.setFillColor(ACCENT)
        canvas.setFont("CV-Bold", 8)
        canvas.drawString(x, y, "HUMADEX  /  UM FERI")
        canvas.setFillColor(INK)
        canvas.setFont("CV-Bold", 29)
        canvas.drawString(x, y - 34, "Valentino Šafran")
        canvas.setFont("CV", 11)
        canvas.drawString(x, y - 54, d["role"])
        sub = Paragraph(escape(d["subtitle"]), style("header-subtitle", 9.1, 13))
        _, sh = sub.wrap(WIDTH - 34 * mm, 50)
        sub.drawOn(canvas, x, y - 67 - sh)
        contact_y = y - 77 - sh
        canvas.setFont("CV", 8.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(x, contact_y, EMAIL + "  |  " + d["location"])
        canvas.linkURL("mailto:" + EMAIL, (x, contact_y - 2, x + 124, contact_y + 10), relative=0)
        photo_size = 28 * mm
        photo_x, photo_y = W - MARGIN - photo_size, y - photo_size + 3
        canvas.saveState()
        clip = canvas.beginPath()
        clip.roundRect(photo_x, photo_y, photo_size, photo_size, 3)
        canvas.clipPath(clip, stroke=0, fill=0)
        canvas.drawImage(doc.cv_photo, photo_x, photo_y, width=photo_size, height=photo_size, mask="auto")
        canvas.restoreState()
        rule_y = H - 62 * mm
    else:
        canvas.setFillColor(INK)
        canvas.setFont("CV-Bold", 14)
        canvas.drawString(MARGIN, H - 21 * mm, "Valentino Šafran")
        canvas.setFillColor(MUTED)
        canvas.setFont("CV", 8.4)
        canvas.drawRightString(W - MARGIN, H - 21 * mm, d["role"])
        rule_y = H - 26 * mm
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(.6)
    canvas.line(MARGIN, rule_y, W - MARGIN, rule_y)
    canvas.line(MARGIN, 15 * mm, W - MARGIN, 15 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("CV", 7.6)
    canvas.drawString(MARGIN, 10 * mm, "valentino-web.netlify.app")
    canvas.linkURL(SITE, (MARGIN, 9 * mm, MARGIN + 150, 13 * mm), relative=0)
    canvas.drawRightString(W - MARGIN, 10 * mm, d["language"] + "  |  " + str(doc.page) + " / 2")
    canvas.restoreState()


def build(code, data, publications):
    buffer = io.BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=18 * mm, bottomMargin=20 * mm, pageCompression=1,
                          allowSplitting=1)
    doc.cv_data = data
    with Image.open(ROOT / "assets/images/valentino-safran-400.webp") as image:
        photo_bytes = io.BytesIO()
        image.convert("RGB").save(photo_bytes, "JPEG", quality=88)
    photo_bytes.seek(0)
    doc.cv_photo = ImageReader(photo_bytes)
    first = Frame(MARGIN, 20 * mm, WIDTH, H - 86 * mm, leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0, id="first")
    second = Frame(MARGIN, 20 * mm, WIDTH, H - 51 * mm, leftPadding=0, rightPadding=0,
                   topPadding=0, bottomPadding=0, id="second")
    doc.addPageTemplates([
        PageTemplate(id="First", frames=first, onPage=header, autoNextPageTemplate="Later"),
        PageTemplate(id="Later", frames=second, onPage=header),
    ])
    story = []
    story += heading(data["profileTitle"])
    story += [p(data["profile"]), Spacer(1, 7)]
    story += heading(data["experienceTitle"])
    story += [
        p("<b>" + escape(data["job"]) + "</b>", "role", True),
        p("<b>" + escape(data["period"]) + "</b>  |  " + escape(data["affiliation"]), "small", True),
        p(data["lab"], "small"), Spacer(1, 9),
    ]
    for project in data["projects"]:
        story.append(KeepTogether([
            p("<b>" + escape(project["name"]) + "</b>  |  " + escape(project["focus"]), "projectTitle", True),
            p(project["text"], "project"), Spacer(1, 10),
        ]))
    story.append(KeepTogether([
        p("<b>" + escape(data["teachingTitle"]) + "</b>", "projectTitle", True),
        p(data["teaching"], "project"),
    ]))
    story.append(PageBreak())

    left = heading(data["expertiseTitle"])
    for title, description in data["expertise"]:
        left.append(p("<b>" + escape(title) + "</b><br/>" + escape(description), "skill", True))
    right = heading(data["educationTitle"])
    for degree, period in data["degrees"]:
        right += [p("<b>" + escape(degree) + "</b>", "skill", True),
                  p(data["university"] + " | " + period, "small"), Spacer(1, 4)]
    right += [Spacer(1, 3), p("<b>" + escape(data["trainingTitle"]) + "</b><br/>" + escape(data["training"]), "skill", True)]
    right += [Spacer(1, 4), p("<b>" + escape(data["languagesTitle"]) + "</b><br/>" + data["languages"], "skill", True)]
    columns = Table([[left, "", right]], colWidths=[WIDTH * .54, WIDTH * .055, WIDTH * .405])
    columns.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story += [columns, Spacer(1, 14)]
    story += heading(data["publicationsTitle"])
    for pub in publications:
        year, journal, role = [part.strip() for part in pub["meta"].split("·")]
        role = data["firstAuthor"] if role == "First author" else data["coAuthor"]
        story.append(KeepTogether([
            p("<b>" + escape(pub["title"]) + "</b>", "pubTitle", True),
            p(year + "  |  " + journal + "  |  " + role, "pubMeta"),
            p(link(pub["url"].replace("https://", ""), pub["url"]), "doi", True),
            Spacer(1, 11),
        ]))
    story += [Spacer(1, 1), p(link(data["bibliography"], "https://cris.cobiss.net/ecris/si/en/researcher/51746") +
                "  |  " + link("ORCID", "https://orcid.org/0000-0002-3664-3564") +
                "  |  " + link("LinkedIn", "https://linkedin.com/in/valentino-safran"), "small", True)]
    story += [Spacer(1, 9), p("<b>" + escape(data["interestsTitle"]) + "</b><br/>" + escape(data["interests"]), "small", True)]
    doc.build(story)
    buffer.seek(0)
    reader = PdfReader(buffer)
    if len(reader.pages) != 2:
        raise RuntimeError(f"{code}: expected 2 pages; got {len(reader.pages)}")
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer._root_object[NameObject("/Lang")] = TextStringObject(data["locale"])
    writer.add_metadata({"/Title": "Valentino Šafran - CV - " + data["language"],
                         "/Author": "Valentino Šafran", "/Subject": data["subtitle"]})
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"valentino-safran-cv-{code}.pdf"
    with target.open("wb") as output:
        writer.write(output)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if "Valentino Šafran" not in text or "\ufffd" in text or "\u25a0" in text:
        raise RuntimeError(f"{code}: PDF text or diacritics verification failed")
    print(json.dumps({"language": code, "pages": 2, "bytes": target.stat().st_size,
                      "path": str(target)}, ensure_ascii=False))


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--font-dir")
    options = args.parse_args()
    register_fonts(options.font_dir)
    parser = PublicationParser()
    parser.feed((ROOT / "index.html").read_text(encoding="utf-8-sig"))
    if len(parser.publications) != 4:
        raise RuntimeError("Expected four selected publications in index.html; review the PDF layout if this changes.")
    languages = json.loads((Path(__file__).parent / "content.json").read_text(encoding="utf-8-sig"))
    for code, data in languages.items():
        build(code, data, parser.publications)


if __name__ == "__main__":
    main()
