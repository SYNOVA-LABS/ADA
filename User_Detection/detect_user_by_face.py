import cv2
import os
import numpy as np
import face_recognition
import time
import hashlib
import logging
from datetime import datetime
from store_user import storeface

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize constants
FACES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_faces")
if not os.path.exists(FACES_FOLDER):
    os.makedirs(FACES_FOLDER)
    logger.info(f"Created faces folder at {FACES_FOLDER}")

# Function to load known faces from the faces folder
def load_known_faces():
    known_face_encodings = []
    known_face_names = []
    
    logger.info("Loading known faces from database...")
    for filename in os.listdir(FACES_FOLDER):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(FACES_FOLDER, filename)
            face_image = face_recognition.load_image_file(image_path)
            
            # Try to find a face in the image
            face_encodings = face_recognition.face_encodings(face_image)
            if face_encodings:
                face_encoding = face_encodings[0]
                known_face_encodings.append(face_encoding)
                
                # Use filename without extension as the person's name
                name = os.path.splitext(filename)[0]
                known_face_names.append(name)
                logger.info(f"Loaded face: {name}")
            else:
                logger.warning(f"No face found in {filename}, skipping")
    
    logger.info(f"Loaded {len(known_face_encodings)} faces from database")
    return known_face_encodings, known_face_names

# Function to save a new face
def save_new_face(face_image):
    # Generate a unique name using timestamp and random hash
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_object = hashlib.md5(str(time.time()).encode())
    unique_id = hash_object.hexdigest()[:8]
    
    name = f"person_{timestamp}_{unique_id}"
    filename = f"{name}.jpg"
    file_path = os.path.join(FACES_FOLDER, filename)
    
    cv2.imwrite(file_path, face_image)
    logger.info(f"New face added to DB: {name}")
    
    storeface(face_image, name)
    
    return name, face_recognition.face_encodings(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))[0]

def main():
    # Load known faces
    known_face_encodings, known_face_names = load_known_faces()
    
    # Initialize video capture (0 for default webcam)
    video_capture = cv2.VideoCapture(0)
    
    if not video_capture.isOpened():
        logger.error("Failed to open webcam")
        return
    
    logger.info("Starting face recognition system...")
    
    # Variables for processing
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    last_saved_time = 0
    save_cooldown = 5  # Seconds to wait before saving another unknown face
    
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        if not ret:
            logger.error("Failed to capture frame")
            break
            
        # Only process every other frame to save time
        if process_this_frame:
            # Resize frame to 1/4 size for faster face recognition
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
            # Convert the image from BGR color (OpenCV) to RGB (face_recognition)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Find all the faces in the current frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known faces
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
                name = "Unknown"
                
                # If a match was found, use the first one
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    #logger.info(f"Face recognized: {name}")
                else:
                    logger.info("Face not in DB")
                    # Save unknown face if cooldown has elapsed
                    current_time = time.time()
                    if current_time - last_saved_time > save_cooldown:
                        # Get the face region in the original frame
                        top, right, bottom, left = face_locations[face_encodings.index(face_encoding)]
                        # Scale back up face locations since the frame we detected in was 1/4 size
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4
                        
                        # Extract the face image
                        face_image = frame[top:bottom, left:right]
                        
                        # Save the face and get the new name
                        try:
                            name, new_encoding = save_new_face(face_image)
                            known_face_names.append(name)
                            known_face_encodings.append(new_encoding)
                            last_saved_time = current_time
                        except Exception as e:
                            logger.error(f"Error saving new face: {e}")
                
                face_names.append(name)
        
        process_this_frame = not process_this_frame
        
        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            
            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        
        # Display face count
        face_count = len(face_locations)
        cv2.putText(frame, f"Faces: {face_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Display the resulting image
        cv2.imshow('Face Recognition', frame)
        
        # Hit 'q' on the keyboard to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    video_capture.release()
    cv2.destroyAllWindows()
    logger.info("Face recognition system stopped")

if __name__ == "__main__":
    main()
