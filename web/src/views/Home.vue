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
        </div>
        <div class="thumb-col" v-if="status.active_scene_filename">
          <img
            :src="getThumb(status.active_scene_filename)"
            class="now-playing-thumb"
          />
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
      status: { active_scene: null, active_playlist: null },
      pollInterval: null,
    };
  },
  async mounted() {
    await this.refresh();
    this.pollInterval = setInterval(this.refresh, 2000);
  },
  beforeUnmount() {
    clearInterval(this.pollInterval);
  },
  methods: {
    getThumb(filename) {
      return api.getThumbnailUrl(filename);
    },
    async refresh() {
      try {
        const statusRes = await api.getSystemStatus();
        this.settings = statusRes.data;
        this.status = statusRes.data;
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
</style>
