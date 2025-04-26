"""
Module for handling LLM context for computer vision tasks.
This module receives questions from the main ADA system, processes them with an LLM,
and generates context for CV analysis rather than answering directly.
"""

import logging
import os
import time
import tempfile
import threading
from gtts import gTTS
from pygame import mixer
from llama_cpp import Llama

# Set up logging
logger = logging.getLogger(__name__)

# Global LLM model instance
llm = None

def initialize_llm():
    """
    Initialize the LLM model.
    Only initializes once, subsequent calls return the existing model.
    """
    global llm
    if llm is None:
        try:
            # Model path - using the same direct path as in notebook for consistency
            model_path = "../Models/tinyllama-1.1b-chat-v1.0.Q8_0.gguf"
            
            # Check if the model exists at the specified path
            if not os.path.exists(model_path):
                # Try an alternative path calculation
                alt_model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                         "Models/tinyllama-1.1b-chat-v1.0.Q8_0.gguf")
                
                if os.path.exists(alt_model_path):
                    model_path = alt_model_path
                    logger.info(f"Found model at alternative path: {model_path}")
                else:
                    logger.error(f"Model file not found at: {model_path} or {alt_model_path}")
                    # Print current working directory to help with debugging
                    logger.error(f"Current working directory: {os.getcwd()}")
                    return None
                
            logger.info(f"Loading LLM model from: {model_path}")
            
            # Load the model with the same parameters as in the notebook
            llm = Llama(
                model_path=model_path,
                n_ctx=512,         # Small context window for faster inference
                n_threads=4,       # Adjust based on your CPU cores
                n_batch=32,        # Lower batch size for faster inference
                f16_kv=True,       # Use half-precision for key/value cache
                use_mlock=True,    # Keep model in RAM
                verbose=False,
                n_gpu_layers=-1    # Use GPU acceleration if available
            )
            logger.info("LLM model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM model: {e}")
            # Print more detailed error information
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    return llm

def generate_cv_context(question: str) -> str:
    """
    Process a user question through the LLM and generate a CV-focused context question.
    
    Args:
        question: The user's original question as a string
        
    Returns:
        A CV-focused question/context as a string
    """
    model = initialize_llm()
    if not model:
        return "Error accessing vision system"
    
    try:
        # Format the question as a prompt that directs the LLM to generate CV context
        prompt = f"""
User has asked: "{question}"

Convert this into a computer vision analysis question. Don't answer the question directly.
Instead, generate a single, concise instruction for a computer vision system to analyze
the current video frame. Focus on what visual elements the CV system should look for.

Example conversions:
- "How old am I?" → "Determine the approximate age of the person in the frame"
- "What am I wearing?" → "Identify the clothing items worn by the person in the frame"
- "Is there anyone else here?" → "Detect and count the number of people in the frame"

Computer vision instruction:
"""
        
        # Process with LLM
        logger.info(f"Generating CV context for question: {question}")
        output = model(
            prompt,
            max_tokens=100,     # Limit response length for faster processing
            stop=["Example:"],  # Stop at any follow-up examples
            echo=False          # Don't include the prompt in the output
        )
        
        cv_context = output["choices"][0]["text"].strip()
        logger.info(f"Generated CV context: {cv_context}")
        
        # If the output is empty or too short, provide a fallback
        if not cv_context or len(cv_context) < 5:
            cv_context = f"Analyze the visual elements in the frame related to: {question}"
            logger.warning(f"Using fallback CV context: {cv_context}")
        
        return cv_context
    except Exception as e:
        logger.error(f"Error generating CV context: {e}")
        return f"Analyze the frame for information about: {question}"

def play_response_async(response: str) -> None:
    """
    Convert the text response to speech and play it asynchronously.
    
    Args:
        response: The text response to speak
    """
    try:
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_filename = temp_file.name
        
        # Generate the speech audio
        tts = gTTS(text=response, lang="en", slow=False)
        tts.save(temp_filename)
        logger.info("Speech generated for LLM response")
        
        # Initialize the mixer if not already initialized
        if not mixer.get_init():
            mixer.init()
        
        mixer.music.load(temp_filename)
        mixer.music.play()
        
        # Wait for the audio to finish playing
        while mixer.music.get_busy():
            time.sleep(0.1)
        
        # Clean up the temporary file
        os.unlink(temp_filename)
        logger.info("Response playback complete")
    except Exception as e:
        logger.error(f"Error playing response: {e}")

def log_user_question(question: str) -> str:
    """
    Process a user question and generate CV context instead of a direct answer.
    Logs the original question and generated CV context.
    
    Args:
        question: The user's question as a string
        
    Returns:
        str: The generated CV context
    """
    try:
        # Create log directory inside the LLM_CV_Context folder if it doesn't exist
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate CV context instead of answering directly
        cv_context = generate_cv_context(question)
        
        # Log both original question and CV context
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        log_file = os.path.join(log_dir, f"llm_cv_context.log")
        
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] Original question: {question}\n")
            f.write(f"[{timestamp}] Generated CV context: {cv_context}\n\n")
        
        logger.info(f"Generated CV context for question: {question}")
        
        # Skip directly to returning the CV context without verbal notification
        
        # Return the CV context for use by the main system
        return cv_context
        
    except Exception as e:
        logger.error(f"Failed to generate CV context: {e}")
        return "Error analyzing visual information"
