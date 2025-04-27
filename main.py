"""
Main entry point for the ADA system.
This module initializes the webcam, handles user detection and greets recognized users.
Then it continues to the core functionality of the ADA system.
"""

import cv2  # OpenCV for video capture for user to see themselves
import logging
import time
import threading
import os
from pygame import mixer  # for playing audio files

# Update imports to include the new function
from User_Detection.detect_user_by_face import detect_user, detect_user_with_registration_check, register_new_user
from Activator.listener import wake_word_detector
from User_Input.get_user_input import get_user_question
from Vision_GPT.vision_and_promt_processor import analyze_image_with_question
from TTS.text_to_speech import play_response_async, is_audio_playing

# Set up logging (sys logger instead of print because it's more flexible)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global session history file path - now in Vision_GPT logs folder
SESSION_HISTORY_PATH = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Vision_GPT", "logs"), "session_history.log")

def init_session_history():
    """
    Initialize the session history log file.
    This file will store Q&A pairs without timestamps for LLM context.
    """
    try:
        # Create or truncate the session history file
        with open(SESSION_HISTORY_PATH, 'w') as f:
            f.write("ADA SESSION HISTORY\n")
            f.write("==================\n\n")
        logger.info(f"Session history initialized at {SESSION_HISTORY_PATH}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize session history: {e}")
        return False

def add_to_session_history(question, answer):
    """
    Add a Q&A pair to the session history log.
    
    Args:
        question: The user's question
        answer: ADA's response
    """
    try:
        with open(SESSION_HISTORY_PATH, 'a') as f:
            f.write(f"Q: {question}\n")
            f.write(f"A: {answer}\n\n")
    except Exception as e:
        logger.error(f"Failed to update session history: {e}")

def cleanup_session_history():
    """
    Clean up the session history file.
    """
    try:
        if os.path.exists(SESSION_HISTORY_PATH):
            logger.info(f"Session history saved at {SESSION_HISTORY_PATH}")
    except Exception as e:
        logger.error(f"Error handling session history cleanup: {e}")


def init_systems() -> tuple:
    """
    Initialize audio and video capture systems.

    Returns:
        tuple: (video_capture, success) where success is a boolean indicating if initialization was successful
    """
    logger.info("Starting ADA system...")

    # Initialize session history
    history_success = init_session_history()
    if not history_success:
        logger.warning("Failed to initialize session history, continuing without it")

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
        "Waiting for wake word try say 'hey ada' or 'hi'...",
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


