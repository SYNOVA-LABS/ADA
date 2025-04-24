# Face Recognition System

This system uses OpenCV and face_recognition libraries to detect and recognize faces in real-time via webcam. It stores recognized users in a SQLite database for future identification. This way we can give each user a customized experence

- NOTE: the db and user_faces folder dose not exist but will be created upon the User_detection starting to the first time, both the db and faces folder are not commited for privacy

## System Flowchart

```mermaid
flowchart TD
    A[Start Program] --> B[Initialize System]
    B --> C[Load Known Faces from Database]
    C --> D[Start Webcam Capture]
    
    D --> E{Capture Successful?}
    E -- No --> Z[Exit Program]
    E -- Yes --> F[Process Video Frames]
    
    F --> G[Detect Faces in Frame]
    G --> H{Face Detected?}
    H -- No --> P
    
    H -- Yes --> I{Face in Database?}
    I -- Yes --> J[Display User Name]
    I -- No --> K{Cooldown Elapsed?}
    
    K -- No --> J
    K -- Yes --> L[Extract Face Image]
    L --> M[Save Image to Folder]
    M --> N[Prompt for User Details]
    N --> O[Store in Database]
    O --> J
    
    J --> P[Display Results]
    P --> Q{Quit Pressed?}
    Q -- Yes --> Z
    Q -- No --> F
    
    subgraph "Init"
        B
    end
    
    subgraph "Face Processing"
        G
        H
        I
        K
        L
        M
        N
        O
    end
    
    subgraph "Display Loop"
        F
        P
        Q
    end
```

## Key Features

1. **Face Detection**: Identifies faces in webcam video
2. **Face Recognition**: Compares detected faces against database of known faces
3. **User Management**: Adds new faces to database with user-provided information
4. **Database Storage**: Stores face encodings, images, and user information in SQLite
5. **Real-time Feedback**: Shows recognized users with name labels

## Implementation Details

- Uses face_recognition for accurate face detection and encoding
- SQLite database for storing user details and face data
- OpenCV for webcam capture and display
- Processes every other frame to improve performance
- Implements cooldown period to avoid duplicate entries
