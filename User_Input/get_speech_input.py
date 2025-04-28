"""
Module for getting user input through the microphone.
This module handles capturing and processing user questions using local speech recognition.
the module listens for a question, processes it, and returns the recognized text.
under the hood it uses the Vosk speech recognition library for offline processing.
- it starts by listening for a question after a short delay if no question is detected it will go back to listening
- it will repeat this process until a question is detected or the timeout is reached.
"""

import logging
import os
import queue
import json
import time
import sounddevice as sd  # audio input/output library
from vosk import (
    Model,
    KaldiRecognizer,
)  # Vosk speech recognition library to recognize speech

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


def listen_for_question() -> str | None:
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
        def callback(indata: bytes, frames: int, time: float, status: sd.CallbackFlags):
            if status:
                logger.warning(f"Audio status: {status}")
            q.put(bytes(indata))

        # Use a timeout to prevent indefinite listening
        start_time = time.time()
        timeout = 10  # seconds to wait for a question if nothing happens in that time we start the process again and wait for a new question

        # Start listening
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            rec = KaldiRecognizer(model, SAMPLE_RATE)
            full_text = ""  # Initialize full_text to store recognized text

            while (
                time.time() - start_time < timeout
            ):  # loop for a maximum of 10 seconds (timeout)
                try:
                    data = q.get(
                        timeout=2
                    )  # wait for audio data for 2 seconds before checking again meaning if we get any data in 2 seconds we flag that as a question an continue listening to that question
                    if rec.AcceptWaveform(data):  # if data was speech
                        result = json.loads(rec.Result())
                        text = result.get("text", "").lower()

                        if text:
                            logger.info(f"Recognized: {text}")
                            full_text += " " + text

                    # Check if we have a substantial question
                    # After collecting enough text or if silence is detected
                    partial = json.loads(
                        rec.PartialResult()
                    )  # get partial result which is the text that was recognized so far during the current 2 second period
                    if (
                        partial.get("partial", "") == "" and full_text
                    ):  # if we have silence for 2 seconds and some text thats means the user is done speaking
                        return (
                            full_text.strip()
                        )  # return the full text as thast the final result

                except queue.Empty:
                    # If queue is empty for a while and we have text, consider it complete
                    if full_text:
                        return full_text.strip()
                    continue
                except Exception as e:
                    logger.error(f"Error in question recognition: {e}")
                    return None

            # If we've been listening for a while (10 seconds) and have text, return it 10 seconds is the maximum time we will wait for a question
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


def get_user_question() -> str | None:
    """
    Main function to get user questions. This function is called from the main thread
    and handles the state management for question processing.
    it has global variables to manage the state of the question processing so when the main function calls this function it will check if the _is_processing flag is set to true or false which is preserved across function calls

    Returns:
        str: The user's question if one is detected, otherwise None
    """
    global _is_processing, _last_process_time  # Use global variables to manage state so we can reuse the same variables across function calls (i.e if _is_processing is set to false and we return in the next call it will be set to false)

    # Only allow a new question after a cooldown period (3 seconds) if its been less than 3 seconds since the last question return None
    current_time = time.time()
    if _is_processing and current_time - _last_process_time < 3:
        return None

    # Reset processing state if it's been too long (10 seconds) since the last question. after 10 sec we set the processing state to false as we are not processing anything after that
    if _is_processing and current_time - _last_process_time > 10:
        _is_processing = False

    # If we're not currently processing a question, try to get one (first time or after cooldown once again)
    if not _is_processing:
        _is_processing = True
        _last_process_time = current_time

        # Actually listen for a question
        question = listen_for_question()

        # If a question is detected, process it and return it if not try to get a question again
        # since this function is caled repetively if the _is_processing flag is set to flase thats means when the function is called again we will try to get a question again
        # in the main function we will wait for the question to be detected if not call function again where the _is_processing flag will be set to false from the previous call
        if question:
            # Return the question and keep processing state to avoid immediate re-triggering
            _is_processing = False  # Reset to allow new questions
            return question
        else:
            # No question detected, reset processing state
            _is_processing = False

    return None  # if no question is detected return None so we can try again from main function (flags preserved as there global)
