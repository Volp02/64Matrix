<template>
  <div class="playlist-editor">
    <header class="editor-header">
      <input
        v-model="playlistName"
        placeholder="Playlist Name"
        class="name-input"
      />
      <div class="palette-selector">
        <label>Default Palette:</label>
        <select v-model="defaultPalette" class="palette-select">
          <option value="">None (use global)</option>
          <optgroup label="Default Palettes">
            <option
              v-for="palette in defaultPalettes"
              :key="palette.id"
              :value="palette.id"
            >
              {{ palette.name }}
            </option>
          </optgroup>
          <optgroup label="Custom Palettes" v-if="customPalettes.length > 0">
            <option
              v-for="palette in customPalettes"
              :key="palette.id"
              :value="palette.id"
            >
              {{ palette.name }}
            </option>
          </optgroup>
        </select>
      </div>
      <div class="duration-selector">
        <label>Default Duration (s):</label>
        <input
          type="number"
          v-model.number="defaultDuration"
          min="1"
          step="0.5"
          class="duration-select-input"
          placeholder="30"
        />
        <button 
          @click="applyDefaultDuration" 
          class="apply-duration-btn"
          :disabled="items.length === 0"
          title="Apply default duration to all scenes"
        >
          Apply to All
        </button>
      </div>
      <div class="actions">
        <button @click="savePlaylist" class="save-btn">💾 Save Playlist</button>
        <button @click="$router.push('/library')" class="cancel-btn">
          Back to Library
        </button>
      </div>
    </header>

    <div class="editor-workspace">
      <!-- Left Column: Source Scenes -->
      <div class="column source-column">
        <h3>Available Scenes</h3>
        <div class="scene-list">
          <div
            v-for="scene in availableScenes"
            :key="scene.filename"
            class="scene-card source-card"
            draggable="true"
            @dragstart="onDragStart($event, scene)"
          >
            <span class="scene-type">{{ scene.type }}</span>
            <span class="scene-name">{{ scene.name }}</span>
            <button class="add-btn" @click="addItem(scene)">+</button>
          </div>
        </div>
      </div>

      <!-- Right Column: Timeline -->
      <div class="column timeline-column" @dragover.prevent @drop="onDrop">
        <h3>Sequence Timeline ({{ totalDuration }}s)</h3>

        <div v-if="items.length === 0" class="empty-state">
          Drag scenes here or click '+' to add to playlist
        </div>

        <div class="timeline-list">
          <div
            v-for="(item, index) in items"
            :key="index"
            class="scene-card timeline-card"
          >
            <div class="card-header">
              <span class="item-index">{{ index + 1 }}.</span>
              <span class="scene-name">{{ item.name || item.filename }}</span>
              <button class="remove-btn" @click="removeItem(index)">❌</button>
            </div>

            <div class="card-controls">
              <label>Duration (s):</label>
              <input
                type="number"
                v-model.number="item.duration"
                min="1"
                class="duration-input"
              />
              <div v-if="item.type === 'script'" class="palette-selector-inline">
                <label>Palette:</label>
                <select v-model="item.palette" class="palette-select-small">
                  <option value="">Default</option>
                  <optgroup label="Default">
                    <option
                      v-for="palette in defaultPalettes"
                      :key="palette.id"
                      :value="palette.id"
                    >
                      {{ palette.name }}
                    </option>
                  </optgroup>
                  <optgroup label="Custom" v-if="customPalettes.length > 0">
                    <option
                      v-for="palette in customPalettes"
                      :key="palette.id"
                      :value="palette.id"
                    >
                      {{ palette.name }}
                    </option>
                  </optgroup>
                </select>
              </div>
              <div class="order-controls">
                <button @click="moveItem(index, -1)" :disabled="index === 0">
                  ▲
                </button>
                <button
                  @click="moveItem(index, 1)"
                  :disabled="index === items.length - 1"
                >
                  ▼
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  name: "PlaylistEditor",
  data() {
    return {
      playlistId: null, // If editing existing
      playlistName: "My New Playlist",
      items: [], // { filename, type, duration, name, palette... }
      availableScenes: [],
      defaultPalette: "", // Default palette for the playlist
      defaultDuration: 30, // Default duration for all scenes
      defaultPalettes: [],
      customPalettes: [],
    };
  },
  computed: {
    totalDuration() {
      return this.items.reduce((acc, item) => acc + (item.duration || 30), 0);
    },
  },
  async mounted() {
    await this.fetchScenes();
    await this.fetchPalettes();
    const id = this.$route.params.id;
    if (id) {
      await this.loadPlaylist(id);
    }
  },
  methods: {
    async loadPlaylist(id) {
      try {
        const res = await api.getPlaylists(); // Optimization: get single if available, or just filter
        const playlists = res.data.playlists || {};
        const pl = playlists[id];
        if (pl) {
          this.playlistId = pl.id;
          this.playlistName = pl.name;
          // Clone items and ensure palette field exists (for backward compatibility)
          this.items = pl.items.map((i) => ({
            filename: i.filename,
            type: i.type,
            duration: i.duration || pl.default_duration || 30,
            name: i.name || i.filename,
            palette: i.palette || "", // Default to empty string if not present
          }));
          this.defaultPalette = pl.default_palette || "";
          this.defaultDuration = pl.default_duration || 30;
        }
      } catch (e) {
        console.error("Failed to load playlist", e);
      }
    },
    async fetchScenes() {
      try {
        const res = await api.getScenes();
        this.availableScenes = res.data.scenes;
      } catch (e) {
        console.error("Failed to load scenes", e);
      }
    },
    async fetchPalettes() {
      try {
        const res = await api.getPalettes();
        this.defaultPalettes = Object.values(res.data.default || {});
        this.customPalettes = Object.values(res.data.custom || {});
      } catch (e) {
        console.error("Failed to load palettes", e);
      }
    },

    addItem(scene) {
      this.items.push({
        filename: scene.filename,
        type: scene.type,
        name: scene.name,
        duration: this.defaultDuration || 30, // Use default duration
        palette: "", // No palette by default (uses playlist default or global)
      });
    },

    removeItem(index) {
      this.items.splice(index, 1);
    },

    moveItem(index, direction) {
      if (index + direction < 0 || index + direction >= this.items.length)
        return;
      const item = this.items[index];
      this.items.splice(index, 1);
      this.items.splice(index + direction, 0, item);
    },
    
    applyDefaultDuration() {
      if (!this.defaultDuration || this.defaultDuration <= 0) {
        alert("Please set a valid default duration first");
        return;
      }
      if (confirm(`Apply ${this.defaultDuration}s duration to all ${this.items.length} scenes?`)) {
        this.items.forEach(item => {
          item.duration = this.defaultDuration;
        });
      }
    },

    onDragStart(event, scene) {
      event.dataTransfer.setData("scene", JSON.stringify(scene));
    },

    onDrop(event) {
      const sceneData = event.dataTransfer.getData("scene");
      if (sceneData) {
        const scene = JSON.parse(sceneData);
        this.addItem(scene);
      }
    },

    async savePlaylist() {
      if (!this.playlistName) return alert("Please name your playlist");

      const id =
        this.playlistId ||
        this.playlistName.toLowerCase().replace(/[^a-z0-9]/g, "_");

      const payload = {
        id: id,
        name: this.playlistName,
        items: this.items.map((i) => ({
          filename: i.filename,
          type: i.type,
          duration: i.duration,
          palette: i.type === "script" ? (i.palette && i.palette.trim() ? i.palette : null) : null, // Only include palette for scripts, convert empty string to null
        })),
        default_palette: this.defaultPalette && this.defaultPalette.trim() ? this.defaultPalette : null,
        default_duration: this.defaultDuration && this.defaultDuration > 0 ? this.defaultDuration : null,
        settings: {}, // Include settings for compatibility
      };

      try {
        await api.savePlaylist(payload);
        alert("Playlist Saved!");
        this.$router.push("/playlists");
      } catch (e) {
        alert("Failed to save: " + e);
      }
    },
  },
};
</script>

