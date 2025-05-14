#!/usr/bin/env python3
"""
Quiz Video Generator - Main Script (Low Resource Version)

This script generates interactive quiz videos with questions, multiple choice options, and timed answers.
Optimized for minimal heat generation on MacBooks with limited cooling.
"""

import os
import argparse
import multiprocessing
import time
import math
import sys
import signal

from config.settings import json_path, out_dir
from src.utils import load_questions, discover_output_files, filter_questions_to_render
from src.rendering import build_question_video
from src.concat import create_concat_list, concatenate_videos
from src.media import AudioResources

# Global flag to indicate if the process should pause
should_pause = False
pause_duration = 30  # seconds

def signal_handler(sig, frame):
    """Handle CTRL+C by exiting gracefully."""
    print("\nProcess interrupted. Exiting gracefully...")
    sys.exit(0)

def pause_handler(sig, frame):
    """Handle USR1 signal by toggling pause mode."""
    global should_pause
    should_pause = not should_pause
    if should_pause:
        print(f"\n⏸️ Processing paused. Will resume in {pause_duration} seconds...")
    else:
        print("\n▶️ Processing manually resumed.")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate quiz videos with minimal resource usage")
    parser.add_argument("-o", "--output", default=out_dir,
                        help="Output directory for videos")
    parser.add_argument("-f", "--final", default="quiz_final.mp4",
                        help="Final output video filename")
    parser.add_argument("--skip-rendering", action="store_true",
                        help="Skip rendering individual videos, only concatenate existing ones")
    parser.add_argument("--force-render", nargs="+", type=str,
                        help="Force render specific question IDs even if they exist")
    parser.add_argument("-j", "--jobs", type=int, default=1,
                        help="Number of parallel processes to use (default: 1)")
    parser.add_argument("--nice", type=int, default=19, 
                        help="Process nice value (1-19, higher means lower priority, default: 19)")
    parser.add_argument("--batch-size", type=int, default=1,
                        help="Process questions in batches of this size (default: 1)")
    parser.add_argument("--cool-time", type=int, default=20,
                        help="Cooling time in seconds between batches (default: 20)")
    parser.add_argument("--throttle", action="store_true",
                        help="Enable CPU throttling between questions")
    parser.add_argument("--sequential", action="store_true",
                        help="Process questions sequentially (no multiprocessing)")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip rendering questions that already have videos")
    
    return parser.parse_args()


def set_process_priority(nice_value):
    """Set the process priority (nice value) for better system responsiveness."""
    try:
        # Only works on Unix-like systems (macOS, Linux)
        os.nice(nice_value)
        print(f"Process priority set to nice {nice_value}")
    except (AttributeError, OSError, ImportError):
        # Handle Windows and other systems
        try:
            import psutil
            p = psutil.Process(os.getpid())
            if os.name == 'nt':  # Windows
                p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                print("Process priority set to below normal")
            else:
                p.nice(nice_value)
                print(f"Process priority set to nice {nice_value}")
        except (ImportError, Exception) as e:
            print(f"Warning: Could not set process priority: {e}")


def process_question(args):
    """Process a single question entry."""
    qid, qdata, output_dir = args
    
    # Check if question video already exists and should be skipped
    output_file = os.path.join(output_dir, f"quiz_{qid}.mp4")
    if os.path.exists(output_file):
        print(f"Question ID {qid} already rendered, skipping.")
        return output_file
    
    try:
        print(f"Rendering question ID: {qid}")
        # Each process creates its own AudioResources instance for thread safety
        audio_resources = AudioResources()
        video_path = build_question_video(qid, qdata, audio_resources, output_dir)
        
        # Clean up audio resources to free memory
        del audio_resources
        
        return video_path
    except Exception as e:
        print(f"Error processing question {qid}: {e}")
        return None


def process_question_sequential(qid, qdata, output_dir, cooling_time=5, throttle=False):
    """Process a single question without multiprocessing."""
    # Check if question video already exists and should be skipped
    output_file = os.path.join(output_dir, f"quiz_{qid}.mp4")
    if os.path.exists(output_file):
        print(f"Question ID {qid} already rendered, skipping.")
        return output_file
    
    try:
        print(f"Rendering question ID: {qid}")
        # Create AudioResources for this question
        audio_resources = AudioResources()
        
        # Check if we should pause processing
        global should_pause
        if should_pause:
            print(f"Pausing for {pause_duration} seconds to cool down...")
            time.sleep(pause_duration)
            should_pause = False
        
        # Process the question
        video_path = build_question_video(qid, qdata, audio_resources, output_dir)
        
        # Clean up to free memory
        del audio_resources
        
        # Cooling period to prevent overheating
        if cooling_time > 0:
            print(f"Cooling down for {cooling_time} seconds...")
            if throttle:
                # Use a low-CPU sleep approach
                end_time = time.time() + cooling_time
                while time.time() < end_time:
                    time.sleep(0.5)
                    # Very minimal CPU usage during sleep
                    if time.time() % 2 < 0.1:
                        # Force garbage collection occasionally
                        import gc
                        gc.collect()
            else:
                # Simple sleep
                time.sleep(cooling_time)
        
        return video_path
    except Exception as e:
        print(f"Error processing question {qid}: {e}")
        return None


