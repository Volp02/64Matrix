import time
import logging
import threading
import io
from collections import deque
from PIL import Image

logger = logging.getLogger(__name__)

class Engine:
    def __init__(self, matrix_driver, state_manager):
        self.matrix = matrix_driver
        self.state_manager = state_manager
        self._running = False
        self._target_fps = 60  # Target 60 FPS for smoother animations
        self._frame_duration = 1.0 / self._target_fps
        
        # Preview frame capture
        self._preview_lock = threading.Lock()
        self._latest_preview_frame = None  # PNG bytes
        self._last_capture_time = 0
        self._preview_capture_interval = 0.2  # Capture every 200ms (5 FPS)
        
        # FPS monitoring - use deque for O(1) append/pop performance
        self._frame_times = deque(maxlen=120)  # Track ~2 seconds at 60 FPS
        self._fps_window = 2.0  # Calculate FPS over 2 second window
        self._last_fps_log = 0  # Last time we logged FPS warning
        self._fps_log_interval = 5.0  # Only log FPS warnings every 5 seconds
        self._current_fps = 0.0  # Current calculated FPS

    def start(self):
        """Starts the render loop in the current thread (blocking) or separate thread."""
        self._running = True
        logger.info("Engine started.")
        self._loop()

    def stop(self):
        self._running = False
        logger.info("Engine stopping...")

    def _loop(self):
        last_time = time.time()
        error_count = 0
        max_consecutive_errors = 10
        
        while self._running:
            try:
                current_time = time.time()
                dt = current_time - last_time
                # Cap delta time to prevent huge jumps (e.g., system sleep)
                dt = min(dt, 1.0)
                last_time = current_time
                
                # 1. Get Settings & Active Scene
                try:
                    settings = self.state_manager.get_settings()
                    scene = self.state_manager.active_scene
                except Exception as e:
                    logger.error(f"Error getting state: {e}")
                    time.sleep(0.1)
                    continue
                
                # Speed Multiplier
                # If speed is 2.0, passed dt should be 2x real time?
                # Or we limit the sleep? Usually, dt passed to update is scaled.
                speed = settings.get("speed", 1.0)
                # Validate speed range
                speed = max(0.1, min(2.0, speed))
                scaled_dt = dt * speed
                
                if scene:
                    try:
                        # 2. Update Logic
                        scene.update(scaled_dt)
                        
                        # 3. Render
                        # Clear canvas (optional, depends on scene optimization)
                        self.matrix.clear() 
                        
                        scene.draw(self.matrix.canvas)
                        
                        # 4. Capture preview frame BEFORE swap (capture what we just drew)
                        self._maybe_capture_preview()
                        
                        # 5. Swap Hardware Buffers
                        self.matrix.swap_canvas()
                        
                        # Reset error count on successful frame
                        error_count = 0
                        
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error in render loop (frame {error_count}/{max_consecutive_errors}): {e}", exc_info=True)
                        
                        # If too many consecutive errors, clear scene to prevent infinite loop
                        if error_count >= max_consecutive_errors:
                            logger.critical(f"Too many consecutive errors ({error_count}). Clearing active scene.")
                            try:
                                self.state_manager.set_scene(None)
                            except:
                                pass
                            error_count = 0
                        
                        # Prevent tight loop spamming errors
                        time.sleep(0.1)
                else:
                    # No scene active, clear screen or show logo?
                    try:
                        self.matrix.clear()
                        self.matrix.swap_canvas()
                    except Exception as e:
                        logger.error(f"Error clearing matrix: {e}")
                    time.sleep(0.1)

                # 5. Timing / Frame Cap
                elapsed = time.time() - current_time
                sleep_time = self._frame_duration - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                # 6. FPS Monitoring
                self._update_fps_tracking(current_time)
                    
            except KeyboardInterrupt:
                logger.info("Engine loop interrupted by user")
                break
            except Exception as e:
                logger.critical(f"Critical error in engine loop: {e}", exc_info=True)
                # Prevent complete crash, but log heavily
                time.sleep(1)

    def _maybe_capture_preview(self):
        """Capture a preview frame if enough time has passed since last capture."""
        current_time = time.time()
        if current_time - self._last_capture_time >= self._preview_capture_interval:
            try:
                # Capture frame from matrix
                img = self.matrix.capture_frame()
                if img:
                    # Convert to PNG bytes
                    buffer = io.BytesIO()
                    # Scale up for better visibility (e.g., 4x = 256x256)
                    scaled = img.resize((img.width * 4, img.height * 4), Image.Resampling.NEAREST)
                    scaled.save(buffer, format='PNG')
                    png_bytes = buffer.getvalue()
                    
                    # Store latest frame (thread-safe)
                    with self._preview_lock:
                        self._latest_preview_frame = png_bytes
                    
                    self._last_capture_time = current_time
            except Exception as e:
                logger.debug(f"Failed to capture preview frame: {e}")
    
    def _update_fps_tracking(self, current_time):
        """Track frame times and calculate FPS, logging warnings if performance is poor."""
        # Add current frame time - deque automatically drops old entries when full
        self._frame_times.append(current_time)
        
        # Remove old frame times outside the window (deque makes this efficient)
        cutoff_time = current_time - self._fps_window
        while self._frame_times and self._frame_times[0] < cutoff_time:
            self._frame_times.popleft()
        
        # Calculate FPS (number of frames in the window / window duration)
        if len(self._frame_times) > 1:
            time_span = self._frame_times[-1] - self._frame_times[0]
            if time_span > 0:
                self._current_fps = (len(self._frame_times) - 1) / time_span
                
                # Log warning if FPS is below 40 (adjusted for 60 FPS target)
                if self._current_fps < 40.0:
                    if current_time - self._last_fps_log >= self._fps_log_interval:
                        logger.warning(
                            f"⚠️  Low FPS detected: {self._current_fps:.1f} FPS "
                            f"(target: {self._target_fps} FPS). "
                            f"Check system load and performance optimizations."
                        )
                        self._last_fps_log = current_time
    
    def get_current_fps(self):
        """Get the current calculated FPS."""
        return self._current_fps
    
    def get_preview_frame(self):
        """
        Get the latest captured preview frame as PNG bytes.
        Returns bytes or None if no frame available.
        """
        with self._preview_lock:
            return self._latest_preview_frame
    
    def run_threaded(self):
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        return thread
