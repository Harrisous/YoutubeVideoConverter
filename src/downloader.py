import os
import json
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

def download_video(video_url, output_path="temp"):
    """
    Downloads the video using yt-dlp to the output_path.
    Returns the path to the downloaded video file.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    ydl_opts = {
        'format': 'worstvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', # Download low quality video for processing speed
        'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        video_id = info_dict.get("id", None)
        filename = ydl.prepare_filename(info_dict)
    
    return filename, video_id

def download_transcript(video_id, output_path="temp"):
    """
    Downloads the transcript for the given video_id.
    Returns the path to the saved transcript JSON.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    try:
        # transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try fetching English, native or auto-generated
        try:
            transcript = transcript_list.find_transcript(['en']) 
        except:
             # If no english explicit, try auto-translated or any available
             try:
                transcript = transcript_list.find_generated_transcript(['en'])
             except:
                # Fallback to the first available one
                transcript = next(iter(transcript_list))

        fetched_transcript = transcript.fetch()
        
        formatter = JSONFormatter()
        json_formatted = formatter.format_transcript(fetched_transcript)
        
        output_file = os.path.join(output_path, f"{video_id}_transcript.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_formatted)
        
        return output_file
    except Exception as e:
        print(f"Error with youtube_transcript_api: {e}")
        print("Attempting fallback with yt-dlp...")
        
        try:
            ydl_opts = {
                'skip_download': True,
                'writeautomaticsub': True,
                'writesubtitles': True,
                'subtitleslangs': ['en'],
                'subtitlesformat': 'json3',
                'outtmpl': os.path.join(output_path, f"{video_id}"),
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
            
            # yt-dlp saves as video_id.en.json3 check for it
            expected_file = os.path.join(output_path, f"{video_id}.en.json3")
            if os.path.exists(expected_file):
                 # Convert json3 to standard format
                 final_output = os.path.join(output_path, f"{video_id}_transcript.json")
                 try:
                     with open(expected_file, 'r', encoding='utf-8') as f:
                         data = json.load(f)
                     
                     transcript = []
                     for event in data.get('events', []):
                         if 'segs' in event:
                             text = "".join([seg.get('utf8', '') for seg in event['segs']])
                             start = event.get('tStartMs', 0) / 1000.0
                             duration = event.get('dDurationMs', 0) / 1000.0
                             if text.strip():
                                 transcript.append({
                                     'text': text,
                                     'start': start,
                                     'duration': duration
                                 })
                     
                     with open(final_output, 'w', encoding='utf-8') as f:
                         json.dump(transcript, f, indent=2)
                     
                     return final_output
                 except Exception as e3:
                     print(f"Error converting json3: {e3}")
                     return expected_file # Return original if conversion fails
            
            return None
        except Exception as e2:
            print(f"Error with yt-dlp fallback: {e2}")
            return None
