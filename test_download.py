
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.data_loader import load_video_urls
from src.downloader import download_video, download_transcript

def test_pipeline():
    print("Testing Data Loader...")
    data = load_video_urls()
    print(f"Loaded {len(data)} entries.")
    
    first_entry = data[0]
    video_url = first_entry['video_url']
    print(f"Testing Downloader for {video_url}...")
    
    # Test Transcript
    print("Downloading transcript...")
    # extracting video ID from URL for test (simplified)
    # The real downloader extracts it via yt-dlp, but let's see if we can just test download_video which returns ID
    
    video_path, video_id = download_video(video_url)
    print(f"Video downloaded to {video_path}, ID: {video_id}")
    
    if video_id:
        transcript_path = download_transcript(video_id)
        print(f"Transcript downloaded to {transcript_path}")

if __name__ == "__main__":
    test_pipeline()
