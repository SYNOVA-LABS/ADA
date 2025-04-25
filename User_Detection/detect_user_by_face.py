""" 
This script uses OpenCV and face_recognition libraries to perform real-time face recognition.
the script captures video from the webcam, detects faces, and recognizes them against a database of known faces.
this way we can recognize users and store their faces to then give them access to the system with their personalized settings.
"""
import cv2
import os
import numpy as np
import face_recognition
import time
import hashlib
import logging
from datetime import datetime
from db_handler import load_face_data, store_face_data

# Set up logging (sys logger instead of print because it's more flexible)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# pull known faces from the folder of faces pics if DNE it creates it
FACES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_faces")
if not os.path.exists(FACES_FOLDER):
    os.makedirs(FACES_FOLDER)
    logger.info(f"Created faces folder at {FACES_FOLDER}")

def load_known_faces() -> tuple:
    """
    Load the known faces from the database.

    This function loads all the known faces stored in the SQLite database and returns two lists: one with the face encodings and one with the corresponding names.

    Returns:
        known_face_encodings (list[numpy.array]): A list of face encodings for the known faces.
        known_face_names (list[str]): A list of the names corresponding to the known faces.
    """
    
    logger.info("Loading known faces from database...")
    # Get face data from database
    known_face_encodings, known_face_names = load_face_data()
    logger.info(f"Loaded {len(known_face_encodings)} faces from database")
    return known_face_encodings, known_face_names

def save_new_face(face_image: np.ndarray) -> tuple:
    # Generate a unique ID using timestamp and hash
    """
    Save a new face image and store it in the database.

    This function takes a new face image, generates a unique ID for it, saves the image to the faces folder, gets the face encoding, stores the face data in the database, and prompts the user for a name. It returns the name and face encoding.

    Parameters:
        face_image (numpy.ndarray): The new face image.

    Returns:
        name (str): The user-provided name for the new face.
        face_encoding (numpy.ndarray): The face encoding for the new face.
    """
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_object = hashlib.md5(str(time.time()).encode())
    unique_id = hash_object.hexdigest()[:8]
    face_id = f"{timestamp}_{unique_id}"
    
    # Create the filename for storage
    filename = f"{face_id}.jpg"
    file_path = os.path.join(FACES_FOLDER, filename)
    
    # Save the face image to the folder
    cv2.imwrite(file_path, face_image)
    logger.info(f"New face image saved: {file_path}")
    
    # Get the face encoding
    rgb_face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
    face_encoding = face_recognition.face_encodings(rgb_face_image)[0]
    
    # Store the face data in database giving it a id, encoding and path and get the user-provided name back for the face, name also stored in the db
    name = store_face_data(face_id, face_encoding, file_path)
    
    return name, face_encoding

