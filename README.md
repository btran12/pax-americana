# Pax Americana

**[paxamericana.xyz](https://paxamericana.xyz/)** — A comprehensive interactive record of every U.S. military intervention from 1776 to the present.

## Overview

Pax Americana is a static web application that documents and visualizes United States military interventions across 249 years of history. It covers wars declared and undeclared, invasions, bombing campaigns, occupations, coups, and proxy conflicts against 34 nations.

## Features

- **Interactive conflict list** — Browse and filter 400+ interventions by type (war, invasion, bombing, coup, occupation, naval)
- **Detail panel** — Each conflict includes a full description, key statistics (casualties, cost, duration, troops deployed), key facts, and an outcome/legacy summary
- **Conflict timeline** — A scrollable, zoomable timeline spanning 1776–present with color-coded event markers; supports both mouse drag and touch swipe on mobile
- **Countries attacked** — A reference grid listing all 34 countries targeted, with year ranges
- **Live data** — Active 2026 operations flagged in real time; Brent crude oil price fetched live for the Iran conflict entry
- **Search & filter** — Instant search by conflict name or country, combined with type filters

## Stats (as of 2026)

| Stat | Value |
|------|-------|
| Total interventions | ~400+ |
| Years at war (of 249) | 229 |
| Estimated total cost | $11.7 trillion |
| Estimated foreign deaths | ~4 million+ |
| Countries attacked | 34 |
| Active operations (2026) | 4 |

## Tech Stack

Pure HTML, CSS, and vanilla JavaScript — no frameworks, no build step. Deployed as a static site via GitHub Pages.

- **Fonts**: Bebas Neue, DM Mono, Libre Baskerville (Google Fonts)
- **Data**: Hardcoded JSON array in `script.js`
- **Hosting**: GitHub Pages (`CNAME` → `paxamericana.xyz`)

## File Structure

```
index.html     — Markup and structured data (SEO/Open Graph)
styles.css     — All styling, including responsive mobile layout
script.js      — Event data, rendering logic, filters, timeline, and interactions
favicon.svg    — Site icon
robots.txt     — Search crawler directives
sitemap.xml    — XML sitemap for SEO
CNAME          — Custom domain for GitHub Pages
```

## Running Locally

No build step required. Open `index.html` directly in a browser, or serve with any static file server:

```bash
npx serve .
# or
python3 -m http.server 8080
```

## License

Data is presented for historical and educational purposes. All content is original editorial work.
