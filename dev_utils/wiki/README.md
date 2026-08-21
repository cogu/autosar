# AUTOSAR XML Tag Index Generator

This directory contains automation tooling for generating the GitHub Wiki XML Tag Index Markdown page ([`xml_index.md`](xml_index.md)) directly from the implementation cache (`dev_utils/.implementation_cache.json`).

## Workflow

### 1. Refresh Implementation Cache (Automatic or Manual)
The cache indexes all Python classes in `src/autosar/xml/element.py`, extracting their XML Tag variants, Element Categories (from grouping comments `# ---`), package element status, and introduction release version:

```bash
python dev_utils/refresh_implementation.py
```

### 2. Generate the Wiki Page
Generate [`xml_index.md`](xml_index.md) by extracting the cached tags and rendering the Jinja2 template ([`templates/xml_index.md.jinja2`](templates/xml_index.md.jinja2)):

```bash
python dev_utils/wiki/generate_wiki_page.py
```

To refresh the cache and regenerate the page in one step:
```bash
python dev_utils/wiki/generate_wiki_page.py --refresh
```

---

## Diagnostics

* **`inspect_tags.py`**: Scans `autosar.xml.element` against `.implementation_cache.json` and git release history:
  ```bash
  python dev_utils/wiki/inspect_tags.py
  ```