def main():
    """Main execution function."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    try:
        # On Unix systems, set up USR1 signal to pause/resume (can be sent with: kill -USR1 PID)
        signal.signal(signal.SIGUSR1, pause_handler)
    except AttributeError:
        # SIGUSR1 not available on Windows
        pass
    
    args = parse_args()
    
    # Set process priority to lowest
    set_process_priority(args.nice)
    
    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)
    
    output_paths = []
    
    if not args.skip_rendering:
        # Load questions from JSON
        all_questions = load_questions(json_path)
        if not all_questions:
            print("No questions found. Exiting.")
            return
        
        # Filter questions if --skip-existing is enabled
        if args.skip_existing:
            questions = filter_questions_to_render(all_questions, args.output, args.force_render)
        else:
            questions = all_questions
        
        if not questions:
            print("All questions already have videos. Skipping rendering.")
        else:
            # Print status information with thermal management details
            if args.sequential:
                print(f"Processing {len(questions)} questions sequentially (no parallelism)")
                print(f"Cooling time between questions: {args.cool_time} seconds")
                if args.throttle:
                    print("CPU throttling enabled during cooling periods")
            else:
                print(f"Using {args.jobs} parallel processes (of {multiprocessing.cpu_count()} available CPU cores)")
                print(f"Processing {len(questions)} questions in batches of {args.batch_size}")
                print(f"Cooling time between batches: {args.cool_time} seconds")
            
            # Print thermal management instructions
            print("\n🌡️ THERMAL MANAGEMENT 🌡️")
            print("- If your Mac gets too hot, you can press Ctrl+C to stop gracefully")
            if sys.platform == 'darwin' or sys.platform.startswith('linux'):
                print(f"- You can also pause processing by running: kill -USR1 {os.getpid()}")
                print("  This will automatically pause for 30 seconds to cool down")
            print("- Close other applications and put your Mac on a hard, cool surface")
            print("- Consider using a cooling pad or external fan if available")
            print()
            
            # Process questions based on selected mode
            if args.sequential:
                # Process questions one at a time
                for question in questions:
                    for qid, qdata in question.items():
                        path = process_question_sequential(
                            qid, qdata, args.output, 
                            cooling_time=args.cool_time,
                            throttle=args.throttle
                        )
                        if path:
                            output_paths.append(path)
            else:
                # Process questions in small batches with multiprocessing
                question_items = []
                for q in questions:
                    for qid, qdata in q.items():
                        question_items.append((qid, qdata, args.output))
                
                batch_size = args.batch_size
                total_batches = math.ceil(len(question_items) / batch_size)
                
                for batch_num in range(total_batches):
                    start_idx = batch_num * batch_size
                    end_idx = min(start_idx + batch_size, len(question_items))
                    batch = question_items[start_idx:end_idx]
                    
                    print(f"\nProcessing batch {batch_num+1}/{total_batches} ({len(batch)} questions)")
                    
                    # Process the batch with multiprocessing
                    with multiprocessing.Pool(processes=args.jobs) as pool:
                        batch_results = pool.map(process_question, batch)
                        
                        # Filter out None results and add to output paths
                        batch_paths = [path for path in batch_results if path]
                        output_paths.extend(batch_paths)
                    
                    # Check if we should pause processing
                    global should_pause
                    if should_pause:
                        print(f"Pausing for {pause_duration} seconds to cool down...")
                        time.sleep(pause_duration)
                        should_pause = False
                    
                    # Give the system a significant cooling period between batches
                    if batch_num < total_batches - 1:
                        print(f"Batch complete. Cooling down for {args.cool_time} seconds...")
                        time.sleep(args.cool_time)
                        
                        # Force garbage collection to free memory
                        import gc
                        gc.collect()
    
    # If no videos were rendered, discover existing ones
    if not output_paths:
        print("Looking for existing quiz videos...")
        output_paths = discover_output_files(args.output)
        if not output_paths:
            print("No quiz videos found. Please run without --skip-rendering first.")
            return
    
    # Create a short cooling period before concatenation
    print("Preparing for video concatenation...")
    time.sleep(5)
    
    # Step 2: Create FFmpeg concat list file
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