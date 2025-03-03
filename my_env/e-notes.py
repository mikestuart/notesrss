import os
import json
import posixpath
from datetime import datetime
from bs4 import BeautifulSoup

# Evernote imports (example)
from evernote_client.client import fetch_notes, fetch_note_content, fetch_resource_data, note_store

# Local utilities
from utils.file_utils import get_notes_folder, sanitize_filename
from utils.html_utils import clean_html, wrap_html_document

ARTICLES_DIR = get_notes_folder()

office_mime_map = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/msword": "doc",
    "application/vnd.ms-excel": "xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.ms-powerpoint": "ppt",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
}

def get_file_extension(mime_type):
    """Return a file extension based on MIME type, with fallback."""
    return office_mime_map.get(mime_type, mime_type.split("/")[-1])

def save_note_as_html(note_metadata):
    """
    Fetches the note from Evernote, saves images/attachments,
    cleans HTML using our updated function, then writes note.html and metadata.json.
    """
    note = note_store.getNote(note_metadata.guid, True, False, False, True)

    note_guid = note.guid
    note_title = note.title.strip()
    note_created = (
        datetime.fromtimestamp(note.created / 1000).strftime('%Y-%m-%d')
        if hasattr(note, 'created') and note.created
        else 'Unknown'
    )

    # Fetch tags
    note_tags = []
    if hasattr(note, 'tagNames') and note.tagNames:
        note_tags = note.tagNames
    elif hasattr(note, 'tagGuids') and note.tagGuids:
        try:
            all_tags = note_store.listTags()
            tag_lookup = {tag.guid: tag.name for tag in all_tags}
            note_tags = [tag_lookup.get(guid, 'Unknown') for guid in note.tagGuids]
        except Exception as e:
            print(f"⚠️ Error retrieving tags: {e}")
    else:
        print("⚠️ No tags found for this note.")

    # Prepare folders
    note_folder = os.path.join(ARTICLES_DIR, note_guid)
    os.makedirs(note_folder, exist_ok=True)
    img_folder = os.path.join(note_folder, "images")
    att_folder = os.path.join(note_folder, "attachments")
    os.makedirs(img_folder, exist_ok=True)
    os.makedirs(att_folder, exist_ok=True)

    # Parse raw ENML
    soup = BeautifulSoup(note.content, "html.parser")

    # Resource map: bodyHash -> resource object
    resource_map = {}
    if note.resources:
        resource_map = {res.data.bodyHash.hex(): res for res in note.resources}

    # 1) Replace <en-media> placeholders with real <img> or <a>
    for media in soup.find_all("en-media"):
        hash_val = media.get("hash")
        if not hash_val:
            continue
        resource = resource_map.get(hash_val)
        if not resource:
            print(f"⚠️ Missing resource for hash: {hash_val}")
            continue

        # get resource data
        file_data, mime_type = fetch_resource_data(resource.guid)
        if not file_data:
            continue

        # choose filename
        if getattr(resource, 'attributes', None) and getattr(resource.attributes, 'fileName', None):
            original_filename = sanitize_filename(resource.attributes.fileName)
        else:
            ext = get_file_extension(mime_type)
            original_filename = f"{resource.guid}.{ext}"

        # save file
        if mime_type.startswith("image/"):
            file_path = os.path.join(img_folder, original_filename)
            web_path = posixpath.join("images", original_filename)
        else:
            file_path = os.path.join(att_folder, original_filename)
            web_path = posixpath.join("attachments", original_filename)

        with open(file_path, "wb") as f:
            f.write(file_data)

        # replace <en-media> with <img> or <a>
        if mime_type.startswith("image/"):
            img_tag = soup.new_tag("img", src=web_path)
            media.replace_with(img_tag)
        else:
            link_tag = soup.new_tag("a", href=web_path)
            link_tag.string = f"Download {original_filename}"
            media.replace_with(link_tag)

    # 2) Convert to string, then run clean_html
    replaced_html = str(soup)
    cleaned_content = clean_html(replaced_html)

    # 3) Wrap with HTML doc
    full_html = wrap_html_document(note_title, cleaned_content)

    # Write final HTML
    html_path = os.path.join(note_folder, "note.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    # Write metadata
    metadata = {
        "title": note_title,
        "guid": note_guid,
        "created_at": note_created,
        "tags": note_tags
    }
    with open(os.path.join(note_folder, "metadata.json"), "w", encoding="utf-8") as meta_file:
        json.dump(metadata, meta_file, indent=4)

    print(f"✅ Note saved: {note_title} (GUID: {note_guid}, Created: {note_created}, Tags: {note_tags})")


# Step 1: List Notebooks
notebooks = note_store.listNotebooks()
for i, nb in enumerate(notebooks):
    print(f"{i+1}. {nb.name} (GUID: {nb.guid})")

choice = int(input("\nSelect a notebook: ")) - 1
selected_notebook_guid = notebooks[choice].guid

# Step 2: Fetch notes from chosen notebook
note_metadatas = fetch_notes(selected_notebook_guid)
for meta in note_metadatas:
    save_note_as_html(meta)

print("\n✅ All notes saved successfully with images/attachments and no Evernote styles!")
