import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from TTS.api import TTS

def generate_audio_for_text(text, output_file, model_name="tts_models/en/vctk/vits", speaker="p225"):
    """
    Generates audio from text using Coqui TTS.
    """
    # Initialize TTS
    # This might need to be done once globally to avoid reloading model
    tts = TTS(model_name=model_name, progress_bar=False, gpu=False) # GPU false for now to be safe, user said "local GPU" but need to check availability
    
    # Generate
    tts.tts_to_file(text=text, file_path=output_file, speaker=speaker)
    return output_file

def create_video_segment(image_path, audio_path, duration=None):
    """
    Creates a video segment with an image and audio.
    """
    audio = AudioFileClip(audio_path)
    if duration:
        # If we want to force duration (e.g. alignment), stretch/cut? 
        # Usually we want audio length to dictate duration
        pass
        
    video = ImageClip(image_path).set_duration(audio.duration)
    video = video.set_audio(audio)
    return video

def generate_final_video(segments, output_file="output/final_video.mp4"):
    """
    Concatenates video segments into final output.
    segments: list of (image_path, audio_path) tuples or ImageClip objects.
    """
    if not os.path.exists("output"):
        os.makedirs("output")
        
    clips = []
    for seg in segments:
        if isinstance(seg, tuple):
            clips.append(create_video_segment(seg[0], seg[1]))
        else:
            clips.append(seg)
            
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_file, fps=24)
