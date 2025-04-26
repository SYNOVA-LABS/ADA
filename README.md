![model](assets/adalogo.png)

# ADA (Advanced Digital Agent)

ADA is a modular, extensible personal assistant system that combines face recognition, contextual understanding, and natural language processing to provide a personalized interactive experience.

## **SYSTEM ARCHITECTURE V1.0**

![model](assets/ada.svg)


### Modules

- [**User Detection**](User_Detection/) - Recognizes users via face recognition for personalized interactions
- [**Activator**](Activator/) - Central control system managing ADA's activation states and module coordination
- [**Greet User**](Greet_User/) - Provides personalized audio greetings using text-to-speech technology
- [**CV Context**](CV_Context/) - Analyzes visual environment to provide contextual awareness
- [**LLM CV Context Questions**](LLM_CV_Context_Questions/) - Generates intelligent questions about visual scenes
- [**User Input**](User_Input/) - Captures and processes various forms of user input
- [**Vision GPT**](Vision_GPT/) - Integrates visual input with language understanding for image analysis and questions
- [**Models**](Models/) - Contains language and speech models used by the system

### Key Features

- **User Recognition** - Identifies users through computer vision
- **Contextual Understanding** - Interprets visual environment and user context
- **Natural Interaction** - Responds to voice commands and generates natural speech
- **Modular Design** - Extensible architecture allowing for new capabilities
- **Privacy-Focused** - Processes data locally when possible
- **Visual Analysis** - Answers questions about visual content in real-time

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

After saying a wake word, ADA will detect your presence and begin listening for your commands.

#### Install Python (if you don't have Python)

**macOS:**
```bash
brew install python3
```

**Windows:**
1. Download the installer from [python.org](https://www.python.org/downloads/)
2. Run the installer and make sure to check "Add Python to PATH"
3. Verify installation by opening command prompt and typing `python --version`

### System Requirements

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- Webcam for user detection
- Microphone for voice input
- Internet connection for OpenAI API access

### Future Development

- Enhanced CV contextual understanding
- Multi-user simultaneous interaction
- Expanded domain knowledge
- Integration with home automation systems
- Mobile companion application

### Contributing

Contributions are welcome! Please check the CONTRIBUTING.md file for guidelines.

### License

This project is licensed under the MIT License - see the LICENSE file for details.
[LICENCE](LICENSE)
