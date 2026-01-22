import json
import os
import logging

logger = logging.getLogger(__name__)

class FileOps:
    @staticmethod
    def load_json(filepath, default=None):
        if not os.path.exists(filepath):
            logger.info(f"File not found: {filepath}, returning default.")
            return default or {}
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {filepath}: {e}")
            return default or {}

    @staticmethod
    def save_json(filepath, data):
        # Ensure directory exists
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Saved data to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save {filepath}: {e}")
