import requests
import sys
import os

# Add current directory to path so we can import backend modules
sys.path.append(os.getcwd())

from backend.ingestion.chunker import chunk_slide
from backend.models.core import Slide

BASE_URL = "http://localhost:8001"
FILE_PATH = "/Users/rob/Development/demoGauntlet/data/AI-Powered_Partnership_Framework.pptx"

def upload_deck():
    print(f"Uploading {FILE_PATH}...")
    try:
        with open(FILE_PATH, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/ingestion/upload", files=files)
            if response.status_code == 200:
                sid = response.json()['session_id']
                print(f"Upload successful. Session ID: {sid}")
                return sid
            else:
                print(f"Upload failed: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Upload Error: {e}")
        return None

def get_slides(session_id):
    print(f"Fetching slides for session {session_id}...")
    try:
        response = requests.get(f"{BASE_URL}/ingestion/session/{session_id}/slides")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get slides: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching slides: {e}")
        return None

def debug_chunking():
    session_id = upload_deck()
    if not session_id:
        return

    slides_data = get_slides(session_id)
    if not slides_data:
        return

    print(f"\n--- Analyzing Chunking for {len(slides_data)} Slides ---\n")

    for s_data in slides_data:
        # Reconstruct Slide object
        slide = Slide(
            index=s_data['index'],
            title=s_data['title'],
            text=s_data['text'],
            notes=s_data.get('notes', ""),
            tags=s_data.get('tags', [])
        )

        print(f"Slide {slide.index + 1}: {slide.title}")
        print(f"Original Text Length: {len(slide.text)} chars")
        
        chunks = chunk_slide(slide)
        print(f"Generated {len(chunks)} chunks:")
        
        for i, chunk in enumerate(chunks):
            print(f"  [{i+1}] {chunk.text[:100]}..." if len(chunk.text) > 100 else f"  [{i+1}] {chunk.text}")
        
        print("-" * 40)

if __name__ == "__main__":
    debug_chunking()
