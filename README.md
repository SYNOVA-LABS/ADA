![model](assets/adalogo.svg)

# ADA (Advanced Digital Agent)

ADA is a modular, extensible personal assistant system that combines face recognition, contextual understanding, and natural language processing to provide a personalized interactive experience. This Project is a Part of,
[Proximum AI](https://github.com/Proximum-AI)

## **SYSTEM ARCHITECTURE V1.0**

![model](assets/ada.svg)


### Modules

- [**User Detection**](User_Detection/) - Recognizes and stores users via face recognition for personalized interactions
- [**Activator**](Activator/) - Handles wake word detection to activate the ADA system
- [**TTS**](TTS/) - Text-to-Speech module for converting responses to spoken audio
- [**User Input**](User_Input/) - Captures and processes speech input from users
- [**Vision GPT**](Vision_GPT/) - Integrates visual input with GPT-4o for image analysis and answering questions
- [**Models**](Models/) - Contains Local AI models like speech recognition models for local processing

### Other Folders
- [**Tests**](tests/) - Contains model tests, done using jupyter nookbooks
- [**Assets**](assets/) - Contains the images and diagrams for social previews

### Usefull Files
- [**Start Script**](setup_and_run.sh) - This file sets up ada downloading all models and libraries, The setup script will guide you through installation and prompt for your OpenAI API key, once all requirements are satisfied this script will automatically start ADA.
- [**Main**](main.py) - Starting point for the ADA system (running this file starts ADA only if you have all the requirments)
- [**Env file**](.env) - Contains the OpenAI api key for the model (local file)
- [**Git Ignore**](.gitignore) - Contains the files and folders too be ingored for tracking, this stops all sensitive data from being tracked for possibly uploaded to github
- [**Requirements**](requirements.txt) - contains the python requirements (libraries) for the ADA system
- [**Model Requirements**](model_requirements.py) - Handles the download of local models like vosk from the internet

### Key Features

- **User Recognition** - Identifies users through facial recognition
- **Wake Word Activation** - Activates using configurable wake words
- **Vision-based Q&A** - Answers questions about what the camera sees
- **Natural Speech Interaction** - Processes spoken questions and provides spoken responses
- **User Registration** - Adds new users to the system for future recognition
- **Session Logging** - Maintains history of interactions in current session for reference and an all time history with all interactions with ADA.
- **Real-time Visual Feedback** - Displays system status and responses on screen

### Getting Started

#### Required:
- OpenAI API key (Get one at [OpenAI Platform](https://platform.openai.com/))

#### Run the Bash script
The setup script will guide you through installation and prompt for your OpenAI API key.

From the root directory, run:
```bash
./setup_and_run.sh
```

The script will:
1. Set up a Python virtual environment
2. Install all required dependencies
3. Prompt you for your OpenAI API key
4. Launch the ADA application

> [!IMPORTANT]
> <span style="color:purple">ADA maintains a session history that records all Q&A interactions during your current session. This history is used to provide context to the model, allowing for more coherent multi-turn conversations. There is also a All time history log that includes all conversations with ADA up-to date. Additionally the User Detection module keeps images of all user faces it has regognized so far under the 'user_faces' subfolder, there is also a db that has the face encodings which are linked with the face image and aditional info. All face data, that is the face images and encodings that are used to identify the user are only stored locally and are not tracked or transmitted to anyone. Additionally all session history and all time history with the model is also kept locally and is not tracked. See the gitignore for all the files that are ingored under the (sensitive data) section for more info.</span>



#### Using ADA with Wake Words
Once ADA is running, activate it using any of these wake words:
- "Hey ADA"
- "Hey A.D.A"
- "OK ADA"
- "Hello ADA"
- "ADA"
- "Hi"

After saying a wake word, ADA will detect your presence and begin listening for your questions. You can ask questions about what the camera sees, and ADA will analyze the image and provide spoken responses. See the terminal for all logs related to the system

> [!IMPORTANT]
> <span style="color:purple">Each interaction with ADA uses your OpenAI API credits. No conversation data is transmitted except to the OpenAI API during direct requests.</span>

#### Install Python (if you don't have Python)

**macOS:**
```bash
brew install python3
```

**Windows:**
1. Download the installer from [python.org](https://www.python.org/downloads/)
2. Run the installer and make sure to check "Add Python to PATH"
3. Verify installation by opening command prompt and typing `python --version`

### Models and API's
- Vosk small, for voice recognition (see the Models folders readme for more info)
- GPT-4o: OpenAI's multimodal model that powers ADA's vision capabilities
  - **Functionality**: Processes both images and text to answer questions about visual content
  - **Capabilities**: Object recognition, text reading (OCR), scene analysis, counting, and logical reasoning
  - **Cost Estimate**: 
    - Approximately $0.01-0.05 per question (varies with image size and complexity)
    - $5-10 for ~100-500 typical interactions
    - Based on OpenAI's pricing of $5 per 1M input tokens and $15 per 1M output tokens
    - Each image counts as approximately 1,000 tokens depending on resolution

### System Requirements

- Python 3.10 or higher
- 4GB RAM minimum (8GB recommended)
- Webcam for user detection and visual analysis
- Microphone for voice input
- Internet connection for OpenAI API access
- OpenAI API key with access to GPT-4o

### License

This project is licensed under the MIT License - see the LICENSE file for details.

- [LICENCE](LICENSE)