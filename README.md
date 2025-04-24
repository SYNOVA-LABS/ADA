# ADA (Advanced Digital Agent)

## **MODEL ARCETECTURE V1.0**

![model](assets/ada.svg)

### Models

- [User_Recognition](User_Detection/) (this model is used to regognized the current user for a personalized experience)

### Getting Started

#### 1. Install Python

**macOS:**
```bash
brew install python3
```

**Windows:**
1. Download the installer from [python.org](https://www.python.org/downloads/)
2. Run the installer and make sure to check "Add Python to PATH"
3. Verify installation by opening command prompt and typing `python --version`

#### 2. Create and Activate Virtual Environment (Recommended)

**macOS:**
```bash
# Create virtual environment
python3 -m venv venv_name

# Activate virtual environment
source venv_name/bin/activate
```

**Windows:**
```bash
# Create virtual environment
python -m venv venv_name

# Activate virtual environment
venv_name\Scripts\activate
```

#### 3. Install Requirements

```bash
pip install -r requirements.txt
```

#### 4. Run the User Detection System

```bash
# Navigate to the User_Detection directory
cd User_Detection

# Run the face detection script
python3 detect_user_by_face.py
```

#### More features coming soon!
