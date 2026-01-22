import os
import logging
from PIL import Image, ImageSequence
from app.core.base_scene import BaseScene

logger = logging.getLogger(__name__)

class GifScene(BaseScene):
    def __init__(self, matrix, state_manager, filepath):
        super().__init__(matrix, state_manager)
        self.filepath = filepath
        self.frames = []
        self.frame_durations = [] # in seconds
        self.total_duration = 0
        self.current_frame_index = 0
        self.elapsed_time = 0
        self.loaded = False
        
        self._load_gif()

    def _load_gif(self):
        try:
            with Image.open(self.filepath) as im:
                # Resize if necessary? handling scaling is complex, let's assume 64x64 or stretch
                # For best quality, assume user provides correct size or center it.
                # Let's simple resize to matrix size for now.
                
                for frame in ImageSequence.Iterator(im):
                    # Convert to RGB
                    frame = frame.convert('RGB')
                    frame = frame.resize((self.width, self.height), Image.Resampling.NEAREST)
                    
                    self.frames.append(frame)
                    
                    # Duration
                    duration = frame.info.get('duration', 100) # ms
                    duration_sec = duration / 1000.0
                    self.frame_durations.append(duration_sec)
                    self.total_duration += duration_sec
                
                self.loaded = True
                logger.info(f"Loaded GIF {os.path.basename(self.filepath)} with {len(self.frames)} frames.")
        except Exception as e:
            logger.error(f"Failed to load GIF {self.filepath}: {e}")

    def update(self, dt):
        if not self.loaded or not self.frames:
            return

        self.elapsed_time += dt
        
        # Advance frame
        current_duration = self.frame_durations[self.current_frame_index]
        
        if self.elapsed_time >= current_duration:
            self.elapsed_time -= current_duration
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)

    def draw(self, canvas):
        if not self.loaded or not self.frames:
            return
            
        img = self.frames[self.current_frame_index]
        canvas.SetImage(img)


class ClipLoader:
    def __init__(self, matrix, state_manager, clips_dir="scenes/clips"):
        self.matrix = matrix
        self.state_manager = state_manager
        self.clips_dir = clips_dir
        
        if not os.path.exists(self.clips_dir):
            os.makedirs(self.clips_dir)

    def list_available_clips(self):
        # Scan for supported extensions
        exts = ['.gif']
        files = [f for f in os.listdir(self.clips_dir) if any(f.lower().endswith(ext) for ext in exts)]
        return files

    def load_clip(self, filename):
        filepath = os.path.join(self.clips_dir, filename)
        if not os.path.exists(filepath):
            return None
            
        if filename.lower().endswith('.gif'):
            return GifScene(self.matrix, self.state_manager, filepath)
            
        return None
