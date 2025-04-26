# Greet User Module

This module provides personalized audio greetings using text-to-speech technology for the ADA system.


## System Flowchart

```mermaid
flowchart TD
    A[Start: greet_user called] --> B{Check user name}
    B -->|name starts with 'User_'| C[Generic greeting]
    B -->|Regular name| D[Personalized greeting]
    C --> E[Create text-to-speech]
    D --> E
    E --> F[Save to temporary file]
    F --> G[Start daemon thread]
    G --> H[Return to main process]
    
    I[Thread: play_greeting_async] --> J[Load audio]
    J --> K[Play audio]
    K --> L[Wait for completion]
    L --> M[Delete temp file]
    M --> N[Log completion]

    style A fill:#d4f1f9
    style G fill:#d5f5e3
    style H fill:#d5f5e3
    style I fill:#fcf3cf
    style N fill:#fcf3cf
```

## Key Features

1. **Personalized Greetings**: Custom voice greetings using the user's recognized name
2. **Asynchronous Playback**: Background audio processing to keep the main application responsive
3. **Resource Management**: Automatic handling of temporary audio files
4. **Text-to-Speech**: Natural voice generation using Google's TTS service

## Implementation Details

- Uses gTTS for speech generation and Pygame mixer for playback
- Threading for non-blocking audio processing
- Integrates with the main application via shared mixer instance
- Distinguishes between known users and auto-generated usernames