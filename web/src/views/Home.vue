<template>
  <div class="dashboard">
    <div class="status-card" v-if="status.active_scene">
      <div class="status-content">
        <div class="info-col">
          <h3>Now Playing</h3>
          <div class="status-row" v-if="status.active_playlist">
            <span class="label">Playlist:</span>
            <span class="value">{{ status.active_playlist }}</span>
          </div>
          <div class="status-row">
            <span class="label">Scene:</span>
            <span class="value">{{ status.active_scene }}</span>
          </div>
          <div class="status-row" v-if="status.selected_palette_data">
            <span class="label">Palette:</span>
            <span class="value">{{ status.selected_palette_data.name }}</span>
          </div>
          <div
            class="status-row"
            v-if="status.fps !== undefined && dashboardDisplay.showFps"
          >
            <span class="label">FPS:</span>
            <span class="value fps-value" :class="getFpsClass(status.fps)">
              {{ status.fps.toFixed(1) }}
            </span>
          </div>
          <div
            class="status-row"
            v-if="dashboardDisplay.showSystemInfo && status.version"
          >
            <span class="label">Version:</span>
            <span class="value">{{ status.version }}</span>
          </div>
        </div>
        <div class="palette-preview-col" v-if="status.selected_palette_data">
          <div class="palette-mini-preview">
            <div
              v-for="(color, idx) in status.selected_palette_data.colors"
              :key="idx"
              class="mini-swatch"
              :style="{ backgroundColor: color }"
              :title="color"
            ></div>
          </div>
        </div>
        <div class="thumb-col" v-if="status.active_scene_filename">
          <img
            :src="getThumb(status.active_scene_filename)"
            class="now-playing-thumb"
          />
        </div>
      </div>
    </div>

    <!-- Live Preview Section -->
    <div class="preview-card" v-if="dashboardDisplay.showPreview">
      <h3>Live Preview</h3>
      <div class="preview-container">
        <img
          :src="previewUrl"
          class="preview-image"
          @error="handlePreviewError"
          alt="Matrix Display Preview"
        />
      </div>
    </div>

    <!-- System Performance Section -->
    <div class="status-card" v-if="dashboardDisplay.showSystemInfo && systemStats">
      <h3>System Performance</h3>
      <div class="stats-grid">
        <div class="stat-item" v-if="dashboardDisplay.showCpuUsage">
          <span class="stat-label">CPU Usage</span>
          <span class="stat-value" :class="getStatClass(systemStats.cpu_percent, 80, 90)">
            {{ systemStats.cpu_percent }}%
          </span>
        </div>
        <div class="stat-item" v-if="dashboardDisplay.showRamUsage">
          <span class="stat-label">RAM Usage</span>
          <span class="stat-value" :class="getStatClass(systemStats.ram_percent, 80, 90)">
            {{ systemStats.ram_percent }}% ({{ systemStats.ram_used_mb }} / {{ systemStats.ram_total_mb }} MB)
          </span>
        </div>
        <div class="stat-item" v-if="dashboardDisplay.showCpuTemp && systemStats.cpu_temp !== null">
          <span class="stat-label">CPU Temp</span>
          <span class="stat-value" :class="getTempClass(systemStats.cpu_temp)">
            {{ systemStats.cpu_temp }}°C
          </span>
        </div>
      </div>
    </div>
    
    <SystemControls :settings="settings" @update="updateSettings" />
  </div>
</template>

<script>
import api from "../services/api";
import SystemControls from "../components/SystemControls.vue";

