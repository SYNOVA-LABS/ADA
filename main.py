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
from User_Input.get_user_input import get_user_question
from LLM_CV_Context_Questions.LLM_context_for_CV import log_user_question, play_response_async
from CV_Context.frame_context import process_frame_with_context

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
    Activate ADA core functionality. Displays system status and processes user questions.
    The actual question handling logic is in the User_Input module.

    Args:
        frame: Current video frame to display
    """
    # Initialize the question thread and state variables if not already done
    if not hasattr(activate_ada, "question_thread"):
        activate_ada.question_thread = None
        activate_ada.current_question = None
        activate_ada.question_time = None  # Initialize to current time, not None
        activate_ada.current_response = None
        activate_ada.processing_question = False
        activate_ada.cv_context = None
        activate_ada.cv_response = None
        activate_ada.last_processed_question = None
        activate_ada.response_played = False
        activate_ada.listening_for_new_question = True
        activate_ada.last_listening_start = time.time()  # Initialize with current time
        activate_ada.last_reset_time = time.time()  # Initialize with current time
        activate_ada.display_until = 0  # New: track when to clear display
    
    # Function to check for questions
    def check_for_question():
        try:
            # Set the state to processing
            activate_ada.processing_question = True
            activate_ada.listening_for_new_question = False
            
            # Clear previous responses
            activate_ada.cv_context = None
            activate_ada.cv_response = None
            
            # Get the user's question
            result = get_user_question()
            
            if result:
                # Check if this is a duplicate of the last question to prevent processing again
                if (activate_ada.last_processed_question is not None and 
                    result == activate_ada.last_processed_question and 
                    activate_ada.question_time is not None and
                    time.time() - activate_ada.question_time < 15):
                    logger.info("Received duplicate question, ignoring")
                    activate_ada.processing_question = False
                    # Important: Don't restart listening immediately for duplicates
                    time.sleep(3)  # Pause before allowing listening again
                    activate_ada.listening_for_new_question = True
                    return
                
                # Store the new question and reset state
                activate_ada.current_question = result
                activate_ada.question_time = time.time()  # Set the time here
                activate_ada.last_processed_question = result
                activate_ada.response_played = False
                logger.info(f"User asked: {result}")
                
                # Set display timeout 
                activate_ada.display_until = time.time() + 10  # Show for 10 seconds
                
                # Send the question to LLM to generate CV context
                cv_context = log_user_question(result)
                activate_ada.cv_context = cv_context
                
                # Send the current frame and CV context to the frame_context module
                if cv_context:
                    # Create a copy of the current frame to send for processing
                    current_frame_copy = frame.copy()
                    cv_response = process_frame_with_context(current_frame_copy, cv_context)
                    activate_ada.cv_response = cv_response
                    logger.info(f"CV response: {cv_response}")
                    
                    # Play the response using TTS only once
                    if cv_response and cv_response.strip() and not activate_ada.response_played:
                        # Play the response once and mark it as played
                        response_thread = threading.Thread(
                            target=play_response_async, args=(cv_response,)
                        )
                        response_thread.daemon = True
                        response_thread.start()
                        activate_ada.response_played = True
            else:
                logger.info("No question detected")
                # Important: Ensure we reset state even if no result detected
                activate_ada.processing_question = False
                activate_ada.listening_for_new_question = True
                return
                
        except Exception as e:
            logger.error(f"Error in question processing: {e}")
            # Important: Reset state on error to prevent system from getting stuck
            activate_ada.processing_question = False
            activate_ada.listening_for_new_question = True
            return
        
        # After processing, reset the state to listen for a new question
        # This timer ensures we don't immediately start listening again
        def reset_listening_state():
            try:
                # Longer timeout (5 seconds) to ensure we don't pick up the same input twice
                time.sleep(5)
                activate_ada.processing_question = False
                
                # Only set listening to true if enough time has passed since the last question
                # Make sure question_time is not None before doing comparison
                if activate_ada.question_time is not None and time.time() - activate_ada.question_time > 7:
                    activate_ada.listening_for_new_question = True
                    # Update the timestamp when we start listening again
                    activate_ada.last_listening_start = time.time()
                    activate_ada.last_reset_time = time.time()
                    logger.info("Ready for next question")
                else:
                    # If not enough time has passed, set a timer to check again
                    activate_ada.listening_for_new_question = True
                    activate_ada.last_listening_start = time.time()
                    activate_ada.last_reset_time = time.time()
                    logger.info("Ready for next question (early reset)")
            except Exception as e:
                logger.error(f"Error in reset_listening_state: {e}")
                # Emergency reset
                activate_ada.processing_question = False
                activate_ada.listening_for_new_question = True
                activate_ada.last_listening_start = time.time()
                activate_ada.last_reset_time = time.time()
        
        # Start the timer in a separate thread
        reset_thread = threading.Thread(target=reset_listening_state)
        reset_thread.daemon = True
        reset_thread.start()
    
    # Emergency recovery - if the system seems stuck
    current_time = time.time()
    
    # Safety check - make sure these attributes exist with valid values
    if not hasattr(activate_ada, "last_reset_time"):
        activate_ada.last_reset_time = current_time
        
    if not hasattr(activate_ada, "question_time") or activate_ada.question_time is None:
        activate_ada.question_time = current_time
    
    # If we've been stuck for more than 30 seconds, force a reset
    if current_time - activate_ada.last_reset_time > 30:
        logger.info("Periodic safety reset")
        activate_ada.processing_question = False
        activate_ada.listening_for_new_question = True
        activate_ada.last_listening_start = current_time
        activate_ada.last_reset_time = current_time
    
    # Start question detection thread if:
    # 1. Not already running
    # 2. Not currently processing a question
    # 3. We're ready to listen for a new question
    # 4. At least 5 seconds have passed since we last started listening
    listening_cooldown_passed = (current_time - activate_ada.last_listening_start) > 5
    
    if (activate_ada.question_thread is None or not activate_ada.question_thread.is_alive()) and \
       not activate_ada.processing_question and \
       activate_ada.listening_for_new_question and \
       listening_cooldown_passed:
        logger.info("Starting new listening thread")
        activate_ada.question_thread = threading.Thread(target=check_for_question)
        activate_ada.question_thread.daemon = True
        activate_ada.question_thread.start()
        activate_ada.last_listening_start = current_time
    
    # Display current question and response if available and within display time
    if activate_ada.current_question and (not hasattr(activate_ada, 'display_until') or time.time() < activate_ada.display_until):
        question = activate_ada.current_question
        
        # Create semi-transparent background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 50), (620, 140), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Display the original question on the frame
        cv2.putText(
            frame,
            f"Q: {question[:50]}{'...' if len(question) > 50 else ''}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 165, 0),
            2,
        )
        
        # Display CV context if available
        if activate_ada.cv_context:
            cv_context = activate_ada.cv_context
            cv2.putText(
                frame,
                f"CV: {cv_context[:50]}{'...' if len(cv_context) > 50 else ''}",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )
        
        # Display CV response if available
        if activate_ada.cv_response:
            cv_response = activate_ada.cv_response
            cv2.putText(
                frame,
                f"A: {cv_response[:50]}{'...' if len(cv_response) > 50 else ''}",
                (20, 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )
    elif activate_ada.current_question:
        # If we've passed the display timeout, explicitly clear the display
        activate_ada.current_question = None
        activate_ada.cv_context = None
        activate_ada.cv_response = None
        logger.info("Cleared question display due to timeout")
    
    # Additional timer-based clearing mechanism
    if hasattr(activate_ada, 'display_until') and time.time() > activate_ada.display_until and activate_ada.current_question is not None:
        activate_ada.current_question = None
        activate_ada.cv_context = None
        activate_ada.cv_response = None
        logger.info("Cleared question display due to timeout (secondary check)")
    
    # Show processing indicator if currently processing a question
    if activate_ada.processing_question:
        status = "Processing..." if not activate_ada.response_played else "Processed"
        cv2.putText(
            frame,
            status,
            (frame.shape[1] - 180, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 165, 255) if not activate_ada.response_played else (0, 255, 0),
            2,
        )
    
    # Always show the system is active
    status_text = "ADA system active"
    if activate_ada.listening_for_new_question and not activate_ada.processing_question:
        cooldown_remaining = max(0, 5 - (time.time() - activate_ada.last_listening_start))
        if cooldown_remaining > 0:
            status_text += f" - Ready in {int(cooldown_remaining)}s"
        else:
            status_text += " - Ready for question"
        
    cv2.putText(
        frame,
        status_text,
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