def perform_user_detection(video_capture: cv2.VideoCapture, detection_status: dict) -> None:
    """
    Perform user detection in a separate thread.

    Args:
        video_capture: Video capture object
        detection_status: Dictionary to pass detection results back to main thread
    """
    logger.info("Starting user detection in thread...")
    try:
        # We need to use the main thread for user input dialogs
        # Just detect if there's a face and whether it's recognized
        # Flag if a new user needs to be registered, but don't register yet
        detected_user, is_new_user, needs_registration, face_image = detect_user_with_registration_check(video_capture)
        
        # Pass results back through the shared dictionary
        detection_status["complete"] = True
        detection_status["user"] = detected_user
        detection_status["is_new"] = is_new_user
        detection_status["needs_registration"] = needs_registration
        detection_status["face_image"] = face_image
        
        logger.info(f"Detection thread completed: user={detected_user}, is_new={is_new_user}, needs_registration={needs_registration}")
    except Exception as e:
        logger.error(f"Error in detection thread: {e}")
        detection_status["complete"] = True
        detection_status["error"] = str(e)


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
    Now uses the integrated Vision GPT module for processing.

    Args:
        frame: Current video frame to display
    """
    # Initialize the question thread and state variables if not already done
    if not hasattr(activate_ada, "question_thread"):
        activate_ada.question_thread = None
        activate_ada.current_question = None
        activate_ada.question_time = None
        activate_ada.current_response = None
        activate_ada.processing_question = False
        activate_ada.vision_response = None
        activate_ada.last_processed_question = None
        activate_ada.response_played = False
        activate_ada.listening_for_new_question = True
        activate_ada.last_listening_start = time.time()
        activate_ada.last_reset_time = time.time()
        activate_ada.display_until = 0
    
    # Function to check for questions
    def check_for_question():
        try:
            # Set the state to processing
            activate_ada.processing_question = True
            activate_ada.listening_for_new_question = False
            
            # Clear previous responses
            activate_ada.vision_response = None
            
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
                activate_ada.question_time = time.time()
                activate_ada.last_processed_question = result
                activate_ada.response_played = False
                logger.info(f"User asked: {result}")
                
                # Set display timeout - show for 15 seconds or until next question
                activate_ada.display_until = time.time() + 15
                
                # Create a copy of the current frame to send for processing
                current_frame_copy = frame.copy()
                
                # Process the question and frame together with the Vision GPT module
                vision_response = analyze_image_with_question(current_frame_copy, result)
                activate_ada.vision_response = vision_response
                logger.info(f"Vision response: {vision_response}")
                
                # Add to session history
                add_to_session_history(result, vision_response)
                
                # Play the response using TTS only once
                if vision_response and vision_response.strip() and not activate_ada.response_played:
                    # Play the response once and mark it as played
                    response_thread = threading.Thread(
                        target=play_response_async, args=(vision_response,)
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
        # This function now checks if audio is still playing
        def reset_listening_state():
            try:
                # Wait for audio playback to complete instead of fixed delay
                while is_audio_playing():
                    time.sleep(0.5)  # Check every half second
                
                # Once audio has finished, a small buffer to prevent immediate reactivation
                time.sleep(1)
                
                # Reset states
                activate_ada.processing_question = False
                activate_ada.listening_for_new_question = True
                activate_ada.last_listening_start = time.time()
                activate_ada.last_reset_time = time.time()
                logger.info("Audio playback completed - Ready for next question")
                
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
    
    # Safety checks and recovery code
    current_time = time.time()
    
    # Safety check - make sure these attributes exist with valid values
    if not hasattr(activate_ada, "last_reset_time"):
        activate_ada.last_reset_time = current_time
        
    if not hasattr(activate_ada, "question_time") or activate_ada.question_time is None:
        activate_ada.question_time = current_time
    
    # Emergency recovery - if the system seems stuck for more than 30 seconds
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
    # 4. Audio is not currently playing
    if (activate_ada.question_thread is None or not activate_ada.question_thread.is_alive()) and \
       not activate_ada.processing_question and \
       activate_ada.listening_for_new_question and \
       not is_audio_playing():
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
        
        # Display Vision GPT response if available
        if activate_ada.vision_response:
            vision_response = activate_ada.vision_response
            
            # Split response into multiple lines if it's too long
            max_chars = 50
            if len(vision_response) > max_chars:
                lines = []
                current_line = vision_response
                while len(current_line) > max_chars:
                    # Try to split at spaces to avoid cutting words
                    split_point = current_line[:max_chars].rfind(' ')
                    if split_point == -1:  # If no space found, force split
                        split_point = max_chars
                    
                    lines.append(current_line[:split_point])
                    current_line = current_line[split_point:].strip()
                
                if current_line:  # Add the last part if anything remains
                    lines.append(current_line)
                
                # Display the first two lines only to avoid overcrowding
                for i, line in enumerate(lines[:2]):
                    cv2.putText(
                        frame,
                        f"A: {line}",
                        (20, 100 + i*30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2,
                    )
                
                # Indicate if there's more text
                if len(lines) > 2:
                    cv2.putText(
                        frame,
                        "...",
                        (20, 160),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2,
                    )
            else:
                # If response is short enough, display it on a single line
                cv2.putText(
                    frame,
                    f"A: {vision_response}",
                    (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
    elif activate_ada.current_question:
        # If we've passed the display timeout, explicitly clear the display
        activate_ada.current_question = None
        activate_ada.vision_response = None
        logger.info("Cleared question display due to timeout")
    
    # Additional timer-based clearing mechanism
    if hasattr(activate_ada, 'display_until') and time.time() > activate_ada.display_until and activate_ada.current_question is not None:
        activate_ada.current_question = None
        activate_ada.vision_response = None
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
        if is_audio_playing():
            status_text += " - Playing response"
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
        detection_started = False
        detection_completed = False
        greeting_completed = False
        greeting_started = False

        # Other variables
        wake_thread = None
        detected_user = None
        is_new_user = False
        detection_thread = None
        greeting_start_time = 0
        face_registration_done = False  # New flag to track if registration is complete

        # Use dictionaries to track status between threads and main function
        wake_word_status = {"detected": False}
        detection_status = {"complete": False, "user": None, "is_new": False, "needs_registration": False, "face_image": None, "error": None}

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

            # STATE 2: Wake word detected, start user detection (non-blocking)
            elif not detection_started:
                # Show detecting message but don't block
                cv2.putText(
                    frame,
                    "Detecting user...",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 165, 255),
                    2,
                )
                
                # Start detection in a separate thread
                detection_thread = threading.Thread(
                    target=perform_user_detection,
                    args=(video_capture, detection_status)
                )
                detection_thread.daemon = True
                detection_thread.start()
                
                detection_started = True
                face_registration_done = False  # Reset registration flag
                logger.info("User detection started in background thread")
            
            # Check if detection is complete
            elif detection_started and not detection_completed:
                # Show that detection is in progress
                cv2.putText(
                    frame,
                    "Detecting user...",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 165, 255),
                    2,
                )
                
                # Check if the detection thread has completed
                if detection_status["complete"]:
                    detection_completed = True
                    detected_user = detection_status["user"]
                    is_new_user = detection_status["is_new"]
                    
                    # Handle new user registration if needed
                    if detection_status.get("needs_registration", False) and not face_registration_done:
                        # Show registration message
                        cv2.putText(
                            frame,
                            "New user detected! Please enter your name...",
                            (20, 80),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 255),
                            2,
                        )
                        cv2.imshow("ADA System", frame)
                        cv2.waitKey(1)  # Update the display
                        
                        try:
                            # Get the face image from the detection thread
                            face_image = detection_status.get("face_image")
                            if face_image is not None:
                                # Register the new user in the main thread so dialog windows work properly
                                face_id, name, auth = register_new_user(face_image)
                                if name:
                                    detected_user = name
                                    logger.info(f"New user registered: {name} (ID: {face_id}, Auth: {auth})")
                                face_registration_done = True
                            else:
                                logger.error("Face image not available for registration")
                                face_registration_done = True  # Skip registration
                        except Exception as e:
                            logger.error(f"Error during user registration: {e}")
                            face_registration_done = True  # Mark as done even on error
                    
                    # Only proceed with user detection if we have a user
                    if detected_user:
                        user_detected = True
                        logger.info(
                            f"User detected: {detected_user} (New user: {is_new_user})"
                        )
                        # Don't start greeting yet, just set the flag to start it
                        greeting_start_time = time.time()
                        greeting_started = False
                    else:
                        logger.warning("No user was detected.")

            # STATE 3: User detected, show greeting for specified duration
            elif user_detected and not greeting_completed:
                # Start the greeting in a separate thread when we first enter this state
                if not greeting_started:
                    def play_greeting():
                        try:
                            # Play the greeting asynchronously
                            play_response_async(
                                f"Hello {detected_user}, welcome to ADA, your personal digital assistant.")
                        except Exception as e:
                            logger.error(f"Error playing greeting: {e}")
                    
                    # Start the greeting thread
                    greeting_thread = threading.Thread(target=play_greeting)
                    greeting_thread.daemon = True
                    greeting_thread.start()
                    greeting_started = True
                
                # Keep displaying the visual greeting while the audio plays
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
        
        # Clean up session history
        cleanup_session_history()
        
        logger.info("ADA system stopped")


# Entry point for the script
if __name__ == "__main__":
    main()
