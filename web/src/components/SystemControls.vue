<template>
  <div class="system-controls">
    <div class="control-group">
      <label>Brightness: {{ settings.brightness }}%</label>
      <input
        type="range"
        min="0"
        max="100"
        v-model.number="localSettings.brightness"
        @change="update"
      />
    </div>

    <div class="control-group">
      <label>Speed: {{ settings.speed }}x</label>
      <input
        type="range"
        min="0.1"
        max="2.0"
        step="0.1"
        v-model.number="localSettings.speed"
        @change="update"
      />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    settings: Object,
  },
  data() {
    return {
      localSettings: { ...this.settings },
    };
  },
  watch: {
    settings: {
      handler(newVal) {
        this.localSettings = { ...newVal };
      },
      deep: true,
    },
  },
  methods: {
    update() {
      this.$emit("update", this.localSettings);
    },
  },
};
</script>

<style scoped>
.system-controls {
  background: #1e1e1e;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  display: flex;
  gap: 2rem;
  justify-content: center;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 200px;
}

input[type="range"] {
  width: 100%;
}
</style>
