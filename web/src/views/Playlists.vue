<template>
  <div class="playlists-view">
    <div class="header">
      <h2>Playlists</h2>
      <button @click="$router.push('/editor')">➕ Create Playlist</button>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Items</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pl in playlists" :key="pl.id">
            <td>{{ pl.name }}</td>
            <td>{{ pl.items.length }} scenes</td>
            <td class="actions">
              <button @click="playPlaylist(pl.id)">Play</button>
              <button @click="$router.push('/editor/' + pl.id)">Edit</button>
              <button class="danger" @click="deletePlaylist(pl.id)">
                Delete
              </button>
            </td>
          </tr>
          <tr v-if="playlists.length === 0">
            <td colspan="3" style="text-align: center; color: #666">
              No playlists created yet.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  name: "Playlists",
  data() {
    return {
      playlists: [],
    };
  },
  async mounted() {
    await this.fetchPlaylists();
  },
  methods: {
    async fetchPlaylists() {
      try {
        const res = await api.getPlaylists();
        this.playlists = Object.values(res.data.playlists || {});
      } catch (e) {
        console.error("Fetch playlists failed", e);
      }
    },
    async playPlaylist(id) {
      try {
        await api.playPlaylist(id);
      } catch (e) {
        alert("Failed to play: " + e);
      }
    },
    async deletePlaylist(id) {
      if (!confirm("Delete playlist?")) return;
      try {
        await api.deletePlaylist(id);
        await this.fetchPlaylists();
      } catch (e) {
        alert("Failed to delete: " + e);
      }
    },
  },
};
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

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
</style>
