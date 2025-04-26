#!/usr/bin/env python3

import os
import requests
from tqdm import tqdm
import zipfile
import tarfile

# Fix the models directory path to point to the Models folder
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Models")

MODEL_URLS = {
    "vosk-model-small-en-us-0.15": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
}

def download_file(url, destination):
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destination, 'wb') as f, tqdm(
        desc=os.path.basename(destination),
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)
    
    return destination

def extract_archive(archive_path, extract_dir):
    """Extract ZIP or TAR archives"""
    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    elif archive_path.endswith(('.tar.gz', '.tgz')):
        with tarfile.open(archive_path, 'r:gz') as tar_ref:
            tar_ref.extractall(extract_dir)
    
    # Remove the archive after extraction
    os.remove(archive_path)

def download_models():
    """Download all models if they don't exist"""
    # Ensure the Models directory exists
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    for model_name, url in MODEL_URLS.items():
        # For direct files (like .gguf)
        if url.endswith(('.gguf', '.bin', '.pt')):
            target_path = os.path.join(MODELS_DIR, os.path.basename(url))
            if not os.path.exists(target_path):
                print(f"Downloading {model_name}...")
                download_file(url, target_path)
                print(f"Downloaded {model_name} to {target_path}")
            else:
                print(f"{model_name} already exists at {target_path}")
        
        # For archives (like .zip)
        elif url.endswith(('.zip', '.tar.gz', '.tgz')):
            model_dir = os.path.join(MODELS_DIR, model_name)
            if not os.path.exists(model_dir):
                print(f"Downloading and extracting {model_name}...")
                archive_path = os.path.join(MODELS_DIR, os.path.basename(url))
                download_file(url, archive_path)
                extract_archive(archive_path, MODELS_DIR)
                print(f"Extracted {model_name} to {model_dir}")
            else:
                print(f"{model_name} already exists at {model_dir}")

if __name__ == "__main__":
    print("ADA Model Downloader")
    print("====================")
    download_models()
    print("All models downloaded successfully!")