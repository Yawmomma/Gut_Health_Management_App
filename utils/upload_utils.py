# Upload utilities for Gut Health Management App

import os
import json
import tempfile


def get_temp_upload_dir(subdir='uploads'):
    """Get or create temporary upload directory"""
    temp_dir = os.path.join(tempfile.gettempdir(), f'gut_health_{subdir}')
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def save_upload_data(data, upload_id, subdir='uploads'):
    """Save upload data to temporary file"""
    temp_dir = get_temp_upload_dir(subdir)
    file_path = os.path.join(temp_dir, f"{upload_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    return file_path


def load_upload_data(upload_id, subdir='uploads'):
    """Load upload data from temporary file"""
    temp_dir = get_temp_upload_dir(subdir)
    file_path = os.path.join(temp_dir, f"{upload_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def delete_upload_data(upload_id, subdir='uploads'):
    """Delete temporary upload data file"""
    temp_dir = get_temp_upload_dir(subdir)
    file_path = os.path.join(temp_dir, f"{upload_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
