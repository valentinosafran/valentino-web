# Valentino Šafran — personal CV

A static, responsive CV published from `main` to
[Netlify](https://valentino-web.netlify.app/). No build step, JavaScript,
package installation or third-party font service is needed.

## Preview and edit

Run `python -m http.server 4173 --bind 127.0.0.1` in this folder, then open
http://127.0.0.1:4173/. Edit `index.html` for content and
`assets/css/cv.css` for appearance. Keep the page title, description,
social metadata and `sitemap.xml` date in sync with substantive updates.

The portrait has 200 px and 400 px WebP versions. The original photographs,
Pillar styles and Font Awesome assets remain in the repository for
reference; the page does not request them. Source attribution remains in stylesheet comments and the original assets.

Netlify publishes the repository root using `netlify.toml`. `_headers`
sets security headers, HTML revalidation, and modest asset caching so
subsequent edits can propagate. No hosting account or DNS changes are
required.

## Restore the previous website

The entire refresh is one commit, identified by the annotated tag
`cv-refresh-2026-11-16`. The previous site is preserved at
`before-cv-refresh-2026-11-16` (commit `5683b534838bb04b679859216c5bd1841f2f2fcd`).

To undo the refresh while preserving Git history:

```sh
git pull --ff-only origin main
git revert --no-edit cv-refresh-2026-11-16
git push origin main
```

Netlify's existing Git integration should deploy that revert just like a
normal update. If later edits overlap with the refresh, Git may ask you to
resolve conflicts before completing the revert. No reset or force push is
needed.

To inspect the old site without changing `main`, create a separate
checkout:

```sh
git worktree add ../valentino-web-original before-cv-refresh-2026-11-16
```

## Review and changes — 16 November 2026

The original site already used static HTML, but loaded a 220 KB Bootstrap
theme, a 1.2 MB Font Awesome script and a 709 KB portrait. It also requested
Google Fonts. Several social links were icon-only and lacked accessible
names; the SICRIS link displayed an ORCID icon. The description was simply
"Resume"; the hero image used lazy loading without explicit dimensions.

The refresh retains the slate blue-gray identity and CV format, with
clearer type, section navigation, responsive columns and a readable mobile
layout. Experience is condensed into project contributions; the original
education dates, roles, technologies, languages and interests are retained.
The subtitle is exactly:

> AI & Digital Health Transformation | IoT | Cybersecurity

Changes include:

- A purpose-built 9 KB stylesheet, system fonts and no runtime JavaScript.
- Responsive 4.3 KB / 9.7 KB WebP portraits with reserved dimensions and high
  loading priority.
- Named profile links, a real ORCID link, keyboard focus styles, skip
  navigation, semantic landmarks and print styles.
- Descriptive search and sharing metadata, a canonical URL, Person
  microdata, `robots.txt` and `sitemap.xml`.
- Source-linked project descriptions and four selected publications.
- A Git backup tag and a single reversible refresh commit.

### Content verification

Reviewed public sources as of 16 November 2026. Existing CV claims were
edited for clarity; unverified promotions, credentials, project leadership,
publication counts and new employment were not inferred.

| Update | Source and handling |
| --- | --- |
| PhD student / HUMADEX affiliation | [HUMADEX members](https://humadex.feri.um.si/people/) confirms current PhD-student status. |
| REMERGE exchange with Dextera Consulting, Limassol | [HUMADEX announcement](https://si.linkedin.com/company/humadex/) names Valentino and the exchange. [Official project page](https://humadex.feri.um.si/project/remerge/) confirms the cardiovascular virtual-twin focus. Only the year is shown because the announcement used relative dates. |
| Youth mental-health screening publication | [PLOS Digital Health](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0001069), published 3 April 2026; Valentino is a co-author. |
| Secure FHIR platform publication | [Publisher PDF](https://npublications.com/journals/educationinformation/2025/a282008-0014%282025%29.pdf), published 7 August 2025; Valentino is first author. |
| Robot-assisted clinical decision support publication | [Publisher](https://journals.sagepub.com/doi/abs/10.1177/20552076251339012) and [HUMADEX-hosted paper](https://humadex.feri.um.si/wp-content/uploads/2025/09/safran-et-al-2025-feasibility-of-a-computerized-clinical-decision-support-system-delivered-via-a-socially-assistive.pdf), 2025; Valentino is first author. |
| MRAST publication | [Sensors](https://doi.org/10.3390/s24041101), 2024; Valentino is first author. |
| Alzheimer Europe update | [HUMADEX report](https://humadex.feri.um.si/36-ae-conference-dublin-2/), 2 November 2026. Explicitly labelled group news; it does not claim Valentino attended. |
| Paediatrics outreach | [HUMADEX report](https://humadex.feri.um.si/presenting-medview-certain-and-smile-projects-at-xxxv-srecanje-pediatrov-in-xxii-srecanje-medicinskih-sester-v-pediatriji/), listed on the [SMILE project page](https://humadex.feri.um.si/project/smile-project/) as 20 March 2026; names Valentino and Zala Meklav. |

Group project activity is kept distinct from personal contributions.
SMILE is not labelled as an ongoing project: its official page lists
October 2026 as its end date. Research-project descriptions reflect the
existing CV and the cited sources.

### Validation

Checked in headless Chrome using temporary tools outside the repository:

- Screens at 320, 390, 600, 768, 1024 and 1440 px: no horizontal overflow,
  broken images or missing internal link targets.
- axe WCAG A/AA and best-practice checks: zero automated violations at all
  six widths. Automated testing does not replace a complete manual
  accessibility audit.
- Keyboard skip link, section links, visible focus, 200% text sizing,
  JavaScript-disabled use, print styling and A4 PDF generation checked.
- No browser console or page errors.
- Project/news pages, profile endpoints and DOI links checked. LinkedIn's
  company page, ResearchGate and SAGE restrict automated fetches; their
  URLs were corroborated by public search results. The original designer's
  site also failed the automated fetch and its existing attribution was
  retained.
- Local Lighthouse: desktop 100 performance / 100 accessibility /
  100 best practices / 100 SEO. Isolated mobile run: 99 / 100 / 100 / 100,
  with 1.0 s LCP and zero layout shift. An earlier concurrent run scored
  91 performance; timings vary with host load.
- Core uncompressed first-load files, including HTML and favicon:
  approximately 2.16 MB before versus 44 KB after with the 200 px portrait
  (about 98% smaller). High-density screens may use the 400 px portrait,
  bringing this to about 50 KB. Original Google Fonts downloads are
  excluded from the baseline, so the savings are conservative.

These are local lab measurements, not production field data. The local
preview does not apply Netlify compression or `_headers`; deployment
verification is performed separately after pushing. No test dependencies
or generated QA files are part of the deployed application.
