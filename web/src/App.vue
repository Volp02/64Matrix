<template>
  <div class="app-container">
    <header>
      <h1>Lajos Matrix V2</h1>
      <nav>
        <router-link to="/">Dashboard</router-link>
        <router-link to="/library">Library</router-link>
        <router-link to="/playlists">Playlists</router-link>
      </nav>
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
  background: #111;
  color: #fff;
  font-family: "Inter", sans-serif;
}

.app-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

header {
  text-align: center;
  margin-bottom: 2rem;
}

h1 {
  background: linear-gradient(45deg, #42b883, #35495e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

nav {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
}

nav a {
  color: #888;
  text-decoration: none;
  font-size: 1.1rem;
  transition: color 0.2s;
}

nav a:hover,
nav a.router-link-active {
  color: #42b883;
  font-weight: bold;
}
</style>
