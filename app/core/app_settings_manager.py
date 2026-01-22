import logging
import threading
from app.utils.file_ops import FileOps

logger = logging.getLogger(__name__)

SETTINGS_FILE = "data/settings.json"

class AppSettingsManager:
    """
    Manages application-level settings like Home Assistant integration.
    Separate from StateManager which handles matrix display settings.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Default settings
        defaults = {
            "home_assistant": {
                "enabled": False,
                "url": "",
                "long_lived_token": ""
            }
        }
        
        # Load settings from file
        loaded = FileOps.load_json(SETTINGS_FILE, defaults)
        # Merge with defaults to ensure all keys exist
        self.settings = self._merge_settings(defaults, loaded)
        
        # Save to ensure file exists and has all defaults
        self._save()
    
    def _merge_settings(self, defaults, loaded):
        """Recursively merge loaded settings with defaults"""
        result = defaults.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_settings(self):
        """Get all settings"""
        with self._lock:
            return self.settings.copy()
    
    def get_setting(self, category, key=None):
        """Get a specific setting or category"""
        with self._lock:
            if category not in self.settings:
                logger.warning(f"Unknown settings category: {category}")
                return None
            
            if key:
                return self.settings[category].get(key)
            return self.settings[category].copy()
    
    def update_setting(self, category, key, value):
        """Update a specific setting"""
        with self._lock:
            if category not in self.settings:
                logger.warning(f"Unknown settings category: {category}")
                return False
            
            if key not in self.settings[category]:
                logger.warning(f"Unknown setting key: {category}.{key}")
                return False
            
            old_value = self.settings[category][key]
            self.settings[category][key] = value
            logger.info(f"Setting updated: {category}.{key} = {old_value} -> {value}")
            
            # Persist immediately
            return self._save()
    
    def update_category(self, category, values):
        """Update an entire category of settings"""
        with self._lock:
            if category not in self.settings:
                logger.warning(f"Unknown settings category: {category}")
                return False
            
            # Merge values into category
            self.settings[category].update(values)
            logger.info(f"Settings category updated: {category}")
            
            # Persist immediately
            return self._save()
    
    def _save(self):
        """Save settings to file"""
        try:
            FileOps.save_json(SETTINGS_FILE, self.settings)
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
