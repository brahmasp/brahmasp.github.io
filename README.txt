Brahma S. Pavse — personal academic website
https://brahmasp.github.io

----------------------------------------------------------------------
Overview
----------------------------------------------------------------------
Static site hosted on GitHub Pages. The page template/design is adapted
from Kyle Domico's site (https://kyledomico.com), restyled with the
content in css/custom.css. Bootstrap 5 (grid), FontAwesome, and Google
Fonts (EB Garamond / Inter / JetBrains Mono) are loaded from CDNs.

----------------------------------------------------------------------
Layout
----------------------------------------------------------------------
  index.html          Home: header, News, Selected Publications
  publications.html   Full publications list
  css/custom.css      All styling
  img/                Site images (avatar, favicon)
  documents/          CV and paper/bibtex PDFs
  pubs.bib            BibTeX source for ALL publications
  featured.bib        BibTeX source for the Selected Publications block
  refresh_pubs.py     Regenerates the publication HTML from the .bib files
  generate_sitemap.py Regenerates sitemap.xml

----------------------------------------------------------------------
Updating publications
----------------------------------------------------------------------
1. Edit pubs.bib (all papers) and/or featured.bib (homepage highlights).
2. Run:  python3 refresh_pubs.py
   - Rewrites the block between the <!-- PUBLICATIONS_BLOCK --> markers
     in publications.html (grouped by year).
   - Rewrites the block between the <!-- FEATURED_PUBLICATIONS_BLOCK -->
     markers in index.html (flat list, in bib-file order).
3. (Optional) Run:  python3 generate_sitemap.py

Requires: python3 + bibtexparser  (pip install bibtexparser)

BibTeX field notes (read by refresh_pubs.py):
  url    -> "PDF" button     code -> "Code" button     doi -> "DOI"
  slides/video/poster -> matching buttons
  Entry type sets the colored box: inproceedings=conference,
  article=journal, mastersthesis/bachelorsthesis/phdthesis=thesis, etc.
  The author named "Brahma S. Pavse" is bolded automatically.

----------------------------------------------------------------------
Local preview
----------------------------------------------------------------------
  python3 -m http.server 8000   then open http://localhost:8000
