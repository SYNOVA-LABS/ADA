"""
this module provides a function to play any response of ada via text-to-speech (uses users speaker)
"""

import logging
import os
import time
import tempfile # no saving the audio file to disk
from gtts import gTTS # Google Text-to-Speech
from pygame import mixer # to play audio files 

# Set up logging
logger = logging.getLogger(__name__)

# Global variable to track playback status helps to avoid multiple simultaneous TTS playback
tts_playback_status = {"playing": False}

def play_response_async(response: str) -> None:
    """
    Convert text to speech and play it asynchronously.
    
    Args:
        response: The text to convert to speech
    """
    if not response or not response.strip():
        logger.warning("Empty response, nothing to play")
        return
        
    try:
        # Mark that playback has started
        tts_playback_status["playing"] = True
        
        # Initialize mixer if not already initialized
        if not mixer.get_init():
            mixer.init()
            
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_path = temp_file.name
            
        # Generate the audio file
        tts = gTTS(text=response, lang='en', slow=False)
        tts.save(temp_path)
        
        # Play the audio file
        mixer.music.load(temp_path)
        mixer.music.play()
        
        # Wait for playback to complete
        while mixer.music.get_busy():
            time.sleep(0.1) # Sleep to avoid busy waiting
            
        # Clean up the temporary file
        try:
            os.unlink(temp_path)
        except Exception as e:
            logger.error(f"Error removing temporary audio file: {e}")
            
        # Mark that playback has finished
        tts_playback_status["playing"] = False
        logger.info("TTS playback completed")
        
    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}")
        # Make sure to reset playback status even if there's an error
        tts_playback_status["playing"] = False

def is_audio_playing() -> bool:
    """
    Check if TTS audio is currently playing.
    
    Returns:
        bool: True if audio is playing, False otherwise
    """
    return tts_playback_status["playing"]