# Pelican Python Script to generate a static blog from Evernote notes
# Static blog with theme and RSS support Python 3.10 compatible 
# Reads a direcory of html notes images attachments made by enotes.py
# Uses metadata.json to extract title, tags, author, summary, sentiment, keywords
# TODO: Pelican to Netify Part Two
# TODO: --note_sync_index.json to keep track of notes already processed
# TODO: --add sync and archive notes features
# TODO: --create py script to update NETLIFY vs cli

import os
import json
import shutil
from datetime import datetime
from utils.file_utils import get_notes_folder
from utils.html_summary import html_summary, analyze_sentiment, extract_keywords
from pelican import main as pelican_main
from bs4 import BeautifulSoup

# Configuration
ARTICLES_DIR = get_notes_folder()
PELICAN_CONTENT_DIR = "content"
PELICAN_OUTPUT_DIR = "output"
PELICAN_CONFIG_FILE = "pelicanconf.py"
DEFAULT_THEME = "themes/notmyidea" 
#DEFAULT_THEME = "themes/flex"  
#DEFAULT_THEME = "themes/gum" 
#DEFAULT_THEME = "themes/elegant" 
#DEFAULT_THEME = "themes/octopress" 
#DEFAULT_THEME = "themes/wilson" 
#DEFAULT_THEME = "themes/atilla" 
#DEFAULT_THEME = "themes/hyde" 

def create_pelican_config():
    """
    Generate pelicanconf.py with basic settings.
    """
    config_content = f"""
SITENAME = 'Evernote Notes Blog (Pelican)'
SITEURL = 'https://test.evernoterss.com'  # Adjust this when deploying

PATH = 'content'
TIMEZONE = 'UTC'
DEFAULT_LANG = 'en'
THEME = 'themes/notmyidea'
FEED_ALL_RSS = 'feeds/all.rss.xml'
FEED_ALL_ATOM = 'feeds/all.atom.xml'
DEFAULT_PAGINATION = 10
AUTHOR = "Evernote User"
STATIC_PATHS = ['articles']
STATIC_EXCLUDE_SOURCES = True
PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = []
SUMMARY_MAX_LENGTH = 50  # Adjust this value as needed
RSS_FEED_SUMMARY_ONLY = True  # Include full content in RSS feed
    """

    with open(PELICAN_CONFIG_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(config_content)

def process_article_directory():
    """
    Reads the 'articles' directory, processes each note GUID subdirectory,
    and prepares Pelican-compatible content structure.
    """
    os.makedirs(PELICAN_CONTENT_DIR, exist_ok=True)

    for guid in os.listdir(ARTICLES_DIR):
        guid_path = os.path.join(ARTICLES_DIR, guid)
        if os.path.isdir(guid_path):
            print(f"Processing article with GUID: {guid}")
            process_note_guid(guid_path, guid)
    
    # Manually copy the articles directory to the output directory
    output_articles_dir = os.path.join(PELICAN_OUTPUT_DIR, 'articles')
    if os.path.exists(output_articles_dir):
        shutil.rmtree(output_articles_dir)
    shutil.copytree(ARTICLES_DIR, output_articles_dir)
    print(f"✅ Articles directory copied to: {output_articles_dir}")


def process_note_guid(guid_path, guid):
    """
    Processes a single note GUID directory:
    - Reads note.html
    - Reads metadata.json
    - Updates metadata tags without modifying images/attachments
    """
    meta_file = os.path.join(guid_path, "metadata.json")
    with open(meta_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    title = metadata.get("title", "Untitled").strip()
    created = metadata.get("created_at", datetime.now().strftime('%Y-%m-%d'))
    tags = ",".join(metadata.get("tags", []))  
    author = metadata.get("author", "Unknown Author")  # Prevents author error

    print(f"📄 Processing Note: {title} (GUID: {guid})")

    # Read the HTML content of the note
    note_html_file = os.path.join(guid_path, "note.html")
    with open(note_html_file, 'r', encoding='utf-8') as f:
        note_content = f.read()

    # Generate summary using html_summary function
    summary = html_summary(note_html_file)
    sentiment = analyze_sentiment(note_html_file)
    keywords = extract_keywords(note_html_file)
    tags = keywords + "," + sentiment  

    # **Keep images and attachments inside each note folder!**
    soup = BeautifulSoup(note_content, "html.parser")

    for img in soup.find_all("img"):
        if "src" in img.attrs:
            img_filename = os.path.basename(img["src"])
            img["src"] = f"/articles/{guid}/images/{img_filename}"  # Preserves images path

    for link in soup.find_all("a"):
        if "href" in link.attrs:
            file_name = os.path.basename(link["href"])
            link["href"] = f"/articles/{guid}/attachments/{file_name}"  # Preserves attachments path

    # **Write the final content with updated metadata**
    content_file = os.path.join("content", f"{guid}.html")
    with open(content_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="title" content="{title}">
    <meta name="tags" content="{tags}">
    <meta name="date" content="{created}">
    <meta name="author" content="{author}">
    <meta name="category" content="Evernote Notes">
    <meta name="status" content="published">
    <meta name="summary" content="{summary}">
</head>
<body>
{str(soup)}  <!-- Includes preserved images & attachments -->
</body>
</html>""")

    print(f"✅ Processed and saved: {content_file}")

def generate_static_blog():
    """
    Runs Pelican to generate the static blog from processed content using the Pelican Python API.
    """
    print("Starting Pelican generation...")
    pelican_main([
        PELICAN_CONTENT_DIR,
        '-o', PELICAN_OUTPUT_DIR,
        '-s', PELICAN_CONFIG_FILE
    ])
    print("Pelican generation completed.")

def main():
    """
    Main execution to process articles and generate a simple Pelican blog.
    """
    print("Creating Pelican configuration...")
    create_pelican_config()

    print("Processing articles directory...")
    process_article_directory()

    print("Generating static blog with Pelican API...")
    generate_static_blog()

    print(f"Blog successfully generated at '{PELICAN_OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    main()


