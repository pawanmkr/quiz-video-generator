import os
import subprocess
from typing import List
from src.media import AudioResources

def render_intro_clip(output_dir=None):
    """Renders the intro countdown clip with audio.
    
    Args:
        output_dir: Directory to save the intro clip (uses settings.out_dir if None)
        
    Returns:
        Path to the generated intro clip
    """
    # Use the output_dir parameter if provided, otherwise use the default from settings
    if output_dir is None:
        from config.settings import out_dir
        output_dir = out_dir
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "intro.mp4")
    if os.path.exists(output_path):
        print("🟡 Intro clip already exists. Skipping regeneration.")
        return output_path

    print("🎬 Rendering intro countdown clip...")
    
    from moviepy.editor import (
        ColorClip, TextClip,
        CompositeVideoClip, concatenate_videoclips,
        CompositeAudioClip
    )
    from config.settings import W, H, FPS, PALETTE, BOLD_FONT
    from config.settings import VIDEO_ENCODING_PRESET, VIDEO_ENCODING_BITRATE
    
    # Create AudioResources (same as in question clip)
    audio_resources = AudioResources()
    tick_sound = audio_resources.get_clip("tick")
    
    # We want 10 seconds: numbers 10 down to 1 inclusive (10 frames of 1s each)
    numbers = list(range(10, 0, -1))  # [10,9,...,1]
    print("⏳ Countdown numbers:", numbers)
    duration = len(numbers)           # should be 10
    font_size = 200
    font_color = PALETTE["q_text"]
    bg_color   = PALETTE["bg"]

    clips = []
    for num in numbers:
        # One‐second clip with the number centered
        txt = (TextClip(
                  str(num),
                  fontsize=font_size,
                  font=BOLD_FONT,
                  color=f"rgb{font_color}",
                  size=(W, H),
                  method="label"
               )
               .set_position("center")
               .set_duration(1)
             )

        bg = ColorClip(size=(W, H), color=bg_color, duration=1)
        clips.append(CompositeVideoClip([bg, txt]))

    # Concatenate and set the right FPS
    final = concatenate_videoclips(clips, method="compose").set_fps(FPS)

    # Create composite audio using the same method as in question clip
    audio = CompositeAudioClip([tick_sound.subclip(0, min(tick_sound.duration, duration))])
    final = final.set_audio(audio)

    # Export intro with matching theme and codecs
    final.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        preset=VIDEO_ENCODING_PRESET,
        bitrate=VIDEO_ENCODING_BITRATE,
        audio=True  # Explicitly specify audio=True
    )

    # Clean up to free memory
    del audio_resources
    del final
    del audio
    del clips

    print("✅ Intro clip saved at:", output_path)
    return output_path


def create_concat_list(output_paths: List[str], output_dir: str) -> str:
    """Create an FFmpeg concat format list file.
    
    Args:
        output_paths: List of video file paths to concatenate
        output_dir: Directory to save the list file
        
    Returns:
        Path to the created list file
    """
    intro_path = render_intro_clip(output_dir)
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