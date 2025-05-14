import os
import subprocess
from typing import List
from src.render_intro import render_intro_clip

def create_concat_list(output_paths: List[str], output_dir: str) -> str:
    """Create an FFmpeg concat format list file.
    
    Args:
        output_paths: List of video file paths to concatenate
        output_dir: Directory to save the list file
        
    Returns:
        Path to the created list file
    """
    intro_path = render_intro_clip()
    full_list = [intro_path] + output_paths
    list_path = os.path.join(output_dir, "to_concat.txt")
    with open(list_path, "w") as f:
        for p in full_list:
            # Ensure paths are escaped properly if they contain spaces
            f.write(f"file '{p}'\n")
    return list_path

def concatenate_videos(list_path: str, output_path: str) -> bool:
    """Concatenate videos using FFmpeg without re-encoding.
    
    Args:
        list_path: Path to the FFmpeg concat format file
        output_path: Path where the final video will be saved
        
    Returns:
        True if concatenation was successful, False otherwise
    """
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        output_path
    ]
    
    print(f"Concatenating all clips into {output_path} ...")
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error concatenating videos: {e}")
        return False