export default {
  name: "Home",
  components: {
    SystemControls,
  },
  data() {
    return {
      settings: { brightness: 100, speed: 1.0 },
      status: {
        active_scene: null,
        active_playlist: null,
        selected_palette: null,
        selected_palette_data: null,
      },
      pollInterval: null,
      previewInterval: null,
      previewUrl: api.getPreviewUrl(),
      dashboardDisplay: {
        showFps: true,
        showSystemInfo: true,
        showCpuUsage: true,
        showRamUsage: true,
        showCpuTemp: true,
        showPreview: true,
        refreshInterval: 2000,
      },
      systemStats: null,
    };
  },
  async mounted() {
    this.loadDashboardDisplay();
    await this.refresh();
    this.pollInterval = setInterval(
      this.refresh,
      this.dashboardDisplay.refreshInterval,
    );
    // Update preview with same interval as status
    this.previewInterval = setInterval(() => {
      this.previewUrl = api.getPreviewUrl();
    }, this.dashboardDisplay.refreshInterval);

    // Listen for settings changes
    window.addEventListener(
      "dashboardDisplayChanged",
      this.handleDisplaySettingsChange,
    );
  },
  beforeUnmount() {
    clearInterval(this.pollInterval);
    if (this.previewInterval) {
      clearInterval(this.previewInterval);
    }
    window.removeEventListener(
      "dashboardDisplayChanged",
      this.handleDisplaySettingsChange,
    );
  },
  methods: {
    getThumb(filename) {
      return api.getThumbnailUrl(filename);
    },
    handlePreviewError(event) {
      // If preview fails, try to reload after a short delay
      console.warn("Preview image failed to load, retrying...");
      setTimeout(() => {
        this.previewUrl = api.getPreviewUrl();
      }, 500);
    },
    async refresh() {
      try {
        const statusRes = await api.getSystemStatus();
        this.settings = statusRes.data;
        this.status = statusRes.data;
        
        // Fetch system stats if enabled
        if (this.dashboardDisplay.showSystemInfo) {
          const statsRes = await api.getSystemStats();
          this.systemStats = statsRes.data;
        }
      } catch (e) {
        console.error("Failed to fetch data", e);
      }
    },
    async updateSettings(newSettings) {
      try {
        this.settings = newSettings;
        await api.updateSettings(newSettings);
      } catch (e) {
        console.error("Failed to update settings", e);
      }
    },
    getFpsClass(fps) {
      if (fps >= 25) return "fps-good";
      if (fps >= 20) return "fps-warning";
      return "fps-poor";
    },
    loadDashboardDisplay() {
      const saved = localStorage.getItem("dashboardDisplay");
      if (saved) {
        this.dashboardDisplay = JSON.parse(saved);
      }
    },
    handleDisplaySettingsChange(event) {
      this.dashboardDisplay = event.detail;
      // Update refresh interval for status
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
        this.pollInterval = setInterval(
          this.refresh,
          this.dashboardDisplay.refreshInterval,
        );
      }
      // Update refresh interval for preview
      if (this.previewInterval) {
        clearInterval(this.previewInterval);
        this.previewInterval = setInterval(() => {
          this.previewUrl = api.getPreviewUrl();
        }, this.dashboardDisplay.refreshInterval);
      }
    },
    getStatClass(value, warning, critical) {
      if (value >= critical) return 'fps-poor';
      if (value >= warning) return 'fps-warning';
      return 'fps-good';
    },
    getTempClass(temp) {
      if (temp >= 80) return 'fps-poor';
      if (temp >= 70) return 'fps-warning';
      return 'fps-good';
    },
  },
};
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.status-card {
  background: #2a2a2a;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #444;
}

.status-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.thumb-col img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #555;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
}

.status-card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #42b883;
}

.status-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
  gap: 2rem; /* Add some spacing between label and value */
}

.label {
  color: #888;
}

.value {
  font-weight: bold;
  color: #fff;
}

.preview-card {
  background: #2a2a2a;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #444;
}

.preview-card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #42b883;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #1a1a1a;
  border-radius: 4px;
  padding: 1rem;
  border: 2px solid #444;
}

.preview-image {
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.palette-preview-col {
  display: flex;
  align-items: center;
}

.palette-mini-preview {
  display: flex;
  gap: 2px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #555;
  height: 40px;
}

.mini-swatch {
  width: 20px;
  min-width: 20px;
  height: 100%;
}

.fps-value {
  transition: color 0.3s ease;
}

.fps-good {
  color: #42b883 !important;
}

.fps-warning {
  color: #f39c12 !important;
}

.fps-poor {
  color: #e74c3c !important;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: #1a1a1a;
  border-radius: 4px;
  border: 1px solid #444;
}

.stat-label {
  color: #888;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: bold;
  transition: color 0.3s ease;
}
</style>
