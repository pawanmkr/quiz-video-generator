# Quiz Video Generator

A Python application that generates interactive quiz videos with questions, multiple choice options, and timed answers.

## Features

- Creates professional quiz videos with customizable styling
- Shows questions with multiple choice options that slide in
- Includes a timer with progress bar
- Plays audio cues (ticking clock, reveal "ding")
- Supports non-Latin scripts (e.g., Devanagari)
- Automatically concatenates individual question videos

## Project Structure

```
quiz_video_generator/
├── config/               # Configuration settings
├── src/                  # Source code modules
├── assets/               # Media assets
│   ├── fonts/            # Font files 
│   └── audio/            # Audio files
├── data/                 # Data files
└── main.py               # Main entry point
```

## Requirements

- Python 3.6+
- MoviePy
- NumPy
- Pillow (PIL)
- FFmpeg (must be installed and in PATH)

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install moviepy numpy pillow
   ```
3. Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) or using package manager

## Usage

1. Prepare a JSON file with quiz questions (see format below)
2. Run the script:
   ```
   python main.py
   ```

### Command Line Options

```
python main.py [-h] [-o OUTPUT] [-f FINAL] [--skip-rendering]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory for videos
  -f FINAL, --final FINAL
                        Final output video filename
  --skip-rendering      Skip rendering individual videos, only concatenate existing ones
```

## JSON Format

The application expects a JSON file with questions in this format:

```json
[
  {
    "1": {
      "question": "What is the capital of France?",
      "options": {
        "London": false,
        "Paris": true,
        "Berlin": false,
        "Madrid": false
      }
    }
  },
  {
    "2": {
      "question": "Who wrote 'Romeo and Juliet'?",
      "options": {
        "Charles Dickens": false,
        "Jane Austen": false,
        "William Shakespeare": true,
        "Mark Twain": false
      }
    }
  }
]
```

## Customization

You can customize the appearance and behavior by modifying the settings in `config/settings.py`:

- Canvas size and durations
- Colors and fonts
- Layout and animation parameters

## License

MIT