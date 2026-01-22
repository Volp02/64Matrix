<template>
  <div class="library">
    <h2>Library</h2>

    <div class="library-grids">
      <!-- Clips Grid -->
      <div class="grid-section">
        <h3>Clips</h3>
        <div class="scene-grid">
          <div
            v-for="scene in clips"
            :key="scene.filename"
            class="scene-card"
            @click="activate(scene.filename)"
            @contextmenu.prevent="openContextMenu($event, scene)"
          >
            <img
              :src="getThumbUrl(scene.filename)"
              @error="setFallbackImg"
              class="thumbnail"
            />
            <div class="scene-name">{{ scene.name }}</div>
            <button
              class="menu-btn"
              @click.stop="openContextMenu($event, scene)"
              title="Menu"
            >
              ⋮
            </button>
          </div>
        </div>
      </div>

      <!-- Scripts Grid -->
      <div class="grid-section">
        <h3>Scripts</h3>
        <div class="scene-grid">
          <div
            v-for="scene in scripts"
            :key="scene.filename"
            class="scene-card"
            @click="activate(scene.filename)"
            @contextmenu.prevent="openContextMenu($event, scene)"
          >
            <img
              :src="getThumbUrl(scene.filename)"
              @error="setFallbackImg"
              class="thumbnail"
            />
            <div class="scene-name">{{ scene.name }}</div>
            <button
              class="menu-btn"
              @click.stop="openContextMenu($event, scene)"
              title="Menu"
            >
              ⋮
            </button>
          </div>
        </div>
      </div>

      <!-- Live Grid -->
      <div class="grid-section">
        <h3>Live</h3>
        <div class="scene-grid">
          <div
            v-for="scene in live"
            :key="scene.filename"
            class="scene-card"
            @click="activate(scene.filename)"
            @contextmenu.prevent="openContextMenu($event, scene)"
          >
            <img
              :src="getThumbUrl(scene.filename)"
              @error="setFallbackImg"
              class="thumbnail"
            />
            <div class="scene-name">{{ scene.name }}</div>
            <button
              class="menu-btn"
              @click.stop="openContextMenu($event, scene)"
              title="Menu"
            >
              ⋮
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Context Menu -->
    <div
      v-if="showContextMenu"
      class="context-menu"
      :style="{ top: contextMenuY + 'px', left: contextMenuX + 'px' }"
      @click.stop
    >
      <button @click="startRename(contextScene)">✏️ Rename</button>
      <button @click="triggerThumbUpload(contextScene.filename)">
        🖼️ Change Thumbnail
      </button>
      <button class="danger" @click="deleteScene(contextScene.filename)">
        🗑️ Delete
      </button>
    </div>

    <!-- Context Menu Overlay (closes menu on click) -->
    <div
      v-if="showContextMenu"
      class="context-overlay"
      @click="closeContextMenu"
    ></div>

    <!-- Edit Name Modal -->
    <div v-if="editing" class="modal-overlay" @click.self="cancelEdit">
      <div class="modal">
        <h3>Rename Scene</h3>
        <div class="edit-form">
          <input
            v-model="editName"
            @keyup.enter="saveRename(editing)"
            @keyup.esc="cancelEdit"
            placeholder="Scene name"
            autofocus
          />
          <div class="modal-actions">
            <button @click="saveRename(editing)">💾 Save</button>
            <button @click="cancelEdit">❌ Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal">
        <h3>Delete scene?</h3>
        <p class="warning">
          This will permanently delete <strong>{{ sceneToDelete }}</strong>.
        </p>
        <div class="modal-actions">
          <button class="danger" @click="confirmDelete">Delete</button>
          <button @click="cancelDelete">Cancel</button>
        </div>
      </div>
    </div>

    <UploadForm @upload-complete="fetchScenes" />
  </div>
</template>

<script>
import api from "../services/api";
import UploadForm from "../components/UploadForm.vue";

