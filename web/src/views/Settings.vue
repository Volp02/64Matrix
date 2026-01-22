<template>
  <div class="settings">
    <h2>Settings</h2>

    <div class="settings-container">
      <!-- Home Assistant Section -->
      <div class="settings-section">
        <h3>Home Assistant Integration</h3>
        <p class="section-description">
          Connect your matrix to Home Assistant for live data and automation.
        </p>

        <div class="setting-group">
          <label class="setting-label">
            <input
              type="checkbox"
              v-model="homeAssistant.enabled"
              @change="saveHomeAssistant"
            />
            <span>Enable Home Assistant Integration</span>
          </label>
        </div>

        <div v-if="homeAssistant.enabled" class="setting-group">
          <label class="setting-label">
            <span>Home Assistant URL</span>
            <input
              type="text"
              v-model="homeAssistant.url"
              @blur="saveHomeAssistant"
              placeholder="http://homeassistant.local:8123"
            />
          </label>
        </div>

        <div v-if="homeAssistant.enabled" class="setting-group">
          <label class="setting-label">
            <span>Long Lived Token</span>
            <input
              type="password"
              v-model="homeAssistant.long_lived_token"
              @blur="saveHomeAssistant"
              placeholder="Enter your Home Assistant long-lived token"
            />
            <small class="help-text">
              Create a long-lived access token in Home Assistant: Profile → Long-Lived Access Tokens
            </small>
          </label>
        </div>

        <div v-if="homeAssistant.enabled && homeAssistant.url && homeAssistant.long_lived_token" class="status-indicator">
          <span class="status-dot" :class="{ connected: isConnected }"></span>
          <span>{{ isConnected ? "Connected" : "Not Connected" }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  name: "Settings",
  data() {
    return {
      homeAssistant: {
        enabled: false,
        url: "",
        long_lived_token: "",
      },
      isConnected: false,
      saveTimeout: null,
    };
  },
  async mounted() {
    await this.loadSettings();
  },
  methods: {
    async loadSettings() {
      try {
        const res = await api.getAppSettings();
        const settings = res.data.settings;
        
        if (settings.home_assistant) {
          this.homeAssistant = {
            enabled: settings.home_assistant.enabled || false,
            url: settings.home_assistant.url || "",
            long_lived_token: settings.home_assistant.long_lived_token || "",
          };
        }
      } catch (e) {
        console.error("Failed to load settings:", e);
      }
    },
    async saveHomeAssistant() {
      // Debounce saves
      if (this.saveTimeout) {
        clearTimeout(this.saveTimeout);
      }
      
      this.saveTimeout = setTimeout(async () => {
        try {
          await api.updateAppSettings("home_assistant", this.homeAssistant);
          // Optionally test connection here
        } catch (e) {
          alert("Failed to save settings: " + e);
        }
      }, 500);
    },
  },
};
</script>

<style scoped>
.settings {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.settings h2 {
  margin-bottom: 2rem;
  color: #42b883;
}

.settings-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.settings-section {
  background: #2a2a2a;
  border-radius: 8px;
  padding: 2rem;
  border: 1px solid #444;
}

.settings-section h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #42b883;
  font-size: 1.3rem;
}

.section-description {
  color: #aaa;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.setting-group {
  margin-bottom: 1.5rem;
}

.setting-label {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  color: #fff;
}

.setting-label input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
}

.setting-label input[type="text"],
.setting-label input[type="password"] {
  padding: 0.75rem;
  background: #1a1a1a;
  border: 1px solid #444;
  border-radius: 4px;
  color: white;
  font-size: 1rem;
  font-family: inherit;
}

.setting-label input:focus {
  outline: none;
  border-color: #42b883;
}

.help-text {
  color: #888;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem;
  background: #1a1a1a;
  border-radius: 4px;
  color: #aaa;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #666;
}

.status-dot.connected {
  background: #42b883;
  box-shadow: 0 0 8px #42b883;
}
</style>
