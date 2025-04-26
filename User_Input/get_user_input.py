"""
Module for getting user input through the microphone.
This module handles capturing and processing user questions using local speech recognition.
"""

import logging
import os
import queue
import json
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer

logger = logging.getLogger(__name__)

# Configuration for Vosk
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "Models/vosk-model-small-en-us-0.15"
)

# Flags to control the question detection state
_is_processing = False
_last_process_time = 0

def listen_for_question() -> str:
    """
    Listen for a user question using the microphone with Vosk for offline speech recognition.
    
    Returns:
        str: The recognized question, or None if no question was recognized
    """
    logger.info("Listening for user question...")
    
    try:
        # Setup Vosk model
        model = Model(MODEL_PATH)
        q = queue.Queue()
        
        # Callback to store audio data
        def callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio status: {status}")
            q.put(bytes(indata))
        
        # Use a timeout to prevent indefinite listening
        start_time = time.time()
        timeout = 10  # seconds
        
        # Start listening
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            rec = KaldiRecognizer(model, SAMPLE_RATE)
            full_text = ""
            
            while time.time() - start_time < timeout:
                try:
                    data = q.get(timeout=2)
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "").lower()
                        
                        if text:
                            logger.info(f"Recognized: {text}")
                            full_text += " " + text
                    
                    # Check if we have a substantial question
                    # After collecting enough text or if silence is detected
                    partial = json.loads(rec.PartialResult())
                    if partial.get("partial", "") == "" and full_text:
                        # If there's silence and we already have text, return it
                        return full_text.strip()
                        
                except queue.Empty:
                    # If queue is empty for a while and we have text, consider it complete
                    if full_text:
                        return full_text.strip()
                    continue
                except Exception as e:
                    logger.error(f"Error in question recognition: {e}")
                    return None
            
            # If we've been listening for a while and have text, return it
            if full_text:
                return full_text.strip()
            
            # Get any final text
            result = json.loads(rec.FinalResult())
            final_text = result.get("text", "")
            if final_text:
                return (full_text + " " + final_text).strip()
                
    except Exception as e:
        logger.error(f"Error in speech recognition: {e}")
        return None
    
    return None

def get_user_question() -> str:
    """
    Main function to get user questions. This function is called from the main thread
    and handles the state management for question processing.
    
    Returns:
        str: The user's question if one is detected, otherwise None
    """
    global _is_processing, _last_process_time
    
    # Only allow a new question after a cooldown period (3 seconds)
    current_time = time.time()
    if _is_processing and current_time - _last_process_time < 3:
        return None
    
    # Reset processing state if it's been too long
    if _is_processing and current_time - _last_process_time > 10:
        _is_processing = False
    
    # If we're not currently processing a question, try to get one
    if not _is_processing:
        _is_processing = True
        _last_process_time = current_time
        
        # Actually listen for a question
        question = listen_for_question()
        
        if question:
            # Return the question and keep processing state to avoid immediate re-triggering
            _is_processing = False  # Reset to allow new questions
            return question
        else:
            # No question detected, reset processing state
            _is_processing = False
            
    return None