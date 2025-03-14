# Python script to make a blog from a directory of html notes images attachments
# made by e-notes.py. Uses metadata.json to extract title, tags, author, summary,

from flask import Flask, render_template, send_from_directory, abort
from utils.file_utils import get_notes_folder
import os
import json

app = Flask(__name__)
ARTICLES_DIR = get_notes_folder()

@app.route('/')
def index():
    """List all notes by reading metadata.json from each GUID-named folder."""
    notes = []
    for note_folder in os.listdir(ARTICLES_DIR):
        folder_path = os.path.join(ARTICLES_DIR, note_folder)
        if os.path.isdir(folder_path):
            metadata_path = os.path.join(folder_path, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r", encoding="utf-8") as meta_file:
                    metadata = json.load(meta_file)
                    notes.append({
                        "guid": metadata.get("guid", note_folder),
                        "title": metadata.get("title", "Untitled Note"),
                        "summary": metadata.get("summary", "No summary available."),
                        "author": metadata.get("author", "Unknown Author"),
                        "created_at": metadata.get("created_at", "Unknown Date"),
                        "tags": metadata.get("tags", [])
                    })
    return render_template('index.html', notes=notes)

@app.route('/note/<note_guid>/note.html')
def view_note(note_guid):
    """Serve the original note.html file using GUID-based folder structure."""
    note_folder = os.path.join(ARTICLES_DIR, note_guid)
    note_file = os.path.join(note_folder, 'note.html')
    if os.path.exists(note_file):
        return send_from_directory(note_folder, 'note.html')
    else:
        abort(404, description=f"Note with GUID '{note_guid}' not found.")

@app.route('/note/<note_guid>/images/<path:filename>')
def serve_image(note_guid, filename):
    """Serve image files exactly as they are stored."""
    img_folder = os.path.join(ARTICLES_DIR, note_guid, 'images')
    image_path = os.path.join(img_folder, filename)
    if os.path.exists(image_path):
        return send_from_directory(img_folder, filename)
    else:
        abort(404, description="Image not found.")

@app.route('/note/<note_guid>/attachments/<path:filename>')
def serve_attachment(note_guid, filename):
    """Serve attachment files exactly as they are stored."""
    att_folder = os.path.join(ARTICLES_DIR, note_guid, 'attachments')
    attachment_path = os.path.join(att_folder, filename)
    if os.path.exists(attachment_path):
        return send_from_directory(att_folder, filename)
    else:
        abort(404, description="Attachment not found.")

if __name__ == '__main__':
    app.run(debug=True)