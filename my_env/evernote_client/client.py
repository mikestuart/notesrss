import time
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.error.ttypes import EDAMSystemException

# Evernote API Token
ACCESS_TOKEN = "S=s19:U=2179ac:E=19bf14952a8:C=194999826a8:P=185:A=personal-0937:V=2:H=6457dd72f33583b68b06cb6117bb02b9"

# Initialize Evernote Client
client = EvernoteClient(token=ACCESS_TOKEN, sandbox=False)
note_store = client.get_note_store()

def fetch_notes(notebook_guid):
    """Fetch notes from a selected Evernote notebook."""
    note_filter = NoteFilter(notebookGuid=notebook_guid)
    result_spec = NotesMetadataResultSpec(includeTitle=True)
    
    notes_metadata = note_store.findNotesMetadata(note_filter, 0, 100, result_spec)
    return notes_metadata.notes

def fetch_note_content(note_guid):
    """Fetch full ENML content including resources, handling rate limits."""
    retry_cnt = 0  # Initial retry delay
    while True:
        try:
            return note_store.getNote(note_guid, True, True, False, False)
        except EDAMSystemException as e:
            if e.errorCode == 19:  # Rate limit error
                retry_cnt += 1
                if retry_cnt < 3:
                    print(f"⏳ Evernote API rate-limited. Waiting {e.rateLimitDuration} seconds...")
                    time.sleep(e.rateLimitDuration)  # Wait the required time
                else:
                    print("❌ Rate retry limit exceeded. Exiting...")
                    return None
            else:
                raise  # Raise any other exception
        except Exception as e:
            print(f"❌ Unexpected error fetching note {note_guid}: {e}")
            return None

def fetch_resource_data(resource_guid):
    """Fetch binary data of a resource (e.g., image, PDF) using correct GUID."""
    try:
        resource = note_store.getResource(resource_guid, True, False, False, False)
        return resource.data.body, resource.mime
    except Exception as e:
        print(f"❌ Error fetching resource {resource_guid}: {e}")
        return None, None
    
    