# clips.py
import numpy as np
from typing import List, Dict, Tuple, Any, OrderedDict
from moviepy.editor import TextClip, VideoClip
from collections import OrderedDict

from config.settings import (
    W, H, PALETTE, Q_WIDTH, Q_TOP_MARGIN, OPT_COLS, OPT_ROW_GAP, 
    OPT_TOP_GAP, SLIDE_DELAY, SLIDE_DUR, REGULAR_FONT, BOLD_FONT
)
from src.utils import rgb2hex
from src.txt_rendering import render_text_clip

def make_progress_bar(duration: float) -> VideoClip:
    """Create a progress bar animation for the timer."""
    def make_frame(t):
        bar_w = int(W * (t / duration))
        frame = np.zeros((10, W, 3), dtype=np.uint8)
        frame[:] = PALETTE["bar_bg"]
        frame[:, :bar_w] = PALETTE["bar_fg"]
        return frame
    return VideoClip(make_frame, duration=duration).set_pos(("center", 0))

def make_question_clip(question_text: str, dur: float) -> VideoClip:
    """Create a clip displaying the question text using PIL rendering for better Devanagari support."""
    return render_text_clip(
        text=question_text,
        font_path=REGULAR_FONT,
        font_size=70,
        color_rgb=PALETTE["q_text"],
        duration=dur,
        pos=(150, Q_TOP_MARGIN),
        align="left",
        padding=0,
        # No background color to make it transparent
    )

def get_question_height(question_text: str) -> int:
    """
    Estimate the height of the question text for positioning options.
    Creates a temporary clip to measure its dimensions.
    """
    # Create a very short temporary clip just to get dimensions
    temp_clip = render_text_clip(
        text=question_text, 
        font_path=REGULAR_FONT,
        font_size=70,
        color_rgb=PALETTE["q_text"],
        duration=0.1
    )
    _, h = temp_clip.size
    return h

def make_option_clips(options: OrderedDict, dur: float, reveal: bool = False) -> List[VideoClip]:
    """Create clips for all answer options using PIL rendering."""
    # Calculate start_y based on a placeholder question
    qh = get_question_height("Sample")
    start_y = Q_TOP_MARGIN + qh + OPT_TOP_GAP
    
    clips = []
    for idx, (text, is_corr) in enumerate(options.items()):
        row, col = divmod(idx, 2)
        y = start_y + row * OPT_ROW_GAP
        label = f"{idx+1}. {text}"

        if reveal:
            # Reveal phase - correct answer highlighted
            if is_corr:
                color, fs, fontw = PALETTE["correct"], 60, BOLD_FONT
            else:
                color, fs, fontw = PALETTE["opt"], 50, REGULAR_FONT
                
            clip = render_text_clip(
                text=label,
                font_path=fontw,
                font_size=fs,
                color_rgb=color,
                duration=dur,
                pos=(OPT_COLS[col], y)
            )
        else:
            # Guess phase - sliding animation
            color, fs, fontw = PALETTE["opt"], 50, REGULAR_FONT
            clip_duration = max(0.1, dur - idx * SLIDE_DELAY)
            
            # For the slide-in effect, we need a function
            def get_position(t, idx=idx, x0=OPT_COLS[col], y0=y):
                # Only animate during the slide duration after this option's delay
                elapsed = t - idx * SLIDE_DELAY
                if elapsed <= 0:
                    # Before the option's start time, position it off-screen
                    return (x0 - 200, y0)
                elif elapsed >= SLIDE_DUR:
                    # After animation completes, keep it at the final position
                    return (x0, y0)
                else:
                    # During animation, calculate position
                    progress = elapsed / SLIDE_DUR
                    offset = 200 * (1 - progress)
                    return (x0 - offset, y0)
            
            # Create the clip with the animation
            clip = render_text_clip(
                text=label,
                font_path=fontw,
                font_size=fs,
                color_rgb=color,
                duration=clip_duration,
                pos=get_position,
                start_time=idx * SLIDE_DELAY
            )
            
        clips.append(clip)
    return clips