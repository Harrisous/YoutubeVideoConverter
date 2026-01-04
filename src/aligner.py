import os
import cv2
import imagehash
from PIL import Image
import numpy as np

def calculate_image_hash(image_path):
    """
    Calculates the perceptual hash of an image.
    File path input.
    """
    img = Image.open(image_path)
    return imagehash.phash(img)

def calculate_frame_hash(frame):
    """
    Calculates hash of an OpenCV frame (numpy array).
    """
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return imagehash.phash(img)

def find_slide_transitions(video_path, slide_images_paths):
    """
    Analyzes the video to find when each slide appears.
    
    Args:
        video_path: Path to the downloaded low-res video.
        slide_images_paths: List of paths to the high-res PDF slide images (in order).
        
    Returns:
        List of dicts: [{'slide_index': 0, 'start_time': 0.0, 'end_time': 15.4}, ...]
    """
    # Calculate hashes for all ground-truth slides
    slide_hashes = [calculate_image_hash(p) for p in slide_images_paths]
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video {video_path}")
        return []
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    transitions = []
    current_slide_idx = -1
    
    # We don't need to check every single frame, maybe every 0.5 or 1 second is enough
    step_frames = int(fps * 1.0) 
    
    for frame_idx in range(0, frame_count, step_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break
            
        timestamp = frame_idx / fps
        frame_hash = calculate_frame_hash(frame)
        
        # Find best matching slide
        best_match_idx = -1
        min_diff = 100 # High initial value
        
        for i, s_hash in enumerate(slide_hashes):
            diff = frame_hash - s_hash
            if diff < min_diff:
                min_diff = diff
                best_match_idx = i
        
        # Threshold for matching (hamming distance)
        # phash returns 0-64. < 10-15 is usually a good match.
        if min_diff < 15:
            if best_match_idx != current_slide_idx:
                # Transition detected
                # If we had a previous slide, close it
                if current_slide_idx != -1 and transitions:
                    transitions[-1]['end_time'] = timestamp
                
                # Start new slide
                transitions.append({
                    'slide_index': best_match_idx,
                    'start_time': timestamp,
                    'end_time': duration, # Default to end, will update
                    'slide_path': slide_images_paths[best_match_idx]
                })
                current_slide_idx = best_match_idx
    
    cap.release()
    
    # Sort by start time just in case
    # This naive approach assumes slides can appear in any order, 
    # but practically they usually follow sequence. 
    # We might want to enforce sequence logic later if this is too noisy.
    
    return transitions

def align_transcript_with_transitions(transcript_file, transitions):
    """
    Matches transcript segments to the found slide transitions based on timestamps.
    """
    # Implementation dependent on transcript format structure
    # TODO
    pass
