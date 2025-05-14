# Quiz Video Generator - Usage Guide

## Overview

This guide explains how to use the Quiz Video Generator with minimal system resource usage, especially for MacBook Air and other heat-sensitive computers.

## Basic Commands

### Standard Usage

```bash
python main.py
```

This runs with the default settings (single process, maximum nice value, small batch sizes).

### Skip Existing Videos

```bash
python main.py --skip-rendering
```

This will skip rendering videos that already exist and only generate new ones.

## Resource Management Options

### CPU Usage Control

| Option | Description | Example |
|--------|-------------|---------|
| `-j, --jobs` | Number of parallel processes to use | `--jobs 1` (default, uses 1 core) |
| `--nice` | Process priority (1-19, higher = lower priority) | `--nice 19` (default, lowest priority) |
| `--sequential` | Process questions one at a time (no multiprocessing) | `--sequential` |

### Memory & Thermal Management

| Option | Description | Example |
|--------|-------------|---------|
| `--batch-size` | Number of questions to process in each batch | `--batch-size 1` (default) |
| `--cool-time` | Seconds to pause between batches/questions | `--cool-time 20` (default) |
| `--throttle` | Enable CPU throttling during cooling periods | `--throttle` |

### Output Control

| Option | Description | Example |
|--------|-------------|---------|
| `-o, --output` | Directory for output videos | `--output ./my_videos` |
| `-f, --final` | Name of final concatenated video | `--final my_quiz.mp4` |
| `--skip-rendering` | Skip rendering, only concatenate existing videos | `--skip-rendering` |

## Recommended Commands for Different Scenarios

### For MacBook Air (Minimal Heat)

```bash
python main.py --sequential --cool-time 30 --throttle
```

This processes one question at a time with 30-second cooling periods and CPU throttling.

### For Better Performance with Controlled Heat

```bash
python main.py -j 1 --batch-size 2 --cool-time 30
```

This uses 1 core to process 2 questions at a time, with 30-second cooling periods.

### For Systems with Good Cooling

```bash
python main.py -j 2 --batch-size 5 --cool-time 10
```

This uses 2 cores to process questions in batches of 5 with 10-second cooling periods.

### Only Concatenate Existing Videos

```bash
python main.py --skip-rendering
```

This skips rendering individual question videos and only creates the final video from existing clips.

## Runtime Controls

During script execution, you can control the process:

| Action | Description |
|--------|-------------|
| `Ctrl+C` | Gracefully stop processing |
| `kill -USR1 <PID>` | Pause processing for 30 seconds (Unix/Mac only) |

Example of pausing:
1. Find the process ID: `ps aux | grep main.py`
2. Send pause signal: `kill -USR1 12345` (replace 12345 with actual PID)

## Avoiding Re-Rendering Existing Videos

The script automatically skips rendering videos that already exist by checking for files in the output directory. If you want to explicitly avoid re-rendering:

1. Use the `--skip-rendering` option to skip all rendering and only concatenate
2. Or let the script run normally - it will skip files that already exist

## Troubleshooting

### System Getting Too Hot

If your system is overheating:

1. Press `Ctrl+C` to stop the process
2. Restart with more conservative settings:
   ```bash
   python main.py --sequential --cool-time 60 --throttle
   ```
3. Alternatively, send the pause signal: `kill -USR1 <PID>`

### Audio Issues in Final Video

If audio is missing or out of sync:

1. Make sure the intro clip is properly rendered with audio
2. Run the render_intro_clip function separately
3. Check that the audio files referenced in settings are accessible

### Out of Memory Errors

If you encounter memory errors:

1. Reduce batch size: `--batch-size 1`
2. Use sequential mode: `--sequential`
3. Close other applications while running