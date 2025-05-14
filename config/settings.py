import os

# === Durations ===
DUR_GUESS, DUR_REVEAL = 10, 3

# === Canvas size ===
W, H = 1920, 1080

# === Video settings ===
FPS = 30

# Video encoding settings
# Options for preset: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
# Faster presets = faster encoding, slightly lower quality
VIDEO_ENCODING_PRESET = "veryfast"  # Much faster than the default "medium" preset
VIDEO_ENCODING_BITRATE = "2000k"    # Adjust as needed for quality vs file size

# === Base paths ===
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
out_dir = os.path.join(base_dir, "output")
audio_dir = os.path.join(base_dir, "assets", "audio")
fonts_dir = os.path.join(base_dir, "assets", "fonts")

# === File paths ===
json_path = os.path.join(base_dir, "data", "cgl2024t1.json")
tick_path = os.path.join(audio_dir, "tick_10seconds.mp3")
ding_path = os.path.join(audio_dir, "ding.mp3")

# Font paths
DEVANAGARI_FONT = os.path.join(fonts_dir, "Noto_Sans_Devanagari", "static", "NotoSansDevanagari-Regular.ttf")
DEVANAGARI_BOLD = os.path.join(fonts_dir, "Noto_Sans_Devanagari", "static", "NotoSansDevanagari-ExtraBold.ttf")

REGULAR_FONT = DEVANAGARI_FONT
BOLD_FONT = DEVANAGARI_BOLD

# === Theme palette ===
PALETTE = {
    "bg":      (24, 24, 48),
    "q_text":  (204, 204, 204),
    "opt":     (170, 170, 170),
    "correct": (76, 175, 80),
    "bar_bg":  (68, 68, 102),
    "bar_fg":  (255, 255, 0),
}

# === Layout ===
Q_WIDTH = 1600
Q_TOP_MARGIN = 150
OPT_COLS = [150, 1000]
OPT_ROW_GAP = 150
OPT_TOP_GAP = 200
SLIDE_DELAY = 0.15
SLIDE_DUR = 0.25