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
        <div class="stat-item glass-panel" v-if="dashboardDisplay.showCpuUsage">
          <div class="stat-header">
            <span class="stat-label">CPU Usage</span>
            <span class="stat-value-text">{{ systemStats.cpu_percent }}%</span>
          </div>
          <div class="progress-bar-container">
            <div 
              class="progress-bar" 
              :style="{ width: `${systemStats.cpu_percent}%` }"
              :class="getStatClass(systemStats.cpu_percent, 80, 90)"
            ></div>
          </div>
        </div>
        <div class="stat-item glass-panel" v-if="dashboardDisplay.showRamUsage">
          <div class="stat-header">
            <span class="stat-label">RAM Usage</span>
            <span class="stat-value-text">{{ systemStats.ram_percent }}%</span>
          </div>
          <div class="progress-bar-container">
            <div 
              class="progress-bar" 
              :style="{ width: `${systemStats.ram_percent}%` }"
              :class="getStatClass(systemStats.ram_percent, 80, 90)"
            ></div>
          </div>
          <div class="stat-detail">
            {{ systemStats.ram_used_mb }} / {{ systemStats.ram_total_mb }} MB
          </div>
        </div>
        <div class="stat-item glass-panel" v-if="dashboardDisplay.showCpuTemp && systemStats.cpu_temp !== null">
          <div class="stat-header">
            <span class="stat-label">CPU Temp</span>
            <span class="stat-value-text" :class="getTempClass(systemStats.cpu_temp)">
              {{ systemStats.cpu_temp }}°C
            </span>
          </div>
          <div class="temp-indicator">
            <div 
              class="temp-bar" 
              :style="{ width: `${Math.min(systemStats.cpu_temp, 100)}%` }"
              :class="getTempClass(systemStats.cpu_temp)"
            ></div>
          </div>
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

.status-card, .preview-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 1.5rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.status-card:hover, .preview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.15);
}

.status-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.thumb-col img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.status-card h3, .preview-card h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #42b883;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.status-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.8rem;
  font-size: 1.05rem;
  gap: 2rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.status-row:last-child {
  border-bottom: none;
}

.label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.95rem;
}

.value {
  font-weight: 600;
  color: #fff;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.preview-image {
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.palette-preview-col {
  display: flex;
  align-items: center;
}

.palette-mini-preview {
  display: flex;
  gap: 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
  height: 48px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.mini-swatch {
  width: 24px;
  min-width: 24px;
  height: 100%;
}

.fps-value {
  transition: color 0.3s ease;
  font-family: monospace;
  font-weight: 700;
}

.fps-good {
  color: #42b883 !important;
  background-color: #42b883 !important; /* For progress bars */
}

.fps-warning {
  color: #f39c12 !important;
  background-color: #f39c12 !important;
}

.fps-poor {
  color: #e74c3c !important;
  background-color: #e74c3c !important;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.glass-panel {
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

.stat-value-text {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
}

.progress-bar-container {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.3s ease;
}

.temp-indicator {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  margin-top: 0.2rem;
  overflow: hidden;
}

.temp-bar {
  height: 100%;
  transition: width 0.5s ease, background-color 0.3s ease;
}

.stat-detail {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.4);
  text-align: right;
  margin-top: -0.4rem;
}
</style>
