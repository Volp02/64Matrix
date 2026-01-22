<template>
  <div class="upload-form">
    <h3>Upload Content</h3>
    <div class="drop-zone" @click="$refs.fileInput.click()">
      <p v-if="!selectedFile">Click or Drag files here (ZIP, GIF, or PY)</p>
      <p v-else>Selected: {{ selectedFile.name }}</p>
      <input
        type="file"
        ref="fileInput"
        @change="handleFileSelect"
        style="display: none"
        accept=".zip,.gif,.py"
      />
    </div>
    <p v-if="successMessage" class="success-msg">{{ successMessage }}</p>
    <button
      class="upload-btn"
      :disabled="!selectedFile || uploading"
      @click="upload"
    >
      {{ uploading ? "Uploading..." : "Upload" }}
    </button>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  data() {
    return {
      selectedFile: null,
      uploading: false,
      successMessage: "",
    };
  },
  methods: {
    handleFileSelect(event) {
      this.selectedFile = event.target.files[0];
      this.successMessage = "";
    },
    async upload() {
      if (!this.selectedFile) return;

      this.uploading = true;
      this.successMessage = "";
      const formData = new FormData();
      formData.append("file", this.selectedFile);

      try {
        await api.uploadFile(formData);
        this.$emit("upload-complete");
        this.selectedFile = null;
        this.successMessage = "Upload Successful!";
        setTimeout(() => (this.successMessage = ""), 3000);
      } catch (error) {
        alert("Upload failed: " + error.message);
      } finally {
        this.uploading = false;
      }
    },
  },
};
</script>

<style scoped>
.upload-form {
  background: #2a2a2a;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  margin-top: 2rem;
}

.success-msg {
  color: #42b883;
  margin-bottom: 1rem;
  font-weight: bold;
}

.drop-zone {
  border: 2px dashed #666;
  padding: 2rem;
  margin: 1rem 0;
  cursor: pointer;
  border-radius: 4px;
}

.drop-zone:hover {
  border-color: #42b883;
}

.upload-btn {
  background: #42b883;
  color: #fff;
  border: none;
  padding: 0.5rem 2rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.upload-btn:disabled {
  background: #555;
  cursor: not-allowed;
}
</style>
