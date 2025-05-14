import textwrap
import numpy as np
from typing import List, OrderedDict
from moviepy.editor import VideoClip
from PIL import Image, ImageDraw, ImageFont

from config.settings import (
    W, H, PALETTE, Q_WIDTH, Q_TOP_MARGIN, OPT_COLS, OPT_ROW_GAP,
    OPT_TOP_GAP, SLIDE_DELAY, SLIDE_DUR, REGULAR_FONT, BOLD_FONT
)
from src.utils import rgb2hex
from src.txt_rendering import render_text_clip

MAX_OPT_CHARS_PER_LINE = 25  # ✅ keep as-is


def wrap_text_pixel(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    """Wrap text so that no line exceeds max_width in pixels."""
    dummy_img = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(dummy_img)

    words = text.split()
    lines = []
    current = ""

    for word in words:
        test_line = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]

        if line_width <= max_width:
            current = test_line
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return "\n".join(lines)


def wrap_text(text: str, max_chars: int) -> str:
    """Insert line breaks so no line exceeds max_chars chars (used for options)."""
    return textwrap.fill(text, width=max_chars)


def make_progress_bar(duration: float) -> VideoClip:
    def make_frame(t):
        bar_w = int(W * (t / duration))
        frame = np.zeros((10, W, 3), dtype=np.uint8)
        frame[:] = PALETTE["bar_bg"]
        frame[:, :bar_w] = PALETTE["bar_fg"]
        return frame
    return VideoClip(make_frame, duration=duration).set_pos(("center", 0))


def make_question_clip(question_text: str, dur: float) -> VideoClip:
    font = ImageFont.truetype(BOLD_FONT, 90)
    wrapped = wrap_text_pixel(question_text, font, Q_WIDTH)

    return render_text_clip(
        text=wrapped,
        font_path=BOLD_FONT,
        font_size=90,
        color_rgb=PALETTE["q_text"],
        duration=dur,
        pos=(150, Q_TOP_MARGIN),
        align="left",
        padding=(20, 20)
    )


def get_question_height(question_text: str) -> int:
    font = ImageFont.truetype(BOLD_FONT, 90)
    wrapped = wrap_text_pixel(question_text, font, Q_WIDTH)

    temp = render_text_clip(
        text=wrapped,
        font_path=REGULAR_FONT,
        font_size=70,
        color_rgb=PALETTE["q_text"],
        duration=0.1,
        padding=(20, 20)
    )
    return temp.size[1]


def make_option_clips(
    question_text: str,
    options: OrderedDict,
    dur: float,
    reveal: bool = False
) -> List[VideoClip]:
    qh = get_question_height(question_text)
    start_y = Q_TOP_MARGIN + qh + OPT_TOP_GAP

    clips: List[VideoClip] = []

    for idx, (text, is_corr) in enumerate(options.items()):
        row, col = divmod(idx, 2)
        y = start_y + row * OPT_ROW_GAP
        wrapped_opt = wrap_text(f"{idx+1}. {text}", MAX_OPT_CHARS_PER_LINE)

        if reveal:
            color = PALETTE["correct"] if is_corr else PALETTE["opt"]
            fs = 60 if is_corr else 50
            font = BOLD_FONT if is_corr else REGULAR_FONT
            clip = render_text_clip(
                text=wrapped_opt,
                font_path=font,
                font_size=fs,
                color_rgb=color,
                duration=dur,
                pos=(OPT_COLS[col], y),
                padding=(10, 10),
                align="left"
            )
        else:
            color, fs, font = PALETTE["opt"], 50, REGULAR_FONT
            clip_duration = max(0.1, dur - idx * SLIDE_DELAY)

            def get_position(t, idx=idx, x0=OPT_COLS[col], y0=y):
                elapsed = t - idx * SLIDE_DELAY
                if elapsed <= 0:
                    return (x0 - 200, y0)
                if elapsed >= SLIDE_DUR:
                    return (x0, y0)
                prog = elapsed / SLIDE_DUR
                return (x0 - 200 * (1 - prog), y0)

            clip = render_text_clip(
                text=wrapped_opt,
                font_path=font,
                font_size=fs,
                color_rgb=color,
                duration=clip_duration,
                pos=get_position,
                start_time=idx * SLIDE_DELAY,
                padding=(10, 10),
                align="left"
            )
        clips.append(clip)
    return clips
