import json
import os
import logging
from app.utils.file_ops import FileOps

logger = logging.getLogger(__name__)

DATA_FILE = "data/playlists.json"

class PlaylistManager:
    def __init__(self):
        self.playlists = {}
        self.load_playlists()

    def load_playlists(self):
        """Load playlists from disk."""
        self.playlists = FileOps.load_json(DATA_FILE, {})
        logger.info(f"Loaded {len(self.playlists)} playlists")

    def save_playlists(self):
        """Save playlists to disk."""
        try:
            FileOps.save_json(DATA_FILE, self.playlists)
        except Exception as e:
            logger.error(f"Failed to save playlists: {e}")

    def get_all(self):
        return self.playlists

    def get_by_id(self, playlist_id):
        return self.playlists.get(playlist_id)

    def save_playlist(self, playlist_id, data):
        """Create or Update a playlist."""
        # Ensure ID in data matches
        data["id"] = playlist_id
        if "name" not in data:
            data["name"] = playlist_id
        if "items" not in data:
            data["items"] = []
            
        self.playlists[playlist_id] = data
        self.save_playlists()
        return data

    def delete_playlist(self, playlist_id):
        if playlist_id in self.playlists:
            del self.playlists[playlist_id]
            self.save_playlists()
            return True
        return False
    
    def update_scene_filename(self, old_filename, new_filename):
        """
        Update all playlist items that reference old_filename to use new_filename.
        Returns the number of playlists updated.
        """
        updated_count = 0
        for playlist_id, playlist_data in self.playlists.items():
            items = playlist_data.get("items", [])
            updated = False
            for item in items:
                if item.get("filename") == old_filename:
                    item["filename"] = new_filename
                    updated = True
            if updated:
                updated_count += 1
                logger.info(f"Updated playlist '{playlist_id}' to reference {new_filename} instead of {old_filename}")
        
        if updated_count > 0:
            self.save_playlists()
        
        return updated_count
