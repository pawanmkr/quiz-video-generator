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
    padding: int = 10,
    align: str = "left"
) -> Image.Image:
    """
    Render text to a PIL Image using the specified font and color.
    This provides better support for complex scripts like Devanagari.
    
    Args:
        text: Text to render
        font_path: Path to the font file
        font_size: Font size in points
        color_rgb: RGB color tuple for the text
        bg_color: RGB color tuple for the background (transparent if None)
        padding: Padding around the text in pixels
        align: Text alignment ('left', 'center', or 'right')
        
    Returns:
        PIL Image with the rendered text
    """
    # Load the font
    font = ImageFont.truetype(font_path, font_size)
    
    # Create a dummy image to calculate text size
    dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    # Create the actual image with padding
    img_w, img_h = w + (padding * 2), h + (padding * 2)
    
    # Set up background
    if bg_color:
        img = Image.new("RGBA", (img_w, img_h), (*bg_color, 255))
    else:
        img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    
    # Draw the text
    draw = ImageDraw.Draw(img)
    
    # Handle text alignment
    if align == "center":
        x_pos = padding + (w - bbox[2]) // 2
    elif align == "right":
        x_pos = padding + (w - bbox[2])
    else:  # left alignment
        x_pos = padding
        
    y_pos = padding
    
    draw.text((x_pos, y_pos), text, font=font, fill=(*color_rgb, 255))
    return img

def pil_to_moviepy_clip(
    img: Image.Image, 
    duration: float, 
    pos: Union[Tuple[int, int], str, callable] = None
) -> ImageClip:
    """
    Convert a PIL Image to a MoviePy ImageClip.
    
    Args:
        img: PIL Image
        duration: Duration of the clip in seconds
        pos: Position of the clip (same format as MoviePy's set_pos)
        
    Returns:
        MoviePy ImageClip
    """
    # Convert PIL Image to numpy array for MoviePy
    img_array = np.array(img)
    
    # Create MoviePy clip
    clip = ImageClip(img_array).set_duration(duration)
    
    # Set position if provided
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
    padding: int = 10,
    align: str = "left",
    start_time: float = 0
) -> ImageClip:
    """
    Create a MoviePy clip with text rendered using PIL.
    This is particularly useful for complex scripts like Devanagari.
    
    Args:
        text: Text to render
        font_path: Path to the font file
        font_size: Font size in points
        color_rgb: RGB color tuple for the text
        duration: Duration of the clip in seconds
        pos: Position of the clip (same format as MoviePy's set_pos)
        bg_color: RGB color tuple for the background (transparent if None)
        padding: Padding around the text in pixels
        align: Text alignment ('left', 'center', or 'right')
        start_time: Start time of the clip in seconds
        
    Returns:
        MoviePy ImageClip with the rendered text
    """
    # Render text to PIL Image
    img = render_text_to_image(text, font_path, font_size, color_rgb, bg_color, padding, align)
    
    # Convert to MoviePy clip
    clip = pil_to_moviepy_clip(img, duration, pos)
    
    # Set start time if specified
    if start_time > 0:
        clip = clip.set_start(start_time)
        
    return clip