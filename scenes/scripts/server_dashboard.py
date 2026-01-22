from app.core.base_scene import BaseScene
import math
import json
import os
import time
import urllib.request
import urllib.error
import logging

logger = logging.getLogger(__name__)


class ServerDashboard(BaseScene):
    """
    Dashboard displaying server statistics from Home Assistant.
    Cycles through different metrics with animated bars and charts.
    """
    
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        
        # Sensor definitions
        self.sensors = [
            {
                "id": "sensor.ibeb_proxmox_glance_cpu_usage",
                "name": "CPU",
                "unit": "%",
                "max_value": 100,
                "color": (100, 200, 255),  # Cyan
                "warn_threshold": 70,
                "critical_threshold": 90
            },
            {
                "id": "sensor.sp07_server_power",
                "name": "POWER",
                "unit": "W",
                "max_value": 500,  # Adjust based on your server
                "color": (255, 200, 100),  # Orange
                "warn_threshold": 400,
                "critical_threshold": 450
            },
            {
                "id": "sensor.ibeb_proxmox_glance_package_id_0_temperature",
                "name": "TEMP",
                "unit": "°C",
                "max_value": 100,
                "color": (255, 100, 100),  # Red
                "warn_threshold": 70,
                "critical_threshold": 85
            },
            {
                "id": "sensor.qemu_services_101_memory_used_percentage",
                "name": "MEM",
                "unit": "%",
                "max_value": 100,
                "color": (100, 255, 150),  # Green
                "warn_threshold": 80,
                "critical_threshold": 90
            },
            {
                "id": "sensor.node_pve_disk_used_percentage",
                "name": "DISK",
                "unit": "%",
                "max_value": 100,
                "color": (200, 150, 255),  # Purple
                "warn_threshold": 80,
                "critical_threshold": 90
            }
        ]
        
        # Current slide index
        self.current_slide = 0
        self.slide_timer = 0.0
        self.slide_duration = 5.0  # Show each metric for 5 seconds
        
        # Transition animation
        self.transition_progress = 0.0
        self.is_transitioning = False
        
        # Sensor data storage
        self.sensor_data = {}  # {sensor_id: {"value": float, "unit": str, "timestamp": float}}
        self.last_fetch_time = {}
        self.fetch_interval = 10.0  # Fetch every 10 seconds
        
        # Animation
        self.time = 0.0
        self.pulse_phase = 0.0
        
        # Home Assistant settings
        self.ha_url = None
        self.ha_token = None
        self.ha_enabled = False
        
        # Load HA settings
        self._load_ha_settings()
        
        # Initial fetch for all sensors
        for sensor in self.sensors:
            self._fetch_sensor(sensor["id"])
    
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
    
    def _fetch_sensor(self, sensor_id):
        """Fetch sensor value from Home Assistant"""
        if not self.ha_enabled or not self.ha_url or not self.ha_token:
            return
        
        try:
            api_url = f"{self.ha_url}/api/states/{sensor_id}"
            req = urllib.request.Request(api_url)
            req.add_header("Authorization", f"Bearer {self.ha_token}")
            req.add_header("Content-Type", "application/json")
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                state = data.get("state", "unknown")
                attributes = data.get("attributes", {})
                
                try:
                    value = float(state)
                    unit = attributes.get("unit_of_measurement", "")
                    self.sensor_data[sensor_id] = {
                        "value": value,
                        "unit": unit,
                        "timestamp": time.time()
                    }
                except (ValueError, TypeError):
                    logger.warning(f"Invalid sensor state for {sensor_id}: {state}")
        
        except Exception as e:
            logger.error(f"Error fetching sensor {sensor_id}: {e}")
    
    def update(self, dt):
        self.time += dt
        self.pulse_phase += dt * 1.5
        
        # Update slide timer
        self.slide_timer += dt
        
        # Handle transitions
        if self.is_transitioning:
            self.transition_progress += dt * 3.0  # Fast transition
            if self.transition_progress >= 1.0:
                self.transition_progress = 1.0
                self.is_transitioning = False
                self.current_slide = (self.current_slide + 1) % len(self.sensors)
                self.slide_timer = 0.0
        elif self.slide_timer >= self.slide_duration:
            # Start transition to next slide
            self.is_transitioning = True
            self.transition_progress = 0.0
        
        # Fetch sensor data periodically
        current_time = time.time()
        for sensor in self.sensors:
            sensor_id = sensor["id"]
            last_fetch = self.last_fetch_time.get(sensor_id, 0)
            if current_time - last_fetch >= self.fetch_interval:
                self._fetch_sensor(sensor_id)
                self.last_fetch_time[sensor_id] = current_time
    
    def _draw_bar(self, canvas, x, y, width, height, value, max_value, color, warn_threshold, critical_threshold):
        """Draw an animated bar chart"""
        # Calculate fill percentage
        fill_ratio = min(1.0, max(0.0, value / max_value))
        
        # Color based on thresholds
        r, g, b = color
        if value >= critical_threshold:
            # Critical - red
            r, g, b = 255, 50, 50
        elif value >= warn_threshold:
            # Warning - yellow/orange
            r, g, b = 255, 200, 50
        
        # Animated fill with pulse
        pulse = (math.sin(self.pulse_phase * 2) * 0.1 + 0.9)
        fill_height = int(height * fill_ratio * pulse)
        
        # Draw bar background (dark)
        for bar_y in range(y, y + height):
            for bar_x in range(x, x + width):
                if 0 <= bar_x < self.width and 0 <= bar_y < self.height:
                    canvas.SetPixel(bar_x, bar_y, 20, 20, 30)
        
        # Draw filled portion
        for bar_y in range(y + height - fill_height, y + height):
            for bar_x in range(x, x + width):
                if 0 <= bar_x < self.width and 0 <= bar_y < self.height:
                    # Gradient effect
                    rel_y = (bar_y - (y + height - fill_height)) / max(1, fill_height)
                    bright_r = int(r * (0.7 + 0.3 * rel_y))
                    bright_g = int(g * (0.7 + 0.3 * rel_y))
                    bright_b = int(b * (0.7 + 0.3 * rel_y))
                    canvas.SetPixel(bar_x, bar_y, bright_r, bright_g, bright_b)
        
        # Draw border
        for bar_x in range(x, x + width):
            if 0 <= bar_x < self.width:
                if 0 <= y < self.height:
                    canvas.SetPixel(bar_x, y, 100, 100, 120)
                if 0 <= y + height - 1 < self.height:
                    canvas.SetPixel(bar_x, y + height - 1, 100, 100, 120)
        for bar_y in range(y, y + height):
            if 0 <= bar_y < self.height:
                if 0 <= x < self.width:
                    canvas.SetPixel(x, bar_y, 100, 100, 120)
                if 0 <= x + width - 1 < self.width:
                    canvas.SetPixel(x + width - 1, bar_y, 100, 100, 120)
    
    def _draw_text_small(self, canvas, text, x, y, r, g, b):
        """Draw small text (3x5 font)"""
        # Simple 3x5 font patterns
        font = {
            '0': [0b111, 0b101, 0b101, 0b101, 0b111],
            '1': [0b010, 0b110, 0b010, 0b010, 0b111],
            '2': [0b111, 0b001, 0b111, 0b100, 0b111],
            '3': [0b111, 0b001, 0b111, 0b001, 0b111],
            '4': [0b101, 0b101, 0b111, 0b001, 0b001],
            '5': [0b111, 0b100, 0b111, 0b001, 0b111],
            '6': [0b111, 0b100, 0b111, 0b101, 0b111],
            '7': [0b111, 0b001, 0b001, 0b001, 0b001],
            '8': [0b111, 0b101, 0b111, 0b101, 0b111],
            '9': [0b111, 0b101, 0b111, 0b001, 0b111],
            '.': [0b000, 0b000, 0b000, 0b000, 0b010],
            '%': [0b101, 0b001, 0b010, 0b100, 0b101],
            'W': [0b101, 0b101, 0b101, 0b101, 0b111],
            '°': [0b010, 0b101, 0b010, 0b000, 0b000],
            'C': [0b111, 0b100, 0b100, 0b100, 0b111],
            ' ': [0b000, 0b000, 0b000, 0b000, 0b000],
        }
        
        char_width = 4
        current_x = x
        
        for char in text:
            pattern = font.get(char.upper(), [0] * 5)
            for row in range(5):
                for col in range(3):
                    if pattern[row] & (1 << (2 - col)):
                        px = current_x + col
                        py = y + row
                        if 0 <= px < self.width and 0 <= py < self.height:
                            canvas.SetPixel(px, py, r, g, b)
            current_x += char_width
    
    def draw(self, canvas):
        # Dark background
        canvas.Fill(5, 5, 15)
        
        # Get current sensor
        sensor = self.sensors[self.current_slide]
        sensor_id = sensor["id"]
        data = self.sensor_data.get(sensor_id)
        
        # Transition effect
        if self.is_transitioning:
            # Fade out current, fade in next
            alpha = 1.0 - abs(self.transition_progress - 0.5) * 2.0
        else:
            alpha = 1.0
        
        # Draw title (sensor name) - larger and more prominent
        title_y = 1
        title_text = sensor["name"]
        title_x = (self.width - len(title_text) * 4) // 2
        title_r, title_g, title_b = sensor["color"]
        self._draw_text_small(canvas, title_text, title_x, title_y, 
                             int(title_r * alpha), int(title_g * alpha), int(title_b * alpha))
        
        if data:
            value = data["value"]
            unit = sensor["unit"]
            
            # Draw value text (larger, more prominent)
            value_str = f"{value:.1f}"
            value_y = 8
            value_x = (self.width - len(value_str) * 4) // 2
            value_r, value_g, value_b = sensor["color"]
            self._draw_text_small(canvas, value_str, value_x, value_y,
                                int(value_r * alpha), int(value_g * alpha), int(value_b * alpha))
            
            # Draw unit next to value
            unit_x = value_x + len(value_str) * 4 + 2
            unit_y = value_y
            self._draw_text_small(canvas, unit, unit_x, unit_y,
                                int(value_r * 0.7 * alpha), int(value_g * 0.7 * alpha), int(value_b * 0.7 * alpha))
            
            # Draw bar chart - adjusted to fit better
            bar_x = 6
            bar_y = 16
            bar_width = self.width - 12
            bar_height = 38  # Reduced to fit everything
            
            self._draw_bar(canvas, bar_x, bar_y, bar_width, bar_height,
                          value, sensor["max_value"], sensor["color"],
                          sensor["warn_threshold"], sensor["critical_threshold"])
            
            # Draw max value label at top right of bar
            max_str = f"{sensor['max_value']}"
            max_x = bar_x + bar_width - len(max_str) * 4
            max_y = bar_y - 6
            self._draw_text_small(canvas, max_str, max_x, max_y, 100, 100, 120)
            
            # Draw min value label at bottom left of bar (0)
            min_str = "0"
            min_x = bar_x
            min_y = bar_y + bar_height + 1
            self._draw_text_small(canvas, min_str, min_x, min_y, 100, 100, 120)
            
            # Draw percentage indicator at bottom right
            percentage = (value / sensor["max_value"]) * 100
            pct_str = f"{percentage:.0f}%"
            pct_x = bar_x + bar_width - len(pct_str) * 4
            pct_y = bar_y + bar_height + 1
            self._draw_text_small(canvas, pct_str, pct_x, pct_y, 180, 180, 200)
        else:
            # Loading state
            loading_text = "LOADING"
            loading_x = (self.width - len(loading_text) * 4) // 2
            loading_y = self.height // 2
            gray = int(100 * (math.sin(self.pulse_phase) * 0.3 + 0.7))
            self._draw_text_small(canvas, loading_text, loading_x, loading_y, gray, gray, gray)
        
        # Draw slide indicator (dots at bottom) - moved up to ensure visibility
        dot_size = 2
        dot_spacing = 4
        total_width = len(self.sensors) * dot_spacing
        start_x = (self.width - total_width) // 2
        dot_y = self.height - 3  # Moved up slightly
        
        for i in range(len(self.sensors)):
            dot_x = start_x + i * dot_spacing
            if i == self.current_slide:
                # Active dot - bright
                for dy in range(dot_size):
                    for dx in range(dot_size):
                        px = dot_x + dx
                        py = dot_y + dy
                        if 0 <= px < self.width and 0 <= py < self.height:
                            canvas.SetPixel(px, py, 200, 200, 255)
            else:
                # Inactive dot - dim
                for dy in range(dot_size):
                    for dx in range(dot_size):
                        px = dot_x + dx
                        py = dot_y + dy
                        if 0 <= px < self.width and 0 <= py < self.height:
                            canvas.SetPixel(px, py, 50, 50, 60)
