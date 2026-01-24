<template>
  <div class="app-container">
    <header>
      <div class="nav-glass">
        <h1>Lajos Matrix V2</h1>
        <nav>
          <router-link to="/">Dashboard</router-link>
          <router-link to="/library">Library</router-link>
          <router-link to="/playlists">Playlists</router-link>
          <router-link to="/palettes">Palettes</router-link>
          <router-link to="/settings">Settings</router-link>
        </nav>
      </div>
    </header>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: "App",
};
</script>

<style>
body {
  margin: 0;
  background: radial-gradient(circle at top center, #1a1a24, #0f0f13);
  color: #fff;
  font-family: "Inter", sans-serif;
  min-height: 100vh;
}

h1, h2, h3, h4, h5, h6 {
  font-family: "Outfit", sans-serif;
}

.app-container {
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}

@media (max-width: 1024px) {
  .app-container {
    max-width: 800px;
  }
}

header {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.nav-glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 2rem;
  border-radius: 50px;
  display: flex;
  align-items: center;
  gap: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

h1 {
  background: linear-gradient(45deg, #42b883, #647eff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.5rem;
  margin: 0;
  font-weight: 700;
}

nav {
  display: flex;
  gap: 1.5rem;
}

nav a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.2s ease;
  padding: 0.5rem 1rem;
  border-radius: 20px;
}

nav a:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

nav a.router-link-active {
  color: #fff;
  background: #42b883;
  box-shadow: 0 4px 15px rgba(66, 184, 131, 0.4);
}
</style>
