import os
from datetime import datetime, timezone  
from flask import Flask, Response
from feedgen.feed import FeedGenerator
from utils.file_utils import get_notes_folder

# Base folders
NOTES_FOLDER = get_notes_folder()

# Ensure main notes folder exists
os.makedirs(NOTES_FOLDER, exist_ok=True)

def generate_rss():
    """Generate RSS feed from the 10 most recent notes."""
    fg = FeedGenerator()
    fg.title("Evernote Notes RSS")
    fg.link(href="https://test.evernote.com/notes/", rel="self")
    fg.description("RSS feed of saved Evernote notes.")

    # Get sorted list of note directories by modification time
    note_dirs = sorted(
        [d for d in os.listdir(NOTES_FOLDER) if os.path.isdir(os.path.join(NOTES_FOLDER, d))],
        key=lambda x: os.path.getmtime(os.path.join(NOTES_FOLDER, x, "note.html")),
        reverse=True
    )[:10]  # Get 10 most recent notes

    for note_dir in note_dirs:
        note_path = os.path.join(NOTES_FOLDER, note_dir, "note.html")
        if os.path.exists(note_path):
            fe = fg.add_entry()
            fe.title(note_dir.replace("_", " "))
            fe.link(href=f"https://test.evernote.com/notes/{note_dir}/note.html")
            fe.description(f"Read the full note: https://test.evernote.com/notes/{note_dir}/note.html")
            timestamp = os.path.getmtime(note_path)
            pub_date = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone()  # Converts to local time
            fe.pubDate(pub_date)
            

    return fg.rss_str(pretty=True)

app = Flask(__name__)


@app.route('/')
def index():
    indexpage = "<h1>Mikes X13 Notes RSS</h1>"
    indexpage += '<p>This is a <a href="/rss">simple RSS feed</a> of the 10 most recent notes saved to Evernote.</p>'
    return indexpage  

@app.route('/rss')
def rss_feed():
    """Serve the generated RSS feed."""
    rss_content = generate_rss()
    return Response(rss_content, mimetype="application/rss+xml")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)