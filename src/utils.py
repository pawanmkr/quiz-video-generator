import json
import os
from typing import Dict, List, Any, Tuple
from PIL import Image, ImageDraw, ImageFont

def rgb2hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hexadecimal color string."""
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def load_questions(json_path: str) -> List[Dict[str, Any]]:
    """Load question data from JSON file."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading questions: {e}")
        return []

def discover_output_files(out_dir: str, prefix: str = "quiz_", suffix: str = ".mp4") -> List[str]:
    """Discover existing output files matching the pattern."""
    import glob
    pattern = os.path.join(out_dir, f"{prefix}*{suffix}")
    files = glob.glob(pattern)
    # Sort files by question number
    files.sort(key=lambda fn: int(os.path.basename(fn).split('_')[1].split('.')[0]))
    return files