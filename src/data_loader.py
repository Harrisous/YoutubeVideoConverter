import json
import os

def load_video_urls(json_path="video_url.json"):
    """
    Loads the video URL mapping from the JSON file.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    return data

def verify_slides_exist(data, slides_dir="slides"):
    """
    Verifies that all referenced slides exist in the slides directory.
    Returns a list of missing files.
    """
    missing = []
    for entry in data:
        slides = entry.get("slides", {})
        for key, filename in slides.items():
            if not os.path.exists(os.path.join(slides_dir, filename)):
                missing.append(filename)
    return missing
