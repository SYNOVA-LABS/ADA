"""
Main entry point for the ADA system.
This module initializes the webcam, handles user detection and greets recognized users.
Then it continues to the core functionality of the ADA system.
"""

import cv2  # OpenCV for video capture for user to see themselves
import logging
import time
import threading
from pygame import mixer  # for playing audio files

# Add User_Detection to the system path to import modules
from User_Detection.detect_user_by_face import detect_user
from Greet_User.greet_user import greet_user
from Activator.listener import wake_word_detector

# Set up logging (sys logger instead of print because it's more flexible)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def init_systems() -> tuple:
    """
    Initialize audio and video capture systems.

    Returns:
        tuple: (video_capture, success) where success is a boolean indicating if initialization was successful
    """
    logger.info("Starting ADA system...")

    # Initialize video capture (0 for default webcam)
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        logger.error("Failed to open camera. Exiting.")
        return video_capture, False

    logger.info("Camera initialized successfully.")

    return video_capture, True


def wait_for_wake_word(
    frame: cv2.Mat, wake_thread: threading.Thread, wake_word_status: dict
) -> tuple:
    """
    Display waiting message and handle wake word detection thread.

    Args:
        frame: Current video frame to display
        wake_thread: Thread object for wake word detection
        wake_word_status: Dictionary to track wake word detection status

    Returns:
        tuple: (updated_wake_thread, wake_word_detected)
    """
    # Display waiting message
    cv2.putText(
        frame,
        "Waiting for wake word...",
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2,
    )

    # Check if wake word has been detected (from the thread)
    wake_word_detected = wake_word_status.get("detected", False)

    # Start wake word detection thread if not already running
    if (wake_thread is None or not wake_thread.is_alive()) and not wake_word_detected:

        def check_wake_word():
            result = wake_word_detector()
            if result:
                wake_word_status["detected"] = True
                logger.info("Ada activated by wake word.")

        wake_thread = threading.Thread(target=check_wake_word)
        wake_thread.daemon = True
        wake_thread.start()

    return wake_thread, wake_word_detected


def perform_user_detection(frame: cv2.Mat, video_capture: cv2.VideoCapture) -> tuple:
    """
    Perform user detection once.

    Args:
        frame: Current video frame to display
        video_capture: Video capture object

    Returns:
        tuple: (detected_user, is_new_user)
    """
    # Show detecting message
    cv2.putText(
        frame,
        "Detecting user...",
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 165, 255),
        2,
    )
    cv2.imshow("ADA System", frame)
    cv2.waitKey(1)  # Update the display

    # Detect user once
    logger.info("Starting user detection...")
    return detect_user(video_capture)


def display_greeting(
    frame: cv2.Mat, detected_user: str, greeting_start_time: float
) -> bool:
    """
    Display welcome greeting on the frame.

    Args:
        frame: Current video frame to display
        detected_user: Name of the detected user
        greeting_start_time: Time when greeting started

    Returns:
        bool: True if greeting is complete, False otherwise
    """
    time_elapsed = time.time() - greeting_start_time
    greeting_duration = 5  # Show greeting message for 5 seconds

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
        return False
    else:
        logger.info("User initiation completed, continuing to ADA core functionality.")
        return True


def activate_ada(frame: cv2.Mat) -> None:
    """
    Activate ADA core functionality. This will be expanded in future versions.
    Currently just displays a message that ADA is active.

    Args:
        frame: Current video frame to display
    """
    logger.info("ADA core functionality activated")
    # Just show normal video feed without any detection
    # Can add a small indicator that system is active if desired
    cv2.putText(
        frame,
        "ADA system active",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
    )


def main() -> None:
    """
    Main entry point for the ADA system.
    Initializes the webcam, handles user detection and greets recognized users.
    The main application flow:
    1. Waiting for wake word
    2. User detection
    3. Greeting
    4. ADA core functionality
    """
    # Initialize systems
    video_capture, success = init_systems()
    if not success:
        return

    try:
        # Flag to control main application loop
        running = True

        # State flags
        waiting_for_wake_word = True
        user_detected = False
        detection_completed = False
        greeting_completed = False

        # Other variables
        wake_thread = None
        detected_user = None
        is_new_user = False

        # Use a dictionary to track wake word status between thread and main function
        wake_word_status = {"detected": False}

        logger.info("Waiting for wake word activation...")

        # Main application loop
        while running:
            # Capture frame from video
            ret, frame = video_capture.read()
            if not ret:
                logger.error("Failed to capture frame")
                break

            # STATE 1: Waiting for wake word
            if waiting_for_wake_word:
                wake_thread, wake_detected = wait_for_wake_word(
                    frame, wake_thread, wake_word_status
                )
                if wake_detected:
                    waiting_for_wake_word = False
                    # Reset the wake word status for next time
                    wake_word_status["detected"] = False

            # STATE 2: Wake word detected, start user detection (only once)
            elif not detection_completed:
                detected_user, is_new_user = perform_user_detection(
                    frame, video_capture
                )
                detection_completed = True  # Mark detection as completed

                if detected_user:
                    user_detected = True
                    logger.info(
                        f"User detected: {detected_user} (New user: {is_new_user})"
                    )
                    # Greet the user with audio (non-blocking)
                    greet_user(detected_user)
                    greeting_start_time = time.time()
                else:
                    logger.warning("No user was detected.")

            # STATE 3: User detected, show greeting for specified duration
            elif user_detected and not greeting_completed:
                greeting_completed = display_greeting(
                    frame, detected_user, greeting_start_time
                )

            # STATE 4: After greeting, activate ADA core functionality
            else:
                activate_ada(frame)

            # Display the frame (common for all states)
            cv2.imshow("ADA System", frame)

            # Check for 'q' key press (common for all states)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                running = False
                break

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        # Release resources and close windows
        video_capture.release()
        cv2.destroyAllWindows()
        mixer.quit()  # Clean up the audio mixer
        logger.info("ADA system stopped")


# Entry point for the script
if __name__ == "__main__":
    main()