def detect_user(video_capture: cv2.VideoCapture) -> tuple:
    """
    Detect and identify a user from video feed.
    
    This function processes video frames to detect and recognize faces. If an unknown face is 
    detected and the cooldown period has elapsed, it saves the face image, encodes it,
    and updates the database. The function displays the video stream with detected 
    faces and their names, and continues until a user is recognized or added.
    NOTE: while the module supports multiple users via face locations allowing multiple faces in different locations we just take the first one recognized for now
    
    Parameters:
        video_capture: OpenCV VideoCapture object with an active video feed
        
    Returns:
        tuple: (recognized_name, is_new_user)
            - recognized_name (str): The name of the recognized or newly added user
            - is_new_user (bool): Whether the user was newly added to the database
    """

    # Load known faces (db of faces) each time the program starts then it will grow as we add new faces
    # but when the program starts again it will lead all those faces we recognized from the last session from the folder of faces
    known_face_encodings, known_face_names = load_known_faces()
    # if no video capture is found then we return None and False
    if not video_capture.isOpened():
        logger.error("Failed to open webcam")
        return None, False
    
    logger.info("Starting face recognition system...")
    
    # Variables for processing the video stream (current frame)
    face_locations = [] # list of tuples with the coordinates of the face in the format (top, right, bottom, left)
    face_encodings = [] # list of encodings for each face found in the frame
    face_names = [] # list of names for each face found in the frame
    process_this_frame = True # process every other frame to save time
    last_saved_time = 0 # time of the last saved face
    save_cooldown = 5  # Seconds to wait before saving another unknown face preventing duplicate saves, still we process and display the face recognition but just dont save it to the db
    
    recognized_user = None # name of the recognized user
    is_new_user = False # whether the user was newly added in which case its in curr session only 
    
    # Main loop for video capture
    while True:
        # Grab a single frame of video (each iteration is a new frame) even though we are processing every other frame we still need to display every frame to the user
        ret, frame = video_capture.read()
        if not ret:
            logger.error("Failed to capture frame")
            break
            
        # Only process every other frame to save time
        if process_this_frame:
            # Resize frame to 1/4 size for faster face recognition (lower if potato pc)
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25) # (0, 0) means to keep the aspect ratio while the fx and fy are the scaling factors for width and height respectively
            
            # Convert the image from BGR color (OpenCV) to RGB (face_recognition) this is necessary because face_recognition uses RGB color space while OpenCV uses BGR color space
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Find all the faces in the current frame using face_recognition library, then get the encodings for each face found the encoding is a 128D vector that represents the face for the computer to work with
            face_locations = face_recognition.face_locations(rgb_small_frame) # get the locations of the faces in the frame, this returns a list of tuples with the coordinates of the face in the format (top, right, bottom, left)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations) # get the encodings for each face found in the frame, this returns a list of encodings for each face found in the same order as the locations
            
            face_names = [] # reset the face names for the current frame so we can give each face a name as we process it beacuse for some frames a different face may be present so we reset it before we process the frame
            for face_encoding in face_encodings: # for each face in the frame
                # See if the face is a match for the known faces, this will return a list of True/False values for each known face
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6) # tolerance is the threshold for how close the encodings need to be to be considered a match, lower means more strict
                name = "Unknown" # set as unknown by default until we find a match for the face or we save it as a new face
                
                # If a match was found, use the first one i.e the first face that matches one of the known faces (index gets the first index of true in the list of matches)
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    logger.info(f"Face recognized: {name}")
                    recognized_user = name
                    is_new_user = False
                    # Return early with the recognized user to move on to greeting
                    return recognized_user, is_new_user
                # If no match was found, add the face to the database
                else:
                    logger.info("Face not in DB")
                    # Save unknown face ONLY if cooldown has elapsed
                    current_time = time.time()
                    if current_time - last_saved_time > save_cooldown:
                        # Get the face region in the original frame i.e get the top, right, bottom, left coordinates of the face from the face locations
                        # use the index func to the get the current face encoding's index in the face locations list this will return the current face almost always beacuse 2 encodings will not be the same (almost impossible as thats like saying 2 of the same faces in the curr frame)
                        # so all this dose is get the face location of the current face encoding in the list of face encodings as they are corresponding each index from face location has a corresponding index in the face encodings list
                        top, right, bottom, left = face_locations[face_encodings.index(face_encoding)]
                        # Scale back up face locations since the frame we detected in was 1/4 size, this way we save the original quality of the face
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4
                        
                        # Extract the face image by slicing the frame from the original frame this way we only get the face and not the whole frame
                        face_image = frame[top:bottom, left:right]
                        
                        # Save the face and get the new name
                        try:
                            name, new_encoding = save_new_face(face_image) # we pass the image of the face and get a encoding of this new face and the name of the new face
                            known_face_names.append(name) # add the name to the known faces list
                            known_face_encodings.append(new_encoding) # add the encoding to the known faces list
                            last_saved_time = current_time # update the last saved time to the current time so we can save another face after the cooldown
                            recognized_user = name
                            is_new_user = True
                            # Return early with the new user to move on to greeting
                            return recognized_user, is_new_user
                        except Exception as e:
                            logger.error(f"Error saving new face: {e}")
                
                face_names.append(name) # add the name to the list of face names for the current frame this is done regardless of whether a match was found or not if nothing was found then the face will be unknown (this is quite impossible as that means the saving of the face failed + the face was not in the db)
        
        process_this_frame = not process_this_frame # Toggle the process_this_frame variable to process every other frame if we did this frame skip the next one and vice versa
        
    return None, False # if no user was detected return None and False
