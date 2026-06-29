import bibtexparser
from datetime import datetime
from collections import defaultdict
import re

class PublicationHTMLGenerator:
    def __init__(self):
        self.type_to_box = {
            'article': 'journal',
            'inproceedings': 'conference',
            'workshop': 'workshop',
            'preprint': 'preprint',
            'phdthesis': 'thesis',
            'mastersthesis': 'thesis',
            'bachelorsthesis': 'thesis',
            'talk': 'talk',
            'misc': 'technical-report'
        }
        # Fields that shouldn't appear in the final BibTeX citation
        self.excluded_fields = {'slides', 'video', 'code', 'type'}

    def get_publication_type_box(self, entry):
        """Determine the box class based on publication type."""
        entry_type = entry.get('ENTRYTYPE', '').lower()
        custom_type = entry.get('type', '').lower()
        
        if custom_type and custom_type in self.type_to_box:
            return self.type_to_box[custom_type]
        return self.type_to_box.get(entry_type, 'conference')

    def format_authors(self, authors_str, highlight_author="Brahma S. Pavse"):
        """Format the author list with the specified author highlighted."""
        authors = [author.strip().replace("{","").replace("}","") for author in authors_str.split(" and ")]
        formatted_authors = []
        
        for author in authors:
            if author == highlight_author:
                formatted_authors.append(f"<strong>{author}</strong>")
            else:
                formatted_authors.append(author)
        
        return ", ".join(formatted_authors)

    def generate_buttons_section(self, entry):
        """Generate buttons for arxiv and code links."""
        buttons = []
        
        # Add arXiv button if available
        if 'url' in entry:
            buttons.append(
                f'<a href="{entry["url"]}" '
                f'class="btn btn-danger" target="_blank" rel="noopener">'
                f'<i class="fas fa-file-pdf"></i> PDF</a>'
            )
        
        # Add code button if available
        if 'code' in entry:
            buttons.append(
                f'<a href="{entry["code"]}" '
                f'class="btn btn-danger" target="_blank" rel="noopener">'
                f'<i class="fab fa-github"></i> Code</a>'
            )

        if 'doi' in entry:
            buttons.append(
                f'<a href="https://doi.org/{entry["doi"]}" '
                f'class="btn btn-danger" target="_blank" rel="noopener">'
                f'<i class="fas fa-link"></i> DOI</a>'
            )
        
        if 'slides' in entry:
            buttons.append(
                f'<a href="{entry["slides"]}" '
                f'class="btn btn-danger" target="_blank" rel="noopener">'
                f'<i class="fas fa-file-powerpoint"></i> Slides</a>'
            )
        
        if 'video' in entry:
            buttons.append(
                f'<a href="{entry["video"]}" '
                f'class="btn btn-danger" target="_blank" rel="noopener">'
                f'<i class="fas fa-video"></i> Video</a>'
            )

        if 'poster' in entry:
            buttons.append(
                f'<a href="{entry["poster"]}" '
                f'class="btn btn-danger" target="_blank" rel="noopener">'
                f'<i class="fas fa-file-pdf"></i> Poster</a>'
            )
        
        return " ".join(buttons)

    def format_venue(self, entry):
        """Format the venue information."""
        venue = entry.get('booktitle', entry.get('journal', ''))
        if 'year' in entry:
            venue = f"{venue}, {entry['year']}"
        return venue

    def get_clean_bibtex(self, entry):
        """Generate clean BibTeX entry without special fields."""
        # Create a copy of the entry to avoid modifying the original
        clean_entry = entry.copy()
        
        # Remove special fields
        for field in self.excluded_fields:
            clean_entry.pop(field, None)
        
        # Create a new database with just this entry
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = [clean_entry]
        
        # Write to string
        writer = bibtexparser.bwriter.BibTexWriter()
        return writer.write(db)

    def generate_entry_html(self, entry):
        """Generate HTML for a single publication entry."""
        box_type = self.get_publication_type_box(entry)
        title = entry.get('title', '').replace("{", "").replace("}", "")
        authors = self.format_authors(entry.get('author', ''))
        venue = self.format_venue(entry)
        buttons = self.generate_buttons_section(entry)
        entry_id = entry.get('ID', 'unnamed')
        bibtex_content = self.get_clean_bibtex(entry)
        
        html = f"""
                <li>
                    <span class="box {box_type}"></span>
                    <a href="{entry.get('url', '#')}" target="_blank" rel="noopener">{title}</a>
                    <br>
                    <em>{authors}</em><br>
                    {venue}
                    <div class="publication-buttons">
                        {buttons}
                        <label for="{entry_id}" class="btn btn-danger"><i class="fas fa-quote-right"></i> Cite</label>
                    </div>
                    <input type="checkbox" id="{entry_id}" class="toggle-bibtex">
                    <div class="bibtex-content">
                        <pre><code>{bibtex_content}</code></pre>
                    </div>
                </li>"""
        return html

    def generate_publications_html(self, bib_file_path, display_years=True):
        """Generate complete HTML for all publications, grouped by year."""
        with open(bib_file_path) as bibtex_file:
            parser = bibtexparser.bparser.BibTexParser(common_strings=True, ignore_nonstandard_types=False)
            bib_database = bibtexparser.load(bibtex_file, parser=parser)

        # Group entries by year
        entries_by_year = defaultdict(list)
        for entry in bib_database.entries:
            year = entry.get('year', 'No Date')
            entries_by_year[year].append(entry)

        # Sort years in descending order
        sorted_years = sorted(entries_by_year.keys(), reverse=True)

        # Generate CSS and JavaScript
        html = ""
        if display_years:
            for year in sorted_years:
                html += f"\n            <h3>{year}</h3>\n            <ul class=\"pub-list\">\n"
                for entry in sorted(entries_by_year[year], key=lambda x: x.get('month', ''), reverse=True):
                    html += self.generate_entry_html(entry)
                html += "            </ul>\n"

        else:
            html += f"\n            <ul class=\"pub-list\">\n"
            for entry in bib_database.entries:
                html += self.generate_entry_html(entry)
            html += "            </ul>\n"

        return html
    
    def insert_publications_into_file(self, bib_file_path, target_file_path, marker_comment="<!-- PUBLICATIONS_BLOCK -->", display_years=True):
        """
        Generate publications HTML and insert it into the target file at the specified marker comment.
        
        Args:
            bib_file_path (str): Path to the BibTeX file
            target_file_path (str): Path to the target HTML file
            marker_comment (str): Comment that marks where to insert the publications block
        """
        # Generate the publications HTML
        publications_html = self.generate_publications_html(bib_file_path, display_years)
        
        # Read the target file
        with open(target_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Create the pattern to match the marker and any existing content up to the next marker
        pattern = f"({marker_comment}).*?({marker_comment})"
        replacement = f"\\1\n{publications_html}\n\\2"
        
        # Replace the content between markers, or insert if not found
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            print(f"Warning: Marker '{marker_comment}' not found or not properly paired in the target file.")
            return
            
        # Write the modified content back to the file
        with open(target_file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

# Example usage
if __name__ == "__main__":
    generator = PublicationHTMLGenerator()
    
    # Insert publications into target file
    generator.insert_publications_into_file(
        'pubs.bib',
        'publications.html',
        "<!-- PUBLICATIONS_BLOCK -->"
    )

    generator.insert_publications_into_file(
        'featured.bib',
        'index.html',
        "<!-- FEATURED_PUBLICATIONS_BLOCK -->",
        display_years=False
    )