from app.core.base_scene import BaseScene
import math
import json
import os
import time
import urllib.request
import urllib.error
import logging

logger = logging.getLogger(__name__)


class TemperatureDisplay(BaseScene):
    """
    Displays outdoor temperature from Home Assistant sensor.
    Shows temperature with animated background and smooth updates.
    """
    
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        
        # Sensor entity ID
        self.sensor_id = "sensor.node_2_input_7_2_2"
        
        # Current temperature value
        self.temperature = None
        self.unit = "°C"
        self.last_fetch_time = 0
        self.fetch_interval = 30.0  # Fetch every 30 seconds
        self.fetch_error = None
        
        # Animation
        self.time = 0.0
        self.pulse_phase = 0.0
        
        # Home Assistant settings
        self.ha_url = None
        self.ha_token = None
        self.ha_enabled = False
        
        # Load HA settings
        self._load_ha_settings()
        
        # Try initial fetch
        self._fetch_temperature()
    
    def _load_ha_settings(self):
        """Load Home Assistant settings from settings file"""
        try:
            settings_path = "data/settings.json"
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    ha_settings = settings.get("home_assistant", {})
                    self.ha_enabled = ha_settings.get("enabled", False)
                    self.ha_url = ha_settings.get("url", "").strip().rstrip("/")
                    self.ha_token = ha_settings.get("long_lived_token", "").strip()
        except Exception as e:
            logger.error(f"Failed to load HA settings: {e}")
            self.ha_enabled = False
    
    def _fetch_temperature(self):
        """Fetch temperature from Home Assistant"""
        if not self.ha_enabled or not self.ha_url or not self.ha_token:
            self.fetch_error = "HA not configured"
            return
        
        try:
            # Build API URL
            api_url = f"{self.ha_url}/api/states/{self.sensor_id}"
            
            # Create request
            req = urllib.request.Request(api_url)
            req.add_header("Authorization", f"Bearer {self.ha_token}")
            req.add_header("Content-Type", "application/json")
            
            # Fetch with timeout
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                # Extract temperature
                state = data.get("state", "unknown")
                attributes = data.get("attributes", {})
                
                try:
                    self.temperature = float(state)
                    self.unit = attributes.get("unit_of_measurement", "°C")
                    self.fetch_error = None
                except (ValueError, TypeError):
                    self.fetch_error = "Invalid data"
                    logger.warning(f"Invalid temperature state: {state}")
        
        except urllib.error.HTTPError as e:
            if e.code == 401:
                self.fetch_error = "Auth failed"
            elif e.code == 404:
                self.fetch_error = "Sensor not found"
            else:
                self.fetch_error = f"HTTP {e.code}"
            logger.error(f"HA API error: {e}")
        
        except urllib.error.URLError as e:
            self.fetch_error = "Connection error"
            logger.error(f"HA connection error: {e}")
        
        except Exception as e:
            self.fetch_error = "Fetch error"
            logger.error(f"Error fetching temperature: {e}")
    
    def update(self, dt):
        self.time += dt
        self.pulse_phase += dt * 2.0  # Slow pulse animation
        
        # Fetch temperature periodically
        current_time = time.time()
        if current_time - self.last_fetch_time >= self.fetch_interval:
            self._fetch_temperature()
            self.last_fetch_time = current_time
    
    def _draw_digit(self, canvas, digit, x, y, size, r, g, b):
        """Draw a single digit using a simple 7-segment style"""
        # Simple 5x7 digit patterns (0-9)
        patterns = {
            '0': [0b11111, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11111],
            '1': [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
            '2': [0b11111, 0b00001, 0b00001, 0b11111, 0b10000, 0b10000, 0b11111],
            '3': [0b11111, 0b00001, 0b00001, 0b11111, 0b00001, 0b00001, 0b11111],
            '4': [0b10001, 0b10001, 0b10001, 0b11111, 0b00001, 0b00001, 0b00001],
            '5': [0b11111, 0b10000, 0b10000, 0b11111, 0b00001, 0b00001, 0b11111],
            '6': [0b11111, 0b10000, 0b10000, 0b11111, 0b10001, 0b10001, 0b11111],
            '7': [0b11111, 0b00001, 0b00001, 0b00001, 0b00001, 0b00001, 0b00001],
            '8': [0b11111, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b11111],
            '9': [0b11111, 0b10001, 0b10001, 0b11111, 0b00001, 0b00001, 0b11111],
            '.': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100],
            '-': [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
        }
        
        pattern = patterns.get(digit, [0] * 7)
        digit_width = 5
        digit_height = 7
        
        for row in range(digit_height):
            for col in range(digit_width):
                if pattern[row] & (1 << (digit_width - 1 - col)):
                    px = x + col * size
                    py = y + row * size
                    if 0 <= px < self.width and 0 <= py < self.height:
                        canvas.SetPixel(px, py, r, g, b)
    
    def _draw_text(self, canvas, text, x, y, size, r, g, b):
        """Draw text using digit drawing"""
        char_width = 6 * size
        current_x = x
        
        for char in text:
            if char == ' ':
                current_x += char_width // 2
            else:
                self._draw_digit(canvas, char, current_x, y, size, r, g, b)
                current_x += char_width
    
    def draw(self, canvas):
        # Animated gradient background
        pulse = (math.sin(self.pulse_phase) * 0.3 + 0.7)  # Pulse between 0.4 and 1.0
        
        for y in range(self.height):
            for x in range(self.width):
                # Create a subtle gradient from center
                dx = x - self.width / 2
                dy = y - self.height / 2
                dist = math.sqrt(dx*dx + dy*dy) / (self.width / 2)
                
                # Blue-purple gradient background
                r = int(10 * (1 - dist * 0.5) * pulse)
                g = int(20 * (1 - dist * 0.5) * pulse)
                b = int(40 * (1 - dist * 0.5) * pulse)
                
                canvas.SetPixel(x, y, r, g, b)
        
        # Draw temperature or error message
        if self.temperature is not None:
            # Format temperature (round to 1 decimal)
            temp_str = f"{self.temperature:.1f}"
            
            # Color based on temperature (cold = blue, warm = red)
            if self.temperature < 10:
                # Cold - blue/cyan
                r, g, b = 50, 150, 255
            elif self.temperature < 20:
                # Cool - green/cyan
                r, g, b = 100, 200, 255
            elif self.temperature < 25:
                # Mild - yellow
                r, g, b = 255, 200, 50
            else:
                # Warm - orange/red
                r, g, b = 255, 100, 50
            
            # Apply pulse to color
            r = int(r * pulse)
            g = int(g * pulse)
            b = int(b * pulse)
            
            # Draw temperature (size 1 for 5x7 digits)
            # Center the text
            text_width = len(temp_str) * 6
            start_x = (self.width - text_width) // 2
            start_y = (self.height - 7) // 2 - 5
            
            self._draw_text(canvas, temp_str, start_x, start_y, 1, r, g, b)
            
            # Draw unit below temperature
            unit_y = start_y + 10
            unit_x = (self.width - 6) // 2
            self._draw_text(canvas, self.unit, unit_x, unit_y, 1, 
                          int(r * 0.7), int(g * 0.7), int(b * 0.7))
        
        elif self.fetch_error:
            # Draw error message
            error_text = "ERR"
            text_width = len(error_text) * 6
            start_x = (self.width - text_width) // 2
            start_y = (self.height - 7) // 2
            
            # Red error color
            self._draw_text(canvas, error_text, start_x, start_y, 1, 255, 50, 50)
        
        else:
            # Loading state
            loading_text = "---"
            text_width = len(loading_text) * 6
            start_x = (self.width - text_width) // 2
            start_y = (self.height - 7) // 2
            
            # Gray loading color
            gray = int(100 * pulse)
            self._draw_text(canvas, loading_text, start_x, start_y, 1, gray, gray, gray)
