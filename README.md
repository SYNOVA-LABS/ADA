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
- [**Models**](Models/) - Contains language and speech models used by the system

### Key Features

- **User Recognition** - Identifies users through computer vision
- **Contextual Understanding** - Interprets visual environment and user context
- **Natural Interaction** - Responds to voice commands and generates natural speech
- **Modular Design** - Extensible architecture allowing for new capabilities
- **Privacy-Focused** - Processes data locally when possible

### Getting Started

#### Run the Bash script (this will download eveything you need and run the program)
#### In you terminal from the root dir enter the command 
```**bash**
./setup_and_run.sh 
```


#### Install Python (if you dont have python)

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
- Internet connection for certain LLM capabilities

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
