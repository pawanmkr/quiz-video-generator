# txt_rendering.py
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip
from typing import Tuple, Union


def render_text_to_image(
    text: str, 
    font_path: str, 
    font_size: int, 
    color_rgb: Tuple[int, int, int], 
    bg_color: Tuple[int, int, int] = None,
    padding: Union[int, Tuple[int, int]] = 10,
    align: str = "left"
) -> Image.Image:
    """
    Render text to a PIL Image using the specified font and color.
    Supports both uniform and per-axis padding.
    """
    font = ImageFont.truetype(font_path, font_size)
    
    dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Determine padding
    if isinstance(padding, tuple):
        pad_x, pad_y = padding
    else:
        pad_x = pad_y = padding

    img_w, img_h = w + pad_x * 2, h + pad_y * 2

    if bg_color:
        img = Image.new("RGBA", (img_w, img_h), (*bg_color, 255))
    else:
        img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))

    draw = ImageDraw.Draw(img)
    
    # Alignment
    if align == "center":
        x_pos = pad_x + (img_w - pad_x*2 - w) // 2
    elif align == "right":
        x_pos = pad_x + (img_w - pad_x*2 - w)
    else:
        x_pos = pad_x
    y_pos = pad_y

    draw.text((x_pos, y_pos), text, font=font, fill=(*color_rgb, 255))
    return img

def pil_to_moviepy_clip(
    img: Image.Image, 
    duration: float, 
    pos: Union[Tuple[int, int], str, callable] = None
) -> ImageClip:
    img_array = np.array(img)
    clip = ImageClip(img_array).set_duration(duration)
    if pos is not None:
        clip = clip.set_pos(pos)
    return clip


def render_text_clip(
    text: str,
    font_path: str,
    font_size: int,
    color_rgb: Tuple[int, int, int],
    duration: float, 
    pos: Union[Tuple[int, int], str, callable] = None,
    bg_color: Tuple[int, int, int] = None,
    padding: Union[int, Tuple[int,int]] = 0,
    align: str = "left",
    start_time: float = 0
) -> ImageClip:
    img = render_text_to_image(text, font_path, font_size, color_rgb, bg_color, padding, align)
    clip = pil_to_moviepy_clip(img, duration, pos)
    if start_time > 0:
        clip = clip.set_start(start_time)
    return clip