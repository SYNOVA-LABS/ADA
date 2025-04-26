"""
Main entry point for the ADA system.
This module initializes the webcam, handles user detection and greets recognized users.
"""

import cv2  # OpenCV for video capture for user to see themselves
import logging
import sys
import os
import time
from pygame import mixer  # for playing audio files

# Add User_Detection to the system path to import modules
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "User_Detection")
)

from User_Detection.detect_user_by_face import detect_user
from Greet_User.greet_user import greet_user

# Set up logging (sys logger instead of print because it's more flexible)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Main function that coordinates video capture, user detection and greeting.

    This function initializes the webcam, loads known face data from the database,
    and processes video frames to detect and recognize faces. Once a user is
    detected, it greets them with audio while continuing to display the video
    feed without face detection boxes.
    """
    logger.info("Starting ADA system...")

    # Initialize audio system for greeting
    mixer.init()

    # Initialize video capture (0 for default webcam)
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        logger.error("Failed to open camera. Exiting.")
        return

    logger.info("Camera initialized successfully.")

    try:
        # Detect user with video feed
        logger.info("Starting user detection...")
        detected_user, is_new_user = detect_user(video_capture)

        # Greet the user if detected
        if detected_user:
            logger.info(f"User detected: {detected_user} (New user: {is_new_user})")

            # Greet the user with audio (non-blocking no stoping video feed)
            greet_user(detected_user, mixer)

            greeting_start_time = time.time()
            greeting_duration = 5  # Show greeting message for 5 seconds

            # Loop to keep showing video feed after recognition and greeting
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break

                # Calculate time elapsed since greeting started
                time_elapsed = time.time() - greeting_start_time

                # Show welcome message on screen for a few seconds
                if time_elapsed < greeting_duration:
                    # Draw a semi-transparent overlay for the greeting text
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (10, 10), (500, 100), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

                    # Draw the welcome message
                    cv2.putText(
                        frame,
                        f"Welcome, {detected_user}!",
                        (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )
                    cv2.putText(
                        frame,
                        "ADA system is ready",
                        (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2,
                    )

                # Display the frame
                cv2.imshow("ADA System", frame)

                # Break loop on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        else:
            logger.warning("No user was detected.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        # Release resources and close windows
        video_capture.release()
        cv2.destroyAllWindows()
        mixer.quit() # Clean up the audio mixer
        logger.info("ADA system stopped")


# Entry point for the script
if __name__ == "__main__":
    main()
