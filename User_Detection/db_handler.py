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
from datetime import datetime
from .new_user_input import generate_unique_username, get_user_input_opencv

logger = logging.getLogger(__name__)  # system logger

# Database location, if DNE it will make the db
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_data.db")
FACES_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "user_faces"
)  # the detect user file makes this if it DNE


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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        face_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        authorization TEXT,
        encoding BLOB NOT NULL,
        image_path TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL
    )
    """)

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
    init_database()  # create the database if it doesn't exist

    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT face_id, name, encoding FROM faces"
    )  # get all face id's and encodings
    rows = cursor.fetchall()  # get all rows i.e all faces

    # Initialize lists to store encodings and names
    known_face_encodings = []
    known_face_names = []

    # Iterate over the rows and unpickle the encodings (i.e binary to numpy array which is the encoding type). then add to the list (all faces in db are known)
    for face_id, name, encoding_blob in rows:
        try:
            # Unpickle the encoding from the binary blob
            encoding = pickle.loads(encoding_blob)
            known_face_encodings.append(encoding)  # add the encoding to the list
            known_face_names.append(name)  # add the name to the list
            logger.info(f"Loaded face: {name} (ID: {face_id})")
        except Exception as e:
            logger.error(f"Error loading face {face_id}: {e}")

    # Close the database connection
    conn.close()
    logger.info(f"Loaded {len(known_face_encodings)} faces from database")

    return (
        known_face_encodings,
        known_face_names,
    )  # return the list of encodings and names


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
    init_database()  # create the database if it doesn't exist

    # get the image for the users face we just detected to show to them and get input
    face_image = cv2.imread(image_path)
    if face_image is None:  # if the image is not found default to guest
        logger.error(f"Cannot read image at {image_path}")
        name = generate_unique_username()
        auth = "guest"
    else:  # if the image is found
        try:
            # Get user input using OpenCV window
            name, auth = get_user_input_opencv(face_image)
        except Exception as e:
            logger.error(f"Error getting user input: {e}")
            name = generate_unique_username()
            auth = "guest"

    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Pickle the encoding to store as binary for the database
        encoding_blob = pickle.dumps(face_encoding)

        # Insert new face data
        cursor.execute(
            """
        INSERT INTO faces (face_id, name, authorization, encoding, image_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (face_id, name, auth, encoding_blob, image_path, datetime.now()),
        )

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        logger.info(
            f"Stored new face in database: {name} (ID: {face_id}, Auth: {auth})"
        )

        # return the name of the user for the face we just stored to be displayed to the user right after we detect them
        # this way we can add the username for faces that were added in the current session without having to get it from the db again or restart the program
        # when we restart the program we will load the db and get the name from there
        return name

    except Exception as e:
        logger.error(f"Error storing face data: {e}")
        return generate_unique_username()
