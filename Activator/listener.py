"""
Wake word detection module for ADA.
This module provides functionality to detect a wake word/phrase to activate the system.
Uses the Vosk library for offline speech recognition with locally stored models.
"""

import logging
import os
import queue
import json
import sounddevice as sd # used for audio input
from vosk import Model, KaldiRecognizer # actually used for speech recognition

logger = logging.getLogger(__name__)

# Configuration
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "Models/vosk-model-small-en-us-0.15"
)
WAKE_WORDS = ["hey ada", "hey a.d.a", "ok ada", "hello ada", "ada", 'hi']


def wake_word_detector() -> bool:
    """
    Uses Vosk for wake word detection.

    Returns:
        bool: True if wake word is detected, False otherwise
    """
    logger.info("Wake word detector activated")

    # Setup Vosk model
    model = Model(MODEL_PATH)
    q = queue.Queue()

    # Callback func to store audio data
    def callback(indata: bytes, frames: int, time: float, status: sd.CallbackFlags) -> None:
        if status:
            logger.warning(f"Audio status: {status}")
        q.put(bytes(indata))

    # Start listening
    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        logger.info("Listening for wake word...")
        rec = KaldiRecognizer(model, SAMPLE_RATE)

        while True:
            try:
                data = q.get(
                    timeout=2
                )  # 2 seconds timeout meaning it will wait for 2 seconds for data before trying again
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").lower()

                    if text:
                        logger.info(f"Recognized: {text}")

                        # Check if any wake word is in the recognized text
                        if any(wake_word in text for wake_word in WAKE_WORDS):
                            logger.info(f"Wake word detected: {text}")
                            return True
            except queue.Empty:
                logger.debug("Queue empty, continuing to listen")
                continue
            except KeyboardInterrupt:
                logger.info("Wake word detection interrupted")
                return False
            except Exception as e:
                logger.error(f"Error in wake word detection: {e}")
                return False
