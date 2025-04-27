"""
Module for processing user questions with visual context using GPT-4 Vision API.
This module takes both an image and a question, processes them together,
and returns a direct answer that includes visual understanding and reasoning.
"""

import os
import base64
import logging
import requests
import time
from typing import Dict, Any
import cv2
import io
from PIL import Image
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment variables")

# Define log directory
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
# Session history file path (now in the same logs folder)
SESSION_HISTORY_PATH = os.path.join(LOG_DIR, "session_history.log")

def encode_image_to_base64(image_array):
    """Convert a numpy array (OpenCV image) to base64 string."""
    # Convert from BGR (OpenCV) to RGB (PIL)
    image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    # Convert to PIL Image
    pil_image = Image.fromarray(image_rgb)
    # Create a byte buffer
    buffer = io.BytesIO()
    # Save image to buffer in JPEG format
    pil_image.save(buffer, format="JPEG")
    # Get the byte data and encode to base64
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str

def get_session_history():
    """
    Read the current session history to provide as context.
    
    Returns:
        str: The session history as a string, or empty string if not available
    """
    try:
        if os.path.exists(SESSION_HISTORY_PATH):
            with open(SESSION_HISTORY_PATH, 'r') as f:
                # Skip the header lines (first 3 lines)
                lines = f.readlines()
                if len(lines) > 3:
                    return ''.join(lines[3:])
        return ""
    except Exception as e:
        logger.error(f"Error reading session history: {e}")
        return ""

def process_with_vision_api(frame, question: str) -> Dict[str, Any]:
    """
    Process an image and question using OpenAI's GPT-4 Vision API.
    
    Args:
        frame: The current video frame as a numpy array
        question: The user's question as a string
        
    Returns:
        Dict containing the response, including the answer text
    """
    if not OPENAI_API_KEY:
        return {"error": "API key not configured", "answer": "Sorry, I'm not properly configured to analyze images."}
    
    try:
        # Encode the image to base64
        base64_image = encode_image_to_base64(frame)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        # Get session history for context
        session_history = get_session_history()
        
        # Create a detailed system prompt that explains capabilities and includes session history
        system_prompt = """
        You are an advanced vision assistant that can:
        1. Read and interpret text in images (OCR)
        2. Count objects and perform calculations
        3. Identify people, clothing, and objects
        4. Analyze scenes and describe environments
        5. Perform logical reasoning about visual information
        
        Provide direct, concise answers based on what you see in the image.
        If you cannot determine something with confidence, acknowledge that limitation.
        """
        
        # Add session history to system prompt if available
        if session_history:
            system_prompt += "\n\nHere is the conversation history from this session that you can use for context:\n" + session_history
            logger.info("Session history included in the prompt.")
        
        payload = {
            "model": "gpt-4o",  # Updated to use gpt-4o which supports vision capabilities
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        # Log attempt to connect to API (without sensitive data)
        logger.info(f"Sending request to OpenAI Vision API using model: {payload['model']}")
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code != 200:
            logger.error(f"API error: {response_data}")
            
            # Check for specific error types and provide more helpful messages
            if "error" in response_data:
                error_message = response_data["error"].get("message", "")
                if "model_not_found" in response_data["error"].get("code", ""):
                    return {"error": "Model not found", "answer": "Sorry, there was an issue with the vision processing service. The current model is unavailable."}
                elif "billing" in error_message.lower() or "quota" in error_message.lower():
                    return {"error": "Billing issue", "answer": "Sorry, the vision service is currently unavailable due to account limits."}
            
            return {"error": "API error", "answer": "Sorry, I encountered an error while analyzing the image."}
        
        # Extract the answer text from the response
        answer = response_data["choices"][0]["message"]["content"]
        
        # Log successful processing
        logger.info(f"Successfully processed question: {question}")
        
        return {"success": True, "answer": answer, "full_response": response_data}
        
    except Exception as e:
        logger.error(f"Error processing with vision API: {e}")
        return {"error": str(e), "answer": "Sorry, I couldn't process the image due to a technical error."}

def analyze_image_with_question(frame, question: str) -> str:
    """
    Main entry point for the Vision GPT module. Processes a frame and question together.
    
    Args:
        frame: The current video frame to analyze
        question: The user's question as a string
        
    Returns:
        A string response answering the user's question based on image analysis
    """
    try:
        logger.info(f"Processing question with image: {question}")
        
        # Log directory for storing analysis details
        log_dir = LOG_DIR
        os.makedirs(log_dir, exist_ok=True)
        
        # Log the received question and timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        log_file = os.path.join(log_dir, f"vision_gpt_analysis_history.log")
        
        # Process the image and question
        result = process_with_vision_api(frame, question)
        
        # Get the answer from the result
        answer = result.get("answer", "I couldn't analyze the image properly.")
        
        # Log the processing details
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] Question: {question}\n")
            f.write(f"[{timestamp}] Answer: {answer}\n\n")
        
        return answer
        
    except Exception as e:
        logger.error(f"Error in analyze_image_with_question: {e}")
        return "Sorry, I encountered an error while analyzing the image."
