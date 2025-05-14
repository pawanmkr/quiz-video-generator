import os
import json
from typing import List, Dict, Any, Optional, Set, Tuple

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


def load_questions(json_path: str) -> List[Dict[str, Any]]:
    """Load quiz questions from JSON file.
    
    Args:
        json_path: Path to the quiz questions JSON file
        
    Returns:
        List of question dictionaries
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading questions: {e}")
        return []

def discover_output_files(dir_path: str) -> List[str]:
    """Discover existing quiz video files in the output directory.
    
    Args:
        dir_path: Directory to search for quiz video files
        
    Returns:
        List of discovered video file paths, sorted by question number
    """
    file_pattern = "quiz_"
    found_files = []
    
    try:
        for file in os.listdir(dir_path):
            if file.startswith(file_pattern) and file.endswith(".mp4"):
                found_files.append(os.path.join(dir_path, file))
    except FileNotFoundError:
        print(f"Directory not found: {dir_path}")
        return []
    
    # Sort by question number (extracted from filename)
    def get_question_num(path):
        file = os.path.basename(path)
        # Extract question number between "quiz_" and ".mp4"
        try:
            return int(file[len(file_pattern):-4])
        except ValueError:
            return 0
    
    return sorted(found_files, key=get_question_num)

def get_existing_question_ids(dir_path: str) -> Set[str]:
    """Get set of question IDs for which videos already exist.
    
    Args:
        dir_path: Directory to search for quiz video files
        
    Returns:
        Set of question IDs (as strings) that already have videos
    """
    file_pattern = "quiz_"
    existing_ids = set()
    
    try:
        for file in os.listdir(dir_path):
            if file.startswith(file_pattern) and file.endswith(".mp4"):
                # Extract ID from filename (e.g., "quiz_42.mp4" -> "42")
                question_id = file[len(file_pattern):-4]
                existing_ids.add(question_id)
    except FileNotFoundError:
        print(f"Directory not found: {dir_path}")
    
    return existing_ids

def filter_questions_to_render(questions: List[Dict[str, Any]], 
                              output_dir: str,
                              force_render: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Filter questions to only those that need rendering.
    
    Args:
        questions: List of all question dictionaries
        output_dir: Directory where question videos are stored
        force_render: Optional list of question IDs to force render regardless of existence
        
    Returns:
        Filtered list of question dictionaries
    """
    # Get set of question IDs that already have videos
    existing_ids = get_existing_question_ids(output_dir)
    
    # Convert force_render to a set for O(1) lookups
    force_render_set = set(force_render) if force_render else set()
    
    # Filter questions
    filtered = []
    for question in questions:
        for qid in question.keys():
            # Include question if it doesn't exist or is in force_render
            if qid not in existing_ids or qid in force_render_set:
                filtered.append(question)
                break
    
    skipped = len(questions) - len(filtered)
    if skipped > 0:
        print(f"Skipping {skipped} questions that already have videos.")
    
    return filtered