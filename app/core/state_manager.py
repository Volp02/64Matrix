import threading
import logging
import os
from app.utils.file_ops import FileOps

logger = logging.getLogger(__name__)

CONFIG_PATH = "data/config.json"

class StateManager:
    def __init__(self):
        self._lock = threading.Lock()
        
        # Load Global Settings
        defaults = {
            "brightness": 100,  # 0-100
            "speed": 1.0,       # Multiplier
            "selected_palette": "aurora"  # Default color palette ID
        }
        loaded = FileOps.load_json(CONFIG_PATH, defaults)
        # Merge loaded with defaults to ensure all keys exist
        self.global_settings = {**defaults, **loaded}
        
        # Core State
        self.active_scene = None  # The current Scene instance
        
        # External Data Store (Shared dictionary for integrations)
        self.external_data = {}
        
    def get_settings(self):
        with self._lock:
            return self.global_settings.copy()
            
    def update_setting(self, key, value):
        with self._lock:
            if key not in self.global_settings:
                logger.warning(f"Attempted to update unknown setting: {key}")
                return False
            
            # Validate value ranges
            if key == "brightness":
                value = max(0, min(100, int(value)))
            elif key == "speed":
                value = max(0.1, min(2.0, float(value)))
            
            # Update value
            old_value = self.global_settings[key]
            self.global_settings[key] = value
            logger.info(f"Setting updated: {key} = {old_value} -> {value}")
            
            # Persist immediately (or could be debounced)
            # For now, immediate save is fine for low frequency updates
            try:
                FileOps.save_json(CONFIG_PATH, self.global_settings)
            except Exception as e:
                logger.error(f"Failed to persist settings: {e}")
                return False
            
            return True

    def get_data(self, key=None):
        with self._lock:
            if key:
                return self.external_data.get(key)
            return self.external_data.copy()

    def set_data(self, key, value):
        with self._lock:
            self.external_data[key] = value
            logger.debug(f"External Data updated: {key} = {value}")

    def set_scene(self, scene_instance):
        with self._lock:
            if self.active_scene:
                # Optional: Call an exit/cleanup method on the old scene if it exists
                if hasattr(self.active_scene, "exit"):
                    try:
                        self.active_scene.exit()
                    except Exception as e:
                        logger.error(f"Error exiting previous scene: {e}")
            
            self.active_scene = scene_instance
            
            # Optional: Call an enter/setup method on the new scene
            if hasattr(self.active_scene, "enter"):
                try:
                    self.active_scene.enter(self) # Pass self (StateManager) context if needed
                except Exception as e:
                    logger.error(f"Error entering new scene: {e}")
                    
            logger.info(f"Active scene set to: {scene_instance}")

    def get_active_scene(self):
        # Determine if we need to lock here. 
        # Ideally, we return a reference. If the engine uses it, we hope it doesn't get swapped OUT from under it mid-frame.
        # However, Python variable assignment is atomic.
        return self.active_scene
    
    def get_palette_colors(self, palette_manager=None):
        """
        Get colors from the selected palette.
        Returns a list of RGB tuples [(r, g, b), ...] or None if palette not found.
        """
        with self._lock:
            palette_id = self.global_settings.get("selected_palette", "aurora")
        
        if palette_manager:
            palette = palette_manager.get_palette(palette_id)
            if palette and "colors" in palette:
                # Convert hex colors to RGB tuples
                colors = []
                for hex_color in palette["colors"]:
                    try:
                        # Remove # if present
                        hex_color = hex_color.lstrip("#")
                        # Convert to RGB
                        r = int(hex_color[0:2], 16)
                        g = int(hex_color[2:4], 16)
                        b = int(hex_color[4:6], 16)
                        colors.append((r, g, b))
                    except (ValueError, IndexError):
                        logger.warning(f"Invalid color format in palette: {hex_color}")
                        continue
                return colors if colors else None
        
        return None

