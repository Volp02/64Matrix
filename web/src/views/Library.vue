<template>
  <div class="library">
    <h2>Library</h2>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Thumb</th>
            <th>Name</th>
            <th>Type</th>
            <th>Type</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="scene in scenes" :key="scene.filename">
            <td class="thumb-cell">
              <img
                :src="getThumbUrl(scene.filename)"
                @error="setFallbackImg"
                class="thumbnail"
              />
              <input
                type="file"
                ref="thumbInput"
                style="display: none"
                @change="handleThumbUpload($event, scene.filename)"
              />
              <button
                class="icon-btn tiny"
                @click="triggerThumbUpload(scene.filename)"
              >
                ✎
              </button>
            </td>
            <td>
              <span v-if="editing !== scene.filename">{{ scene.name }}</span>
              <div v-else class="edit-row">
                <input
                  v-model="editName"
                  @keyup.enter="saveRename(scene.filename)"
                />
                <button @click="saveRename(scene.filename)">💾</button>
                <button @click="cancelEdit">❌</button>
              </div>
            </td>
            <td>{{ scene.type }}</td>
            <td>{{ scene.type }}</td>
            <td class="actions">
              <button @click="startRename(scene)">Rename</button>
              <button class="danger" @click="deleteScene(scene.filename)">
                Delete
              </button>
              <button @click="activate(scene.filename)">Play</button>
            </td>
          </tr>
        </tbody>
      </table>
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
      // Delete Modal State
      showDeleteConfirm: false,
      sceneToDelete: null,
    };
  },
  async mounted() {
    await this.fetchScenes();
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
      // Create a colored placeholder with initials? Or just a generic icon
      event.target.src = "https://placehold.co/60x60/333/888?text=?";
    },

    // Better approach for thumb upload:
    triggerThumbUpload(filename) {
      // We will create a temp input programmatically to keep template clean
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
        // Force refresh of image? Append timestamp to url
        // For now just re-fetch scenes (won't fix cache)
        // We might need to force reload logic in getThumbUrl
        const img = document.querySelector(`img[src*="${filename}"]`);
        if (img) img.src = api.getThumbnailUrl(filename) + "?t=" + Date.now();
        // Also refresh list to ensure metadata sync if we track thumb existence
        await this.fetchScenes();
      } catch (e) {
        alert("Failed to upload thumbnail: " + e);
      }
    },

    startRename(scene) {
      this.editing = scene.filename;
      this.editName = scene.name; // Use Display Name for editing

      this.$nextTick(() => {
        const input = document.querySelector(".edit-row input");
        if (input) input.focus();
      });
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

    // Delete Flow
    deleteScene(filename) {
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
      // Maybe show toast?
    },
  },
};
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
  background: #222;
  border-radius: 8px;
}

th,
td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #333;
}

th {
  background: #333;
  color: #42b883;
}

.thumbnail {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #444;
}

.thumb-cell {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tiny {
  padding: 2px 5px;
  font-size: 0.8rem;
  opacity: 0.5;
}
.tiny:hover {
  opacity: 1;
}

.actions {
  display: flex;
  gap: 0.5rem;
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

.edit-row {
  display: flex;
  gap: 0.5rem;
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
  z-index: 1000;
}

.modal {
  background: #2a2a2a;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
  text-align: center;
  border: 1px solid #444;
}

.modal h3 {
  margin-top: 0;
  color: #fca;
}

.modal .warning {
  color: #e55;
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}
</style>
