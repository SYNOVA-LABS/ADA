"""
Wake word detection module for ADA.
This module provides functionality to detect a wake word/phrase to activate the system.
Currently using a simulated approach that returns True after a delay.
"""

import time
import logging

logger = logging.getLogger(__name__)


def wake_word_detector():
    """
    Simulates wake word detection with a simple timer.
    In a real implementation, this would use speech recognition or other methods.

    Returns:
        bool: True if wake word is detected, False otherwise
    """
    logger.info("Wake word detector activated")
    # In a real implementation, this would listen for a specific wake word
    # For now, just simulate detection with a timer
    time.sleep(5)  # Simulate waiting for the wake word
    logger.info("Wake word detected")
    return True
