from urllib.parse import urljoin
import os
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

class SitemapGenerator:
    def __init__(self, base_url):
        """
        Initialize the sitemap generator with the website's base URL.
        
        Args:
            base_url (str): The base URL of the website (e.g., 'https://example.com')
        """
        self.base_url = base_url.rstrip('/')
        self.urls = []

    def add_url(self, loc, lastmod=None, changefreq=None, priority=None):
        """
        Add a URL to the sitemap with optional parameters.
        
        Args:
            loc (str): The URL path relative to the base URL
            lastmod (str/datetime): Last modification date
            changefreq (str): Frequency of changes (always/hourly/daily/weekly/monthly/yearly/never)
            priority (float): Priority of this URL relative to other URLs (0.0 to 1.0)
        """
        url_entry = {
            'loc': urljoin(self.base_url, loc.lstrip('/')),
            'lastmod': lastmod,
            'changefreq': changefreq,
            'priority': priority
        }
        self.urls.append(url_entry)

    def crawl_directory(self, directory, file_patterns=None):
        """
        Crawl a directory to find all HTML files and add them to the sitemap.
        
        Args:
            directory (str): The directory to crawl
            file_patterns (list): List of file extensions to include (default: ['.html'])
        """
        if file_patterns is None:
            file_patterns = ['.html']

        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(pattern) for pattern in file_patterns):
                    # Get file path relative to the directory
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, directory)
                    
                    # Convert Windows path separators to URL format
                    url_path = rel_path.replace(os.path.sep, '/')
                    
                    # Get last modification time
                    lastmod = datetime.fromtimestamp(os.path.getmtime(full_path))
                    lastmod = lastmod.strftime('%Y-%m-%d')
                    
                    # Set priority based on depth and file name
                    depth = len(rel_path.split(os.path.sep)) - 1
                    priority = max(0.5, 1.0 - (depth * 0.2))
                    if file == 'index.html':
                        priority = min(1.0, priority + 0.2)
                    
                    # Set change frequency based on file type and location
                    if 'posts' in rel_path or 'blog' in rel_path:
                        changefreq = 'monthly'
                    elif file == 'index.html':
                        changefreq = 'weekly'
                    else:
                        changefreq = 'monthly'
                    
                    self.add_url(url_path, lastmod, changefreq, priority)

    def generate_sitemap(self):
        """
        Generate the sitemap XML content.
        
        Returns:
            str: Pretty-printed XML string
        """
        # Create the root element
        urlset = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        
        # Add each URL to the sitemap
        for url_entry in self.urls:
            url_element = ET.SubElement(urlset, 'url')
            
            # Add location (required)
            loc = ET.SubElement(url_element, 'loc')
            loc.text = url_entry['loc']
            
            # Add optional elements if they exist
            if url_entry['lastmod']:
                lastmod = ET.SubElement(url_element, 'lastmod')
                lastmod.text = str(url_entry['lastmod'])
            
            if url_entry['changefreq']:
                changefreq = ET.SubElement(url_element, 'changefreq')
                changefreq.text = url_entry['changefreq']
            
            if url_entry['priority']:
                priority = ET.SubElement(url_element, 'priority')
                priority.text = str(url_entry['priority'])
        
        # Convert to string and pretty print
        xml_str = ET.tostring(urlset, encoding='unicode')
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent='  ')
        
        return pretty_xml

    def save_sitemap(self, output_path='sitemap.xml'):
        """
        Save the sitemap to a file.
        
        Args:
            output_path (str): Path where the sitemap.xml file should be saved
        """
        sitemap_content = self.generate_sitemap()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)

def generate_website_sitemap(website_root, base_url, output_path='sitemap.xml'):
    """
    Convenience function to generate a sitemap for a website.
    
    Args:
        website_root (str): Path to the website's root directory
        base_url (str): Base URL of the website
        output_path (str): Where to save the sitemap.xml file
    """
    generator = SitemapGenerator(base_url)
    generator.crawl_directory(website_root)
    generator.save_sitemap(output_path)

# Example usage
if __name__ == "__main__":
    # # Example 1: Manual URL addition
    # generator = SitemapGenerator('https://jcnf.me')
    # generator.add_url('index.html', 
    #                  lastmod=datetime.now().strftime('%Y-%m-%d'),
    #                  changefreq='weekly',
    #                  priority=1.0)
    # generator.add_url('publications.html',
    #                  lastmod=datetime.now().strftime('%Y-%m-%d'),
    #                  changefreq='monthly',
    #                  priority=0.8)
    # generator.save_sitemap()

    # Example 2: Automatic crawling
    generate_website_sitemap(
        website_root='.',
        base_url='https://brahmasp.github.io',
        output_path='sitemap.xml'
    )