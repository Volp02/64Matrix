<template>
  <div class="color-palettes">
    <h2>Color Palettes</h2>

    <!-- Default Palettes Section -->
    <section class="palette-section">
      <h3>Default Palettes</h3>
      <div class="palette-grid default-grid">
        <div
          v-for="palette in defaultPalettes"
          :key="palette.id"
          class="palette-card"
          :class="{ selected: selectedPaletteId === palette.id }"
          @click="selectPalette(palette.id)"
        >
          <div class="palette-preview">
            <div
              v-for="(color, idx) in palette.colors"
              :key="idx"
              class="color-swatch"
              :style="{ backgroundColor: color }"
              :title="color"
            ></div>
          </div>
          <div class="palette-name">{{ palette.name }}</div>
          <div v-if="selectedPaletteId === palette.id" class="selected-badge">✓ Selected</div>
        </div>
      </div>
    </section>

    <!-- Custom Palettes Section -->
    <section class="palette-section">
      <h3>Your Palettes</h3>
      <div class="palette-grid custom-grid">
        <!-- Add New Palette Card -->
        <div class="palette-card add-card" @click="showCreateModal = true">
          <div class="add-icon">+</div>
          <div class="palette-name">Add Palette</div>
        </div>

        <!-- Custom Palette Cards -->
        <div
          v-for="palette in customPalettes"
          :key="palette.id"
          class="palette-card"
          :class="{ selected: selectedPaletteId === palette.id }"
          @click="selectPalette(palette.id)"
        >
          <div class="palette-preview">
            <div
              v-for="(color, idx) in palette.colors"
              :key="idx"
              class="color-swatch"
              :style="{ backgroundColor: color }"
              :title="color"
            ></div>
          </div>
          <div class="palette-name">{{ palette.name }}</div>
          <div v-if="selectedPaletteId === palette.id" class="selected-badge">✓ Selected</div>
          <button
            class="edit-btn"
            @click.stop="editPalette(palette)"
            title="Edit palette"
          >
            ✎
          </button>
          <button
            class="delete-btn"
            @click.stop="deletePalette(palette.id)"
            title="Delete palette"
          >
            ×
          </button>
        </div>
      </div>
    </section>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingPalette" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>{{ editingPalette ? 'Edit Palette' : 'Create New Palette' }}</h3>
        <div class="modal-content">
          <div class="form-group">
            <label>Palette Name:</label>
            <input v-model="paletteForm.name" type="text" placeholder="Enter palette name" />
          </div>
          <div class="form-group">
            <label>Colors (hex format, one per line or comma-separated):</label>
            <textarea
              v-model="paletteForm.colorsText"
              placeholder="#FF0000, #00FF00, #0000FF"
              rows="6"
            ></textarea>
            <small>Enter colors in hex format (e.g., #FF0000)</small>
          </div>
          <div class="color-preview">
            <div
              v-for="(color, idx) in parsedColors"
              :key="idx"
              class="preview-swatch"
              :style="{ backgroundColor: color }"
              :title="color"
            >
              <button
                class="remove-color"
                @click="removeColor(idx)"
                v-if="parsedColors.length > 1"
              >
                ×
              </button>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="savePalette" :disabled="!isFormValid">Save</button>
          <button @click="closeModal">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  name: "ColorPalettes",
  data() {
    return {
      defaultPalettes: [],
      customPalettes: [],
      selectedPaletteId: null,
      showCreateModal: false,
      editingPalette: null,
      paletteForm: {
        name: "",
        colorsText: "",
      },
    };
  },
  computed: {
    parsedColors() {
      if (!this.paletteForm.colorsText) return [];
      
      // Split by comma or newline
      const colors = this.paletteForm.colorsText
        .split(/[,\n]/)
        .map((c) => c.trim())
        .filter((c) => c.length > 0);
      
      // Validate hex format
      return colors.filter((c) => /^#[0-9A-Fa-f]{6}$/.test(c));
    },
    isFormValid() {
      return (
        this.paletteForm.name.trim().length > 0 &&
        this.parsedColors.length > 0
      );
    },
  },
  async mounted() {
    await this.fetchPalettes();
    await this.fetchSelectedPalette();
  },
  methods: {
    async fetchPalettes() {
      try {
        const res = await api.getPalettes();
        this.defaultPalettes = Object.values(res.data.default || {});
        this.customPalettes = Object.values(res.data.custom || {});
      } catch (e) {
        console.error("Failed to fetch palettes", e);
        alert("Failed to load palettes: " + e);
      }
    },
    async fetchSelectedPalette() {
      try {
        const res = await api.getSystemStatus();
        this.selectedPaletteId = res.data.selected_palette || "aurora";
      } catch (e) {
        console.error("Failed to fetch selected palette", e);
      }
    },
    async selectPalette(paletteId) {
      try {
        await api.selectPalette(paletteId);
        this.selectedPaletteId = paletteId;
      } catch (e) {
        alert("Failed to select palette: " + e);
      }
    },
    editPalette(palette) {
      this.editingPalette = palette;
      this.paletteForm.name = palette.name;
      this.paletteForm.colorsText = palette.colors.join(", ");
    },
    removeColor(index) {
      const colors = this.parsedColors;
      colors.splice(index, 1);
      this.paletteForm.colorsText = colors.join(", ");
    },
    async savePalette() {
      if (!this.isFormValid) return;

      try {
        const paletteData = {
          name: this.paletteForm.name,
          colors: this.parsedColors,
        };

        if (this.editingPalette) {
          await api.updatePalette(this.editingPalette.id, {
            ...paletteData,
            id: this.editingPalette.id,
          });
        } else {
          await api.createPalette(paletteData);
        }

        await this.fetchPalettes();
        this.closeModal();
      } catch (e) {
        alert("Failed to save palette: " + e);
      }
    },
    async deletePalette(id) {
      if (!confirm("Delete this palette?")) return;

      try {
        await api.deletePalette(id);
        await this.fetchPalettes();
      } catch (e) {
        alert("Failed to delete palette: " + e);
      }
    },
    closeModal() {
      this.showCreateModal = false;
      this.editingPalette = null;
      this.paletteForm = {
        name: "",
        colorsText: "",
      };
    },
  },
};
</script>

<style scoped>
.color-palettes {
  padding: 1rem;
}

h2 {
  color: #42b883;
  margin-bottom: 2rem;
}

h3 {
  color: #888;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.palette-section {
  margin-bottom: 3rem;
}

.palette-grid {
  display: grid;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.default-grid {
  grid-template-columns: repeat(4, 1fr);
}

.custom-grid {
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}

.palette-card {
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}

.palette-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.palette-card.selected {
  border-color: #42b883;
  border-width: 2px;
  box-shadow: 0 0 10px rgba(66, 184, 131, 0.3);
}

.selected-badge {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  background: #42b883;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: bold;
}

.edit-btn {
  position: absolute;
  top: 0.5rem;
  right: 2.5rem;
  background: rgba(66, 184, 131, 0.7);
  border: none;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.palette-card:hover .edit-btn {
  opacity: 1;
}

.edit-btn:hover {
  background: rgba(66, 184, 131, 1);
}

.add-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 150px;
  border: 2px dashed #555;
  background: #1e1e1e;
}

.add-card:hover {
  border-color: #42b883;
  background: #252525;
}

.add-icon {
  font-size: 3rem;
  color: #888;
  margin-bottom: 0.5rem;
}

.add-card:hover .add-icon {
  color: #42b883;
}

.palette-preview {
  display: flex;
  gap: 2px;
  margin-bottom: 0.75rem;
  border-radius: 4px;
  overflow: hidden;
  height: 60px;
}

.color-swatch {
  flex: 1;
  min-width: 0;
  transition: transform 0.2s;
}

.color-swatch:hover {
  transform: scaleY(1.1);
  z-index: 1;
  position: relative;
}

.palette-name {
  text-align: center;
  color: #fff;
  font-weight: 500;
  font-size: 0.9rem;
}

.delete-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(255, 0, 0, 0.7);
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  color: white;
  cursor: pointer;
  font-size: 1.2rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.palette-card:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: rgba(255, 0, 0, 1);
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
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  border: 1px solid #444;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  margin-top: 0;
  color: #42b883;
}

.modal-content {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #ccc;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  background: #1e1e1e;
  border: 1px solid #444;
  border-radius: 4px;
  color: #fff;
  font-family: inherit;
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #42b883;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  color: #888;
  font-size: 0.85rem;
}

.color-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 1rem;
  background: #1e1e1e;
  border-radius: 4px;
}

.preview-swatch {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  position: relative;
  border: 2px solid #444;
}

.remove-color {
  position: absolute;
  top: -8px;
  right: -8px;
  background: rgba(255, 0, 0, 0.8);
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  color: white;
  cursor: pointer;
  font-size: 0.9rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.modal-actions button {
  padding: 0.75rem 1.5rem;
  background: #42b883;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.modal-actions button:hover:not(:disabled) {
  background: #35a372;
}

.modal-actions button:disabled {
  background: #555;
  cursor: not-allowed;
}

.modal-actions button:last-child {
  background: #555;
}

.modal-actions button:last-child:hover {
  background: #666;
}

@media (max-width: 768px) {
  .default-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
