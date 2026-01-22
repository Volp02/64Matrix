import time
import logging
import threading

logger = logging.getLogger(__name__)

class Engine:
    def __init__(self, matrix_driver, state_manager):
        self.matrix = matrix_driver
        self.state_manager = state_manager
        self._running = False
        self._target_fps = 30
        self._frame_duration = 1.0 / self._target_fps

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
                        
                        # 4. Swap Hardware Buffers
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
                    
            except KeyboardInterrupt:
                logger.info("Engine loop interrupted by user")
                break
            except Exception as e:
                logger.critical(f"Critical error in engine loop: {e}", exc_info=True)
                # Prevent complete crash, but log heavily
                time.sleep(1)

    def run_threaded(self):
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        return thread
