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
from store_user import storeface

# Set up logging (sys logger instead of print because it's more flexible)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# pull known faces from the folder of faces pics if DNE it creates it
FACES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_faces")
if not os.path.exists(FACES_FOLDER):
    os.makedirs(FACES_FOLDER)
    logger.info(f"Created faces folder at {FACES_FOLDER}")

# Function to load known faces from the faces folder and store them in the current session
def load_known_faces():
    # current sessions known faces (dynamic, will have new faces added later)
    known_face_encodings = [] # a encoding is a 128D vector that represents the face for the computer to work with
    known_face_names = []
    
    logger.info("Loading known faces from database...")
    # for each face in the folder of faces
    for filename in os.listdir(FACES_FOLDER):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(FACES_FOLDER, filename)
            face_image = face_recognition.load_image_file(image_path)
            
            # Try to find a face in the image and if found, get the encoding and store it along with the name (which is the filename)
            face_encodings = face_recognition.face_encodings(face_image)
            if face_encodings:
                # Use the first encoding found (the encoding is a list of encodings for each face found we just take the first one)
                # though this may seem bad this is only the case for pre uploaded faces where many faces are in the same image
                # when the program adds a new face it adds it one at a time so this is not an issue when using the program's capture
                face_encoding = face_encodings[0]
                known_face_encodings.append(face_encoding)
                
                # Use filename without extension as the person's name
                name = os.path.splitext(filename)[0]
                known_face_names.append(name)
                logger.info(f"Loaded face: {name}")
            else:
                logger.warning(f"No face found in {filename}, skipping") # skip non faces
    
    logger.info(f"Loaded {len(known_face_encodings)} faces from database")
    return known_face_encodings, known_face_names # return the known faces and their names

# Function to save a new face if not already in the database
def save_new_face(face_image):
    # Generate a unique name using timestamp and random hash for no duplicates
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_object = hashlib.md5(str(time.time()).encode())
    unique_id = hash_object.hexdigest()[:8]
    
    name = f"person_{timestamp}_{unique_id}"
    filename = f"{name}.jpg"
    file_path = os.path.join(FACES_FOLDER, filename)
    
    # save the face image to the folder
    cv2.imwrite(file_path, face_image)
    logger.info(f"New face added to DB: {name}")
    
    # return the name and the encoding of the new face to be added to the current session, once we reset the program it will be loaded from the folder
    return name, face_recognition.face_encodings(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))[0]

def main():
    # Load known faces (db of faces) each time the program starts then it will grow as we add new faces
    # but when the program starts again it will lead all those faces we recognized from the last session from the folder of faces
    known_face_encodings, known_face_names = load_known_faces()
    
    # Initialize video capture (0 for default webcam)
    video_capture = cv2.VideoCapture(0)
    
    if not video_capture.isOpened():
        logger.error("Failed to open webcam")
        return
    
    logger.info("Starting face recognition system...")
    
    # Variables for processing the video stream (current frame)
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    last_saved_time = 0
    save_cooldown = 5  # Seconds to wait before saving another unknown face preventing duplicate saves, still we process and display the face recognition but just dont save it to the db
    
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
                        except Exception as e:
                            logger.error(f"Error saving new face: {e}")
                
                face_names.append(name) # add the name to the list of face names for the current frame this is done regardless of whether a match was found or not if nothing was found then the face will be unknown (this is quite impossible as that means the saving of the face failed + the face was not in the db)
        
        process_this_frame = not process_this_frame # Toggle the process_this_frame variable to process every other frame if we did this frame skip the next one and vice versa
        
        # Display the results on the frame (window)
        for (top, right, bottom, left), name in zip(face_locations, face_names): # for each face location and name in the current frame
            # Scale back up face locations since the frame we detected in was 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2) # red box
            
            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED) # red text box
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1) # white text
        
        # Display face count in the corner of the frame
        face_count = len(face_locations)
        cv2.putText(frame, f"Faces: {face_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Display the resulting image with all the boxes and names
        cv2.imshow('Face Recognition', frame)
        
        # Hit 'q' on the keyboard to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources and close windows
    video_capture.release()
    cv2.destroyAllWindows()
    logger.info("Face recognition system stopped")

# Run
if __name__ == "__main__":
    main()