<style scoped>
.playlist-editor {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px); /* Adjust based on header */
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #222;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.palette-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.palette-selector label {
  color: #ccc;
  font-size: 0.9rem;
}

.palette-select {
  background: #333;
  border: 1px solid #444;
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  min-width: 150px;
}

.duration-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.duration-selector label {
  color: #ccc;
  font-size: 0.9rem;
}

.duration-select-input {
  background: #333;
  border: 1px solid #444;
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  width: 80px;
  text-align: center;
}

.apply-duration-btn {
  background: #555;
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
}

.apply-duration-btn:hover:not(:disabled) {
  background: #666;
}

.apply-duration-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.palette-selector-inline {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.palette-selector-inline label {
  color: #aaa;
  font-size: 0.85rem;
}

.palette-select-small {
  background: #444;
  border: 1px solid #555;
  color: white;
  padding: 2px 5px;
  border-radius: 2px;
  font-size: 0.85rem;
  min-width: 100px;
}

.name-input {
  background: #333;
  border: 1px solid #444;
  color: white;
  padding: 0.5rem;
  font-size: 1.2rem;
  border-radius: 4px;
  width: 300px;
}

.actions {
  display: flex;
  gap: 1rem;
}

.save-btn {
  background: #42b883;
  border: none;
  padding: 0.5rem 1.5rem;
  color: #111;
  font-weight: bold;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn {
  background: #555;
  border: none;
  padding: 0.5rem 1.5rem;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

.editor-workspace {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 1rem;
  flex-grow: 1;
  overflow: hidden;
}

.column {
  background: #222;
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.column h3 {
  margin-top: 0;
  border-bottom: 2px solid #333;
  padding-bottom: 0.5rem;
}

.scene-list,
.timeline-list {
  flex-grow: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.scene-card {
  background: #333;
  padding: 0.8rem;
  border-radius: 4px;
  border: 1px solid #444;
}

.source-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: grab;
}

.source-card:active {
  cursor: grabbing;
}

.scene-name {
  font-weight: bold;
  flex-grow: 1;
  margin: 0 0.5rem;
}

.scene-type {
  font-size: 0.7rem;
  background: #444;
  padding: 2px 4px;
  border-radius: 2px;
  color: #aaa;
}

.add-btn {
  background: #4a4;
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
}

.timeline-card {
  background: #2a2a2a;
  border-left: 4px solid #42b883;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.card-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.9rem;
}

.duration-input {
  width: 60px;
  background: #444;
  border: none;
  color: white;
  padding: 2px 5px;
  border-radius: 2px;
}

.order-controls button {
  background: #444;
  border: none;
  color: white;
  padding: 2px 6px;
  cursor: pointer;
  margin-left: 2px;
}

.order-controls button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
}
</style>
