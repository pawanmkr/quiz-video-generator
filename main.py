#!/usr/bin/env python3
"""
Quiz Video Generator - Main Script

This script generates interactive quiz videos with questions, multiple choice options, and timed answers.
Uses PIL-based text rendering for better support of complex scripts like Devanagari.
"""

import os
import argparse
from typing import List, Dict, Tuple
import multiprocessing

from config.settings import json_path, out_dir
from src.utils import load_questions, discover_output_files
from src.rendering import build_question_video
from src.concat import create_concat_list, concatenate_videos


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate quiz videos")
    parser.add_argument("-o", "--output", default=out_dir,
                        help="Output directory for videos")
    parser.add_argument("-f", "--final", default="quiz_final.mp4",
                        help="Final output video filename")
    parser.add_argument("--skip-rendering", action="store_true",
                        help="Skip rendering individual videos, only concatenate existing ones")
    parser.add_argument("-j", "--jobs", type=int, default=multiprocessing.cpu_count(),
                        help="Number of parallel processes to use (default: number of CPU cores)")
    return parser.parse_args()


def process_question(question_entry: Dict) -> str:
    """Process a single question entry.
    
    Args:
        question_entry: A dictionary containing a single question entry
        
    Returns:
        Path to the generated video file
    """
    from src.media import AudioResources
    # Each process creates its own AudioResources instance
    audio_resources = AudioResources()
    
    for qid, qdata in question_entry.items():
        print(f"Rendering question ID: {qid}")
        # Pass output_dir from global configuration
        from config.settings import out_dir
        video_path = build_question_video(qid, qdata, audio_resources, out_dir)
        return video_path


def main():
    """Main execution function."""
    args = parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)
    
    output_paths = []
    
    if not args.skip_rendering:
        # Load questions from JSON
        questions = load_questions(json_path)
        if not questions:
            print("No questions found. Exiting.")
            return
        
        # Step 1: Generate individual quiz clips in parallel
        num_jobs = min(args.jobs, len(questions))
        print(f"Using {num_jobs} parallel processes for rendering {len(questions)} questions...")
        
        # Create a pool with the specified number of processes
        with multiprocessing.Pool(processes=num_jobs) as pool:
            # Process all questions in parallel
            results = pool.map(process_question, questions)
            
            # Filter out None results and add to output paths
            output_paths = [path for path in results if path]
    
    # If no videos were rendered, discover existing ones
    if not output_paths:
        print("Looking for existing quiz videos...")
        output_paths = discover_output_files(args.output)
        if not output_paths:
            print("No quiz videos found. Please run without --skip-rendering first.")
            return
    
    # Step 2: Create FFmpeg "concat" list file
    list_path = create_concat_list(output_paths, args.output)
    
    # Step 3: Concatenate videos with FFmpeg
    final_output = os.path.join(args.output, args.final)
    if concatenate_videos(list_path, final_output):
        print(f"All done! Final video saved to: {final_output}")
    else:
        print("Failed to concatenate videos.")


if __name__ == "__main__":
    # Required for Windows multiprocessing
    multiprocessing.freeze_support()
    main()