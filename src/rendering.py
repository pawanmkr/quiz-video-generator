from collections import OrderedDict
from typing import Dict, Any
import os

from moviepy.editor import (
    ColorClip, CompositeVideoClip, CompositeAudioClip, concatenate_videoclips
)

from config.settings import W, H, PALETTE, DUR_GUESS, DUR_REVEAL
from src.clips import make_question_clip, make_option_clips, make_progress_bar
from src.txt_rendering import render_text_clip
from src.media import AudioResources

def build_question_video(question_id: str, data: Dict[str, Any], 
                         audio_resources: AudioResources, output_dir: str) -> str:
    """Build a full video for a single quiz question.
    
    Args:
        question_id: The ID of the question
        data: Question data including question text and options
        audio_resources: Audio resources manager
        output_dir: Directory to save the output video
        
    Returns:
        Path to the generated video file
    """
    question_text = f"{question_id}. {data['question']}"
    options = OrderedDict(data["options"])
    
    # Get audio resources
    tick_sound = audio_resources.get_clip("tick")
    ding_sound = audio_resources.get_clip("ding")
    
    # === Guess phase ===
    bg1 = ColorClip((W, H), color=PALETTE["bg"], duration=DUR_GUESS)
    q1 = make_question_clip(question_text, DUR_GUESS)
    opt1 = make_option_clips(options, DUR_GUESS, reveal=False)
    bar = make_progress_bar(DUR_GUESS)
    audio1 = CompositeAudioClip([tick_sound])

    guess = CompositeVideoClip([bg1, q1, *opt1, bar])
    guess.duration = DUR_GUESS
    guess = guess.set_audio(audio1)

    # === Reveal phase ===
    bg2 = ColorClip((W, H), color=PALETTE["bg"], duration=DUR_REVEAL)
    q2 = make_question_clip(question_text, DUR_REVEAL)
    opt2 = make_option_clips(options, DUR_REVEAL, reveal=True)
    audio_total = CompositeAudioClip([tick_sound, ding_sound])

    reveal = CompositeVideoClip([bg2, q2, *opt2])
    reveal = reveal.set_duration(DUR_REVEAL)
    reveal = reveal.set_audio(audio_total.subclip(DUR_GUESS, DUR_GUESS + DUR_REVEAL))

    # Add a pause at the beginning
    pause = ColorClip((W, H), color=PALETTE["bg"], duration=1).set_opacity(1)

    # Combine all phases
    final = concatenate_videoclips([pause, guess, reveal], method="compose")
    final = final.set_duration(DUR_GUESS + DUR_REVEAL + 1)

    # Save the video
    out_path = os.path.join(output_dir, f"quiz_{question_id}.mp4")
    final.write_videofile(out_path, fps=60, codec="libx264", audio=True)
    
    return out_path