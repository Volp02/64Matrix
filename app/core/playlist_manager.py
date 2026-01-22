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
