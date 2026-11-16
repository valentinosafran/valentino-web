#!/usr/bin/env python3
"""Generate EN/HR/SL static pages using only Python's standard library.

Edit site/content.json for website copy and cv/content.json for shared CV
translations. Run from the repository root: python scripts/site/build_pages.py
Saved pages are served directly; no runtime JavaScript is required.
"""
import hashlib
import json
from html import escape
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).parent
ORIGIN = "https://valentino-web.netlify.app"
PATHS = {"en": "/", "hr": "/hr/", "sl": "/sl/"}
PROJECT_URLS = [
    ["https://humadex.feri.um.si/project/remerge/"],
    ["https://humadex.feri.um.si/project/smile-project/", "https://humadex.feri.um.si/project/ai4hope-project/"],
    ["https://humadex.feri.um.si/project/hosmart-ai/"],
    [],
    ["https://humadex.feri.um.si/project/persist-project/"],
]
LANGUAGES = {"en": "English", "hr": "Hrvatski", "sl": "Slovenščina"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def e(text):
    return escape(str(text), quote=True)


def project_blocks(cv, site):
    blocks = []
    for index, (project, content) in enumerate(zip(cv["projects"], site["projects"], strict=True)):
        names = project["name"].split(" & ")
        urls = PROJECT_URLS[index]
        title = " &amp; ".join(
            f'<a href="{e(urls[n])}">{e(name)}</a>' if n < len(urls) else e(name)
            for n, name in enumerate(names)
        )
        paragraphs = "\n".join(f'              <p>{e(text)}</p>' for text in content.get("paragraphs", []))
        if content.get("bullets"):
            items = "\n".join(f'                <li>{e(text)}</li>' for text in content["bullets"])
            paragraphs += f'\n              <ul class="contributions">\n{items}\n              </ul>'
        if content.get("source"):
            paragraphs += ('\n              <a class="source-link" href="https://www.linkedin.com/company/humadex/">'
                           f'{e(content["source"])} <span aria-hidden="true">↗</span></a>')
        blocks.append(f'''
            <div class="project">
              <h4>{title} <span class="project-label">{e(project["focus"])}</span></h4>
{paragraphs}
            </div>''')
    blocks.append(f'''
            <div class="project">
              <h4>{e(cv["teachingTitle"])}</h4>
              <p>{e(cv["teaching"])}</p>
            </div>''')
    return "\n".join(blocks)


def build_page(code, cv, site, publications, template, css_version):
    root = "" if code == "en" else "../"
    values = {key: e(value) for key, value in {**cv, **site}.items() if isinstance(value, str)}
    values.update(code=code, upperCode=code.upper(), root=root,
                  canonical=ORIGIN + PATHS[code], cssVersion=css_version,
                  locale=cv["locale"].replace("-", "_"),
                  universityName=e(cv["university"].split(" · ")[0]),
                  period=e(cv["period"].replace(" - ", "–")))
    values["alternates"] = "\n".join(
        f'  <link rel="alternate" hreflang="{lang}" href="{ORIGIN}{path}">'
        for lang, path in {**PATHS, "x-default": "/"}.items()
    )
    language_links = []
    for lang, path in PATHS.items():
        current = ' aria-current="page"' if lang == code else ""
        language_links.append(
            f'          <li><a href="{path}" hreflang="{lang}" lang="{lang}" '
            f'title="{e(LANGUAGES[lang])}"{current}>{lang.upper()}</a></li>'
        )
    values["languageLinks"] = "\n".join(language_links)
    # These editorial paragraphs deliberately contain the institution links.
    values["aboutParagraphs"] = "\n".join(f"        <p>{text}</p>" for text in site["about"])
    values["projects"] = project_blocks(cv, site)
    values["expertise"] = "\n".join(
        f'              <div><dt>{e(title)}</dt><dd>{e(description)}</dd></div>'
        for title, description in cv["expertise"]
    )
    values["education"] = "\n".join(
        f'              <li><h3>{e(title)}</h3><p>{e(cv["university"])}</p>'
        f'<p class="meta">{e(period.replace(" - ", "–"))}</p></li>'
        for title, period in cv["degrees"]
    )
    values["languages"] = "\n".join(
        f'              <div><dt>{e(name)}</dt><dd>{e(level)}</dd></div>'
        for name, level in zip(site["languageNames"], site["languageLevels"], strict=True)
    )
    if len(site["publicationDescriptions"]) != len(publications):
        raise ValueError(f"{code}: translate every publication description.")
    values["publications"] = "\n".join(
        f'''              <li>
                <p class="publication-meta"><time datetime="{e(pub["date"])}">{e(pub["year"])}</time> · <span lang="en">{e(pub["journal"])}</span> · {e(cv[pub["authorRole"]])}</p>
                <h3><a href="https://doi.org/{e(pub["doi"])}" lang="en">{e(pub["title"])} <span aria-hidden="true">↗</span></a></h3>
                <p>{e(description)}</p>
              </li>'''
        for pub, description in zip(publications, site["publicationDescriptions"], strict=True)
    )
    target = ROOT / ("index.html" if code == "en" else f"{code}/index.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template.substitute(values), encoding="utf-8")
    print(f"Built {code.upper()}: {target.relative_to(ROOT)}")


def main():
    content = read_json(SOURCE / "content.json")
    cv_content = read_json(SOURCE.parent / "cv/content.json")
    publications = read_json(SOURCE / "publications.json")
    template = Template((SOURCE / "page.template.html").read_text(encoding="utf-8-sig"))
    css_version = hashlib.sha256((ROOT / "assets/css/cv.css").read_bytes()).hexdigest()[:12]
    if set(content) != set(PATHS) or set(cv_content) != set(PATHS):
        raise ValueError("Website and CV translations must cover EN, HR and SL.")
    for code in PATHS:
        build_page(code, cv_content[code], content[code], publications, template, css_version)
    urls = "\n".join(f"  <url><loc>{ORIGIN}{path}</loc></url>" for path in PATHS.values())
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + urls + "\n</urlset>\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
