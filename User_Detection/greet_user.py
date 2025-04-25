"""
Module for greeting users with text-to-speech.
Uses gTTS (Google Text-to-Speech) to create audio greetings.
"""

import os
import logging
import tempfile  # for creating temporary files for audio file so noo need to save
import threading  # for threading (to play audio in background on a separate thread)
from gtts import gTTS  # Google Text-to-Speech library
from pygame import mixer  # for playing audio files
import time  # for time.sleep

logger = logging.getLogger(__name__)


def initialize_audio() -> None:
    """
    Initialize pygame mixer for audio playback.
    """
    mixer.init()
    logger.info("Audio system initialized")


def play_greeting_async(temp_filename: str) -> None:
    """
    Play the greeting audio file asynchronously.

    Args:
        temp_filename (str): Path to the audio file
    """
    try:
        mixer.music.load(temp_filename)
        mixer.music.play()

        # Wait for the audio to finish playing
        while mixer.music.get_busy():
            time.sleep(0.1)

        # Clean up the temporary file
        os.unlink(temp_filename)
        logger.info("Greeting complete")
        logger.info("User Detection completed continuing...")
    except Exception as e:
        logger.error(f"Error playing greeting: {e}")


def greet_user(name: str) -> None:
    """
    Generate and play a personalized greeting for the user.

    This function generates a greeting using gTTS and plays it
    asynchronously so the video continues during playback.

    Args:
        name (str): The name of the user to greet
    """
    logger.info(f"Greeting user: {name}")

    # Don't greet auto-generated usernames with the full name, just say "Welcome"
    if name.startswith("User_"):
        greeting_text = "Welcome to ADA, your personal digital assistant."
    else:
        greeting_text = (
            f"Hello {name}, welcome to ADA, your personal digital assistant."
        )

    try:
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_filename = temp_file.name

        # Generate the speech audio
        tts = gTTS(text=greeting_text, lang="en", slow=False)
        tts.save(temp_filename)
        logger.info(f"Speech generated greeting user...")

        # Play the audio in a separate thread so video continues
        greeting_thread = threading.Thread(
            target=play_greeting_async, args=(temp_filename,)
        )
        greeting_thread.daemon = True  # daemon is a common word for background thread
        greeting_thread.start()

    except Exception as e:
        logger.error(f"Error creating greeting: {e}")
