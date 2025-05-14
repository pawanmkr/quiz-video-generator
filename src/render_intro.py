import os
from moviepy.editor import (
    ColorClip, TextClip,
    CompositeVideoClip, concatenate_videoclips,
    CompositeAudioClip
)
from config.settings import W, H, FPS, PALETTE, BOLD_FONT, out_dir

def render_intro_clip(audio_resources=None):
    """
    Renders an intro countdown clip with audio.
    
    Args:
        audio_resources: AudioResources manager (optional, will create one if None)
        
    Returns:
        Path to the generated intro clip
    """
    output_path = os.path.join(out_dir, "intro.mp4")
    if os.path.exists(output_path):
        print("🟡 Intro clip already exists. Skipping regeneration.")
        return output_path

    print("🎬 Rendering intro countdown clip...")

    # Create AudioResources if not provided (similar to question clip)
    if audio_resources is None:
        from src.media import AudioResources
        audio_resources = AudioResources()

    # Get tick sound using AudioResources (same as question clip)
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
    # Use the same encoding parameters as question clip for consistency
    from config.settings import VIDEO_ENCODING_PRESET, VIDEO_ENCODING_BITRATE
    final.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        preset=VIDEO_ENCODING_PRESET,
        bitrate=VIDEO_ENCODING_BITRATE,
        audio=True  # Explicitly specify audio=True
    )

    print("✅ Intro clip saved at:", output_path)
    return output_path