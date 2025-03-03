import os
import re

# ✅ Explicitly set the project folder path (update as needed for cloud deployment)
PROJECT_FOLDER = "E:/EvernoteRSS/"  # 🔄 Change this path when moving to cloud
NOTES_FOLDER = os.path.join(PROJECT_FOLDER, "articles")

def get_notes_folder():
    """Returns the absolute path to the notes folder."""
    os.makedirs(NOTES_FOLDER, exist_ok=True)
    return NOTES_FOLDER

def sanitize_filename(name):
    """Sanitizes filenames to remove invalid characters."""
    name = re.sub(r'[<>:"/\\\\|?*]', "", name)
    name = name.replace(" ", "_")  # Replace spaces with underscores
    return name[:80]  # Trim long names