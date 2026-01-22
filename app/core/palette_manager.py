import json
import os
import logging
from app.utils.file_ops import FileOps

logger = logging.getLogger(__name__)

DATA_FILE = "data/palettes.json"

# Default color palettes (8 vibrant, harmonious palettes)
DEFAULT_PALETTES = {
    "aurora": {
        "id": "aurora",
        "name": "Aurora",
        "colors": ["#172347", "#025385", "#0EF3C5", "#04E2B7", "#038298", "#015268"]
    },
    "sunset": {
        "id": "sunset",
        "name": "Sunset",
        "colors": ["#FF6B6B", "#FF8E53", "#FFA07A", "#FFB347", "#FFD700", "#FF6347"]
    },
    "ocean": {
        "id": "ocean",
        "name": "Ocean",
        "colors": ["#001F3F", "#0074D9", "#39CCCC", "#7FDBFF", "#B3E5FC", "#E0F7FA"]
    },
    "forest": {
        "id": "forest",
        "name": "Forest",
        "colors": ["#1B4332", "#2D6A4F", "#40916C", "#52B788", "#74C69D", "#95D5B2"]
    },
    "neon": {
        "id": "neon",
        "name": "Neon",
        "colors": ["#FF00FF", "#00FFFF", "#FF00AA", "#AA00FF", "#00FFAA", "#FFAA00"]
    },
    "fire": {
        "id": "fire",
        "name": "Fire",
        "colors": ["#8B0000", "#DC143C", "#FF4500", "#FF6347", "#FF8C00", "#FFA500"]
    },
    "ice": {
        "id": "ice",
        "name": "Ice",
        "colors": ["#000080", "#0000CD", "#4169E1", "#87CEEB", "#B0E0E6", "#E0F6FF"]
    },
    "autumn": {
        "id": "autumn",
        "name": "Autumn",
        "colors": ["#8B4513", "#A0522D", "#CD853F", "#DEB887", "#F4A460", "#FFD700"]
    }
}

class PaletteManager:
    def __init__(self):
        self.custom_palettes = {}
        self.load_palettes()

    def load_palettes(self):
        """Load custom palettes from disk."""
        self.custom_palettes = FileOps.load_json(DATA_FILE, {})
        logger.info(f"Loaded {len(self.custom_palettes)} custom palettes")

    def save_palettes(self):
        """Save custom palettes to disk."""
        try:
            FileOps.save_json(DATA_FILE, self.custom_palettes)
        except Exception as e:
            logger.error(f"Failed to save palettes: {e}")

    def get_default_palettes(self):
        """Get all default (hardcoded) palettes."""
        return DEFAULT_PALETTES

    def get_custom_palettes(self):
        """Get all custom (user-created) palettes."""
        return self.custom_palettes

    def get_all_palettes(self):
        """Get both default and custom palettes."""
        return {
            "default": DEFAULT_PALETTES,
            "custom": self.custom_palettes
        }

    def get_palette(self, palette_id):
        """Get a specific palette (checks both default and custom)."""
        if palette_id in DEFAULT_PALETTES:
            return DEFAULT_PALETTES[palette_id]
        return self.custom_palettes.get(palette_id)

    def save_palette(self, palette_id, data):
        """Create or update a custom palette."""
        # Ensure ID in data matches
        data["id"] = palette_id
        if "name" not in data:
            data["name"] = palette_id
        if "colors" not in data:
            data["colors"] = []
        
        # Validate colors format
        if not isinstance(data["colors"], list):
            raise ValueError("Colors must be a list")
        
        # Validate color format (should be hex strings)
        for color in data["colors"]:
            if not isinstance(color, str) or not color.startswith("#"):
                raise ValueError(f"Invalid color format: {color}. Colors must be hex strings (e.g., #FF0000)")
        
        self.custom_palettes[palette_id] = data
        self.save_palettes()
        return data

    def delete_palette(self, palette_id):
        """Delete a custom palette (cannot delete default palettes)."""
        if palette_id in DEFAULT_PALETTES:
            raise ValueError("Cannot delete default palettes")
        
        if palette_id in self.custom_palettes:
            del self.custom_palettes[palette_id]
            self.save_palettes()
            return True
        return False
