"""
this module is used to get the name and authorization level of a new user
it uses a popup window to display the face image and ask for input
the returned name and authorization level are used to store the face in the database
"""

import cv2
import time
import hashlib
from datetime import datetime


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


def get_user_input_opencv(face_image: cv2.Mat) -> tuple:
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
    name = None  # just a placeholder, if no name we generate one later
    auth = "guest"

    # Create a copy of the image to display it when asking for input
    display_img = face_image.copy()
    h, w = display_img.shape[:2]

    # Resize if
    max_height = 500
    ratio = max_height / h
    display_img = cv2.resize(display_img, (int(w * ratio), max_height))

    # Add text instructions
    cv2.putText(
        display_img,
        "New User Detected",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
    )
    cv2.putText(
        display_img,
        "Enter name and press ENTER",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
    )
    cv2.putText(
        display_img,
        "Or press ESC to skip naming",
        (10, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
    )

    # Show the image
    cv2.imshow("New User", display_img)

    # Initialize empty name
    input_name = ""

    # Process key inputs
    while True:
        # Show current input
        name_display = display_img.copy()
        cv2.putText(
            name_display,
            f"Name: {input_name}",
            (10, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
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
            else:  # if user pressed enter but no name was entered
                name = generate_unique_username()
            break
        elif key == 8 or key == 127:  # Backspace - remove last char
            input_name = input_name[:-1]
        elif 32 <= key <= 126:  # Printable ASCII characters
            input_name += chr(key)

    # Now ask for authorization if name was provided else default to guest
    if not name.startswith("User_"):
        auth_display = display_img.copy()
        cv2.putText(
            auth_display,
            f"Name: {name}",
            (10, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            auth_display,
            "Authorization: (g)uest, (u)ser, (a)dmin",
            (10, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        cv2.imshow("New User", auth_display)

        # Get authorization level
        key = cv2.waitKey(0) & 0xFF
        if key == ord("a"):
            auth = "admin"
        elif key == ord("u"):
            auth = "user"
        else:
            auth = "guest"

    # Close window
    cv2.destroyWindow("New User")

    return (
        name,
        auth,
    )  # return name and auth for the new regogized face to be stored in the db
