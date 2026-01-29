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
                # 1. Determine target size
                target_size = (self.width, self.height)
                
                # 2. Iterate frames with persistent canvas for correct disposal/transparency
                # Some optimized GIFs store only the changed pixels on a transparent background
                # We interpret this by compositing onto a persistent canvas
                
                # Start with a black background or transparent? 
                # For matrix, black (0,0,0) is usually best base.
                canvas = Image.new('RGBA', im.size, (0, 0, 0, 0))
                
                for frame in ImageSequence.Iterator(im):
                    # Handle Frame Disposal (Simplification: most modern GIFs usually work with simple over-composite)
                    # Ideally we'd respect 'disposal' method from frame.info, but 
                    # standard compositing works for 95% of 'optimized' GIFs.
                    
                    # Composite this frame onto persistent canvas
                    # frame.convert('RGBA') ensures we handle transparency mask in frame
                    frame_rgba = frame.convert('RGBA')
                    
                    # Paste current frame over canvas
                    # If frame has transparency, it will show canvas underneath
                    # Note: We create a NEW image for the step to avoid mutating previous frames in the list
                    # if we were strictly following disposal logic, but here "canvas" tracks the state.
                    
                    # For simple "replace" vs "combine" disposal, proper logic is hard.
                    # But Python's ImageSequence usually gives us the delta frame.
                    # The robust way:
                    # 1. Create copy of current canvas
                    # 2. Paste new frame on top
                    # 3. Use that as new canvas AND as the frame to append
                    
                    canvas.paste(frame_rgba, (0, 0), frame_rgba)
                    
                    # Now we have the full frame image in 'canvas'
                    
                    # 3. Resize High Quality
                    # We must copy() because resize returns a new image, and we want to keep 'canvas' 
                    # at original resolution for next frame composition
                    final_frame = canvas.resize(target_size, Image.Resampling.LANCZOS)
                    
                    # 4. Convert to RGB (Matrix doesn't use Alpha)
                    # Create black background to flatten alpha
                    bg = Image.new('RGB', target_size, (0, 0, 0))
                    bg.paste(final_frame, (0, 0), final_frame)
                    
                    self.frames.append(bg)
                    
                    # Duration
                    duration = frame.info.get('duration', 100) # ms
                    # Handle invalid 0 duration
                    if duration == 0: duration = 100
                    
                    duration_sec = duration / 1000.0
                    self.frame_durations.append(duration_sec)
                    self.total_duration += duration_sec
                
                self.loaded = True
                logger.info(f"Loaded GIF {os.path.basename(self.filepath)} with {len(self.frames)} frames using High-Quality render.")
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
            scene = GifScene(self.matrix, self.state_manager, filepath)
            # Important: used by status UI + thumbnails lookup
            scene.filename = filename
            return scene
            
        return None
