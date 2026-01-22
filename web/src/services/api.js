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
  }
};
