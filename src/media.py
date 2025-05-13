from moviepy.editor import AudioFileClip
from moviepy.audio.fx.volumex import volumex
from typing import Dict, Any
import os

from config.settings import tick_path, ding_path, DUR_GUESS

class AudioResources:
    """Class to manage audio resources for the quiz.
    
    Note: This class creates fresh instances of audio clips for each request,
    which is necessary for multiprocessing compatibility.
    """    
    def __init__(self):
        # Store paths instead of clips
        self._audio_paths = {
            "tick": tick_path,
            "ding": ding_path
        }
    
    def get_clip(self, name: str) -> AudioFileClip:
        """Get an audio clip by name."""
        path = self._audio_paths.get(name)
        if not path:
            return None
            
        # Create fresh clip instances each time
        if name == "tick":
            return AudioFileClip(path)
        elif name == "ding":
            return AudioFileClip(path).set_start(DUR_GUESS).fx(volumex, 0.05)
        return None