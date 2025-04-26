"""
this module provides a function to play the response of a language model
"""

import logging
import os
import time
import tempfile
import threading
from gtts import gTTS
from pygame import mixer
from llama_cpp import Llama

# Set up logging
logger = logging.getLogger(__name__)

def play_response_async(response: str) -> None:
    """
    Convert the text response to speech and play it asynchronously.
    
    Args:
        response: The text response to speak
    """
    try:
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_filename = temp_file.name
        
        # Generate the speech audio
        tts = gTTS(text=response, lang="en", slow=False)
        tts.save(temp_filename)
        logger.info("Speech generated for LLM response")
        
        # Initialize the mixer if not already initialized
        if not mixer.get_init():
            mixer.init()
        
        mixer.music.load(temp_filename)
        mixer.music.play()
        
        # Wait for the audio to finish playing
        while mixer.music.get_busy():
            time.sleep(0.1)
        
        # Clean up the temporary file
        os.unlink(temp_filename)
        logger.info("Response playback complete")
    except Exception as e:
        logger.error(f"Error playing response: {e}")