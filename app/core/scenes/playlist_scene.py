from app.core.base_scene import BaseScene
import logging
import time

logger = logging.getLogger(__name__)

class PlaylistScene(BaseScene):
    def __init__(self, matrix, state_manager, playlist_data, script_loader, clip_loader):
        super().__init__(matrix, state_manager)
        self.playlist_data = playlist_data
        self.script_loader = script_loader
        self.clip_loader = clip_loader
        self.items = playlist_data.get("items", [])
        
        self.current_index = -1
        self.current_scene_instance = None
        self.time_in_scene = 0
        self.current_item_duration = 0
        
        # Start the first item
        self.advance_scene()

    def advance_scene(self):
        if not self.items:
            self.current_scene_instance = None
            return

        # Advance index (looping)
        self.current_index = (self.current_index + 1) % len(self.items)
        item = self.items[self.current_index]
        
        filename = item.get("filename")
        item_type = item.get("type", "script")  # Default to script for backward compatibility
        self.current_item_duration = item.get("duration", 10) # Default 10s
        
        logger.info(f"Playlist advancing to: {filename} (type: {item_type}) for {self.current_item_duration}s")
        
        # Load the Scene based on type
        scene_instance = None
        
        try:
            if item_type == "clip":
                if self.clip_loader:
                    scene_instance = self.clip_loader.load_clip(filename)
                else:
                    logger.error("Clip loader not available")
            else:  # Default to script
                if self.script_loader:
                    scene_instance = self.script_loader.get_scene(filename)
                else:
                    logger.error("Script loader not available")
        except Exception as e:
            logger.error(f"Error loading scene {filename} (type: {item_type}): {e}")
        
        if scene_instance:
            # Lifecycle: Exit old
            if self.current_scene_instance and hasattr(self.current_scene_instance, 'exit'):
                try:
                    self.current_scene_instance.exit()
                except Exception as e:
                    logger.error(f"Error exit sub-scene: {e}")

            self.current_scene_instance = scene_instance
            
            # Lifecycle: Enter new
            if hasattr(self.current_scene_instance, 'enter'):
                try:
                    self.current_scene_instance.enter(self.state_manager)
                except Exception as e:
                    logger.error(f"Error enter sub-scene: {e}")
                    
            # Reset Timer
            self.time_in_scene = 0
        else:
            logger.error(f"Playlist could not load scene: {filename} (type: {item_type})")
            # Failsafe: Try next one immediately to avoid black screen hang
            # But prevent infinite recursion if ALL are bad
            # We'll just wait 1 sec then try again to be safe
            self.current_scene_instance = None
            self.current_item_duration = 1.0 

    def update(self, dt):
        # 1. Update Timer
        self.time_in_scene += dt
        
        # 2. Check for switch
        if self.time_in_scene >= self.current_item_duration:
            self.advance_scene()
            
        # 3. Update Sub-Scene
        if self.current_scene_instance:
            try:
                self.current_scene_instance.update(dt)
            except Exception as e:
                logger.error(f"Error updating sub-scene: {e}")

    def draw(self, canvas):
        if self.current_scene_instance:
            try:
                self.current_scene_instance.draw(canvas)
            except Exception as e:
                logger.error(f"Error drawing sub-scene: {e}")
