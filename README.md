![model](assets/adalogo.png)

# ADA (Advanced Digital Agent)

ADA is a modular, extensible personal assistant system that combines face recognition, contextual understanding, and natural language processing to provide a personalized interactive experience.

## **SYSTEM ARCHITECTURE V1.0**

![model](assets/ada.svg)


### Modules

- [**User Detection**](User_Detection/) - Recognizes users via face recognition for personalized interactions
- [**Activator**](Activator/) - Handles wake word detection to activate the ADA system
- [**TTS**](TTS/) - Text-to-Speech module for converting responses to spoken audio
- [**User Input**](User_Input/) - Captures and processes speech input from users
- [**Vision GPT**](Vision_GPT/) - Integrates visual input with GPT-4o for image analysis and answering questions
- [**Models**](Models/) - Contains speech recognition models for local processing

### Key Features

- **User Recognition** - Identifies users through facial recognition
- **Wake Word Activation** - Activates using configurable wake words
- **Vision-based Q&A** - Answers questions about what the camera sees
- **Natural Speech Interaction** - Processes spoken questions and provides spoken responses
- **User Registration** - Adds new users to the system for future recognition
- **Session Logging** - Maintains history of interactions for reference
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

#### Using ADA with Wake Words
Once ADA is running, activate it using any of these wake words:
- "Hey ADA"
- "Hey A.D.A"
- "OK ADA"
- "Hello ADA"
- "ADA"
- "Hi"

After saying a wake word, ADA will detect your presence and begin listening for your questions. You can ask questions about what the camera sees, and ADA will analyze the image and provide spoken responses.

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
[LICENCE](LICENSE)
