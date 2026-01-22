<template>
  <div class="scene-grid">
    <div
      v-for="scene in scenes"
      :key="scene.filename"
      class="scene-card"
      :class="{
        active: activeScene === scene.filename || activeScene === scene.name,
      }"
      @click="$emit('activate', scene.filename)"
    >
      <div class="scene-icon">
        <span v-if="scene.type === 'script'">🐍</span>
        <span v-else>🎬</span>
      </div>
      <div class="scene-name">{{ scene.name }}</div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    scenes: Array,
    activeScene: String,
  },
};
</script>

<style scoped>
.scene-grid {
  display: grid;
  grid-template_columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.scene-card {
  background: #2a2a2a;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.scene-card:hover {
  background: #3a3a3a;
  transform: translateY(-2px);
}

.scene-card.active {
  border-color: #42b883;
  background: #1a1a1a;
}

.scene-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.scene-name {
  font-size: 0.9rem;
  font-weight: bold;
}
</style>
