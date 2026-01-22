import importlib.util
import os
import sys
import logging
import inspect
from app.core.base_scene import BaseScene

logger = logging.getLogger(__name__)

class ScriptLoader:
    def __init__(self, matrix, state_manager, scripts_dir="scenes/scripts"):
        self.matrix = matrix
        self.state_manager = state_manager
        self.scripts_dir = scripts_dir
        
        # Ensure directory exists
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
            logger.info(f"Created scripts directory: {self.scripts_dir}")

    def load_script(self, filename):
        """
        Loads a python script and returns an instance of the class inheriting from BaseScene.
        """
        file_path = os.path.join(self.scripts_dir, filename)
        if not os.path.exists(file_path):
            logger.error(f"Script file not found: {file_path}")
            return None

        module_name = filename.replace(".py", "")
        
        try:
            # Dynamic import
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module # optional: register in sys.modules
            spec.loader.exec_module(module)
            
            # Find the Scene class
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseScene) and obj is not BaseScene:
                    return obj # Return the Class itself
            
            logger.warning(f"No subclass of BaseScene found in {filename}")
            return None

        except Exception as e:
            logger.exception(f"Failed to load script {filename}: {e}")
            return None

    def get_scene(self, filename):
        """
        Instantiates a fresh scene object from the filename.
        """
        SceneClass = self.load_script(filename)
        if SceneClass:
            try:
                instance = SceneClass(self.matrix, self.state_manager)
                instance.filename = filename
                return instance
            except Exception as e:
                 logger.error(f"Failed to instantiate {filename}: {e}")
                 return None
        return None

    def list_available_scripts(self):
        files = [f for f in os.listdir(self.scripts_dir) if f.endswith(".py")]
        return files