export default {
  name: "Library",
  components: { UploadForm },
  data() {
    return {
      scenes: [],
      editing: null,
      editName: "",
      refreshInterval: null,
      // Context Menu State
      showContextMenu: false,
      contextMenuX: 0,
      contextMenuY: 0,
      contextScene: null,
      // Delete Modal State
      showDeleteConfirm: false,
      sceneToDelete: null,
    };
  },
  computed: {
    clips() {
      return this.scenes.filter((s) => s.type === "clip");
    },
    scripts() {
      return this.scenes.filter((s) => s.type === "script");
    },
    live() {
      return this.scenes.filter((s) => s.type === "live");
    },
  },
  async mounted() {
    await this.fetchScenes();
    // Close context menu on outside click
    document.addEventListener("click", this.closeContextMenu);
  },
  beforeUnmount() {
    document.removeEventListener("click", this.closeContextMenu);
  },
  methods: {
    async fetchScenes() {
      try {
        const res = await api.getScenes();
        this.scenes = res.data.scenes;
      } catch (e) {
        console.error("Fetch scenes failed", e);
      }
    },
    getThumbUrl(filename) {
      return api.getThumbnailUrl(filename);
    },
    setFallbackImg(event) {
      event.target.src = "https://placehold.co/120x120/333/888?text=?";
    },
    openContextMenu(event, scene) {
      this.contextScene = scene;
      this.contextMenuX = event.clientX;
      this.contextMenuY = event.clientY;
      this.showContextMenu = true;
    },
    closeContextMenu() {
      this.showContextMenu = false;
      this.contextScene = null;
    },
    triggerThumbUpload(filename) {
      this.closeContextMenu();
      const input = document.createElement("input");
      input.type = "file";
      input.accept = "image/*";
      input.onchange = async (e) => {
        if (e.target.files.length > 0) {
          await this.uploadThumbnail(filename, e.target.files[0]);
        }
      };
      input.click();
    },
    async uploadThumbnail(filename, file) {
      try {
        await api.uploadThumbnail(filename, file);
        const img = document.querySelector(`img[src*="${filename}"]`);
        if (img) img.src = api.getThumbnailUrl(filename) + "?t=" + Date.now();
        await this.fetchScenes();
      } catch (e) {
        alert("Failed to upload thumbnail: " + e);
      }
    },
    startRename(scene) {
      this.closeContextMenu();
      this.editing = scene.filename;
      this.editName = scene.name;
    },
    cancelEdit() {
      this.editing = null;
      this.editName = "";
    },
    async saveRename(oldFilename) {
      if (!this.editName) return;
      try {
        await api.renameScene(oldFilename, this.editName);
        this.editing = null;
        await this.fetchScenes();
      } catch (e) {
        alert("Rename failed: " + e);
      }
    },
    deleteScene(filename) {
      this.closeContextMenu();
      this.sceneToDelete = filename;
      this.showDeleteConfirm = true;
    },
    cancelDelete() {
      this.showDeleteConfirm = false;
      this.sceneToDelete = null;
    },
    async confirmDelete() {
      if (!this.sceneToDelete) return;
      try {
        await api.deleteScene(this.sceneToDelete);
        await this.fetchScenes();
      } catch (e) {
        alert("Delete failed: " + e);
      } finally {
        this.cancelDelete();
      }
    },
    async activate(filename) {
      await api.activateScene(filename);
    },
  },
};
</script>

<style scoped>
.library {
  padding: 2rem;
}

.library h2 {
  margin-bottom: 2rem;
  color: #42b883;
}

.library-grids {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.grid-section h3 {
  margin-bottom: 1rem;
  color: #aaa;
  font-size: 1.2rem;
}

.scene-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 1rem;
}

.scene-card {
  background: #2a2a2a;
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.scene-card:hover {
  background: #3a3a3a;
  transform: translateY(-2px);
  border-color: #42b883;
}

.thumbnail {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #444;
}

.scene-name {
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  color: #fff;
  word-break: break-word;
  max-width: 100%;
}

.menu-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  font-size: 1.2rem;
  line-height: 1;
  opacity: 0;
  transition: opacity 0.2s;
}

.scene-card:hover .menu-btn {
  opacity: 1;
}

.menu-btn:hover {
  background: rgba(0, 0, 0, 0.8);
}

/* Context Menu */
.context-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 999;
}

.context-menu {
  position: fixed;
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 8px;
  padding: 0.5rem;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  min-width: 180px;
}

.context-menu button {
  display: block;
  width: 100%;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  text-align: left;
  transition: background 0.2s;
  font-size: 0.9rem;
}

.context-menu button:hover {
  background: #3a3a3a;
}

.context-menu button.danger {
  color: #f55;
}

.context-menu button.danger:hover {
  background: #422;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal {
  background: #2a2a2a;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
  text-align: center;
  border: 1px solid #444;
  min-width: 300px;
}

.modal h3 {
  margin-top: 0;
  color: #42b883;
}

.modal .warning {
  color: #e55;
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.edit-form input {
  padding: 0.75rem;
  background: #1a1a1a;
  border: 1px solid #444;
  border-radius: 4px;
  color: white;
  font-size: 1rem;
}

.edit-form input:focus {
  outline: none;
  border-color: #42b883;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

button {
  padding: 0.5rem 1rem;
  background: #444;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover {
  background: #555;
}

button.danger {
  background: #842;
}

button.danger:hover {
  background: #a53;
}

/* Responsive */
@media (max-width: 1400px) {
  .library-grids {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .library-grids {
    grid-template-columns: 1fr;
  }
}
</style>
