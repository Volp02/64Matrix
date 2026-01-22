import json
import os
import logging
from app.utils.file_ops import FileOps

logger = logging.getLogger(__name__)

class LibraryManager:
    def __init__(self, data_file="data/library.json"):
        self.data_file = data_file
        self.library = self._load()
        self.ensure_thumbnails_dir()

    def _load(self):
        if not os.path.exists(self.data_file):
            return {}
        return FileOps.load_json(self.data_file) or {}

    def _save(self):
        FileOps.save_json(self.data_file, self.library)

    def ensure_thumbnails_dir(self):
         path = os.path.join("scenes", "thumbnails")
         if not os.path.exists(path):
             os.makedirs(path)

    def get_metadata(self, filename):
        return self.library.get(filename, {})

    def update_metadata(self, filename, **kwargs):
        if filename not in self.library:
            self.library[filename] = {}
        
        for k, v in kwargs.items():
            self.library[filename][k] = v
            
        self._save()
        return self.library[filename]

    def rename_entry(self, old_filename, new_filename):
        """
        Updates the key in the library.json from old_filename to new_filename.
        Preserves existing metadata.
        """
        if old_filename in self.library:
            self.library[new_filename] = self.library.pop(old_filename)
            self._save()
            return True
        return False
        
    def delete_entry(self, filename):
        if filename in self.library:
            del self.library[filename]
            self._save()
            return True
        return False
