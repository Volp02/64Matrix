import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  getSystemStatus() {
    return apiClient.get('/system/status');
  },
  getSystemStats() {
    return apiClient.get('/system/stats');
  },
  updateSettings(settings) {
    return apiClient.post('/system/settings', settings);
  },
  getScenes() {
    return apiClient.get('/scenes/');
  },
  activateScene(filename) {
    return apiClient.post('/scenes/activate', { filename });
  },
  deleteScene(filename) {
    return apiClient.delete(`/scenes/${filename}`);
  },
  renameScene(filename, newName) {
    return apiClient.put(`/scenes/${filename}`, { new_name: newName });
  },
  uploadThumbnail(filename, file) {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post(`/scenes/${filename}/thumbnail`, formData, {
      headers: {
         'Content-Type': 'multipart/form-data'
      }
    });
  },
  uploadFile(formData) {
    return apiClient.post('/upload/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  getThumbnailUrl(filename) {
     return `/api/scenes/thumbnails/${filename}`;
  },
  getPreviewUrl() {
    // Add timestamp to prevent caching
    return `/api/system/preview?t=${Date.now()}`;
  },
  // Playlists
  getPlaylists() {
    return apiClient.get("/playlists/");
  },
  savePlaylist(playlist) {
    return apiClient.post("/playlists/", playlist);
  },
  deletePlaylist(id) {
    return apiClient.delete(`/playlists/${id}`);
  },
  playPlaylist(id) {
    return apiClient.post(`/playlists/${id}/play`);
  },
  autoGenerateAllPlaylist() {
    return apiClient.post("/playlists/auto-generate-all");
  },
  // Palettes
  getPalettes() {
    return apiClient.get("/palettes/");
  },
  getPalette(id) {
    return apiClient.get(`/palettes/${id}`);
  },
  createPalette(palette) {
    return apiClient.post("/palettes/", palette);
  },
  updatePalette(id, palette) {
    return apiClient.put(`/palettes/${id}`, palette);
  },
  deletePalette(id) {
    return apiClient.delete(`/palettes/${id}`);
  },
  selectPalette(id) {
    return apiClient.post(`/palettes/${id}/select`);
  },
  // App Settings
  getAppSettings() {
    return apiClient.get("/settings/");
  },
  getAppSettingCategory(category) {
    return apiClient.get(`/settings/${category}`);
  },
  updateAppSettings(category, settings) {
    return apiClient.put(`/settings/${category}`, settings);
  },
  updateAppSetting(category, key, value) {
    return apiClient.put(`/settings/${category}/${key}`, value, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
};
