"""
Database handler for face recognition system.
Handles storing and retrieving face data using SQLite.
"""
import os
import sqlite3
import numpy as np
import pickle
import logging
import cv2
import hashlib
import time
from datetime import datetime

logger = logging.getLogger(__name__) # system logger

# Database location, if DNE it will make the db
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_data.db")
FACES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_faces") # the detect user file makes this if it DNE

def init_database() -> None:
    """
    Initialize the SQLite database for storing face data.

    This function ensures the database and necessary directories exist.
    It creates a table 'faces' if it does not already exist, with columns 
    for storing face ID, name, authorization level, face encoding, 
    image path, and creation timestamp.

    Raises:
        sqlite3.Error: If an error occurs during database operations.
    """

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table for face data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        face_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        authorization TEXT,
        encoding BLOB NOT NULL,
        image_path TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")

def load_face_data() -> tuple:    
    """
    Load known face data from the SQLite database.

    This function initializes the database if needed and retrieves all stored
    face encodings and their associated names. It returns two lists: one with
    the face encodings and one with the corresponding names. Each face encoding
    is unpickled from a binary blob stored in the database.

    Returns:
        tuple: A tuple containing:
            - known_face_encodings (list[numpy.ndarray]): A list of face encodings.
            - known_face_names (list[str]): A list of names corresponding to the encodings.
    
    Logs:
        Information about each loaded face, including name and ID.
        Total number of faces loaded.
    
    Raises:
        Exception: If an error occurs during the unpickling of face encodings.
    """

    init_database() # create the database if it doesn't exist
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT face_id, name, encoding FROM faces") # get all face id's and encodings
    rows = cursor.fetchall() # get all rows i.e all faces
    
    # Initialize lists to store encodings and names
    known_face_encodings = []
    known_face_names = []
    
    # Iterate over the rows and unpickle the encodings (i.e binary to numpy array which is the encoding type). then add to the list (all faces in db are known)
    for face_id, name, encoding_blob in rows:
        try:
            # Unpickle the encoding from the binary blob
            encoding = pickle.loads(encoding_blob)
            known_face_encodings.append(encoding) # add the encoding to the list
            known_face_names.append(name) # add the name to the list
            logger.info(f"Loaded face: {name} (ID: {face_id})")
        except Exception as e:
            logger.error(f"Error loading face {face_id}: {e}")
    
    # Close the database connection
    conn.close()
    logger.info(f"Loaded {len(known_face_encodings)} faces from database")
    
    return known_face_encodings, known_face_names # return the list of encodings and names

def generate_unique_username() -> str:
    """
    Generate a unique username based on the current timestamp and a random hash.

    The format is: "User_<YYYYMMDDHHMMSS>_<6_CHAR_HASH>".

    Returns:
        str: A unique username as a string.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_object = hashlib.md5(str(time.time()).encode())
    unique_id = hash_object.hexdigest()[:6]
    return f"User_{timestamp}_{unique_id}"

def get_user_input_opencv(face_image: np.ndarray) -> tuple:
    """
    Display a face image and prompt the user to input their name and authorization level.

    This function uses OpenCV to display an image of a detected face, prompting the user 
    to enter a name via keyboard input. The user can confirm the name by pressing 'Enter' 
    or skip the naming process by pressing 'ESC', in which case a unique username is generated. 
    After entering a name, the user is prompted to select an authorization level by pressing 
    'g' for guest, 'u' for user, or 'a' for admin.
    NOTE: duplicte names are ok since it corresponds to the face id which is unique.

    Parameters:
        face_image (np.ndarray): The face image to be displayed.

    Returns:
        tuple: A tuple containing:
            - name (str): The entered or generated name for the user.
            - auth (str): The authorization level ('guest', 'user', or 'admin').
    """

    # default values
    name = None # just a placeholder, if no name we generate one later
    auth = "guest"
    
    # Create a copy of the image to display it when asking for input
    display_img = face_image.copy()
    h, w = display_img.shape[:2]
    
    # Resize if 
    max_height = 500
    ratio = max_height / h
    display_img = cv2.resize(display_img, (int(w * ratio), max_height))
    
    # Add text instructions
    cv2.putText(display_img, "New User Detected", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(display_img, "Enter name and press ENTER", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(display_img, "Or press ESC to skip naming", (10, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # Show the image
    cv2.imshow("New User", display_img)
    
    # Initialize empty name
    input_name = ""
    
    # Process key inputs
    while True:
        # Show current input
        name_display = display_img.copy()
        cv2.putText(name_display, f"Name: {input_name}", (10, 130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("New User", name_display)
        
        # Get key input (what user presses)
        key = cv2.waitKey(0) & 0xFF
        
        # Handle key
        if key == 27:  # ESC key - skip naming
            name = generate_unique_username()
            break
        elif key == 13:  # Enter key - finish input
            if input_name:
                name = input_name
            else: # if user pressed enter but no name was entered
                name = generate_unique_username()
            break
        elif key == 8:  # Backspace - remove last char
            input_name = input_name[:-1]
        elif 32 <= key <= 126:  # Printable ASCII characters
            input_name += chr(key)
    
    # Now ask for authorization if name was provided else default to guest
    if not name.startswith("User_"):
        auth_display = display_img.copy()
        cv2.putText(auth_display, f"Name: {name}", (10, 130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(auth_display, "Authorization: (g)uest, (u)ser, (a)dmin", (10, 170), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("New User", auth_display)
        
        # Get authorization level
        key = cv2.waitKey(0) & 0xFF
        if key == ord('a'):
            auth = "admin"
        elif key == ord('u'):
            auth = "user"
        else:
            auth = "guest"
    
    # Close window
    cv2.destroyWindow("New User")
    
    return name, auth # return name and auth for the new regogized face to be stored in the db

def store_face_data(face_id: str, face_encoding: np.ndarray, image_path: str) -> str:
    """
    Store new face data in the database.

    This function takes a face ID, face encoding, and image path as input, gets user input for the name and authorization level, and stores the data in the database.

    Parameters:
        face_id (str): Unique identifier for the face.
        face_encoding (numpy.ndarray): The face encoding.
        image_path (str): The path to the face image.

    Returns:
        str: The user-provided name for the new face.
    
    Raises:
        Exception: If an error occurs during database operations.
    """
    init_database() # create the database if it doesn't exist
    
    # get the image for the users face we just detected to show to them and get input
    face_image = cv2.imread(image_path)
    if face_image is None: # if the image is not found default to guest
        logger.error(f"Cannot read image at {image_path}")
        name = generate_unique_username()
        auth = "guest"
    else: # if the image is found
        # Get user input using OpenCV window 
        name, auth = get_user_input_opencv(face_image)
    
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pickle the encoding to store as binary for the database
        encoding_blob = pickle.dumps(face_encoding)
        
        # Insert new face data
        cursor.execute('''
        INSERT INTO faces (face_id, name, authorization, encoding, image_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (face_id, name, auth, encoding_blob, image_path, datetime.now()))
        
        # Commit changes and close the connection
        conn.commit()
        conn.close()
        
        logger.info(f"Stored new face in database: {name} (ID: {face_id}, Auth: {auth})")
        
        # return the name of the user for the face we just stored to be displayed to the user right after we detect them
        # this way we can add the username for faces that were added in the current session without having to get it from the db again or restart the program
        # when we restart the program we will load the db and get the name from there
        return name 
    
    except Exception as e:
        logger.error(f"Error storing face data: {e}")
        return generate_unique_username()
