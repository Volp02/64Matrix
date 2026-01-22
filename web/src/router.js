import { createRouter, createWebHashHistory } from 'vue-router'
import Home from './views/Home.vue'
import Library from './views/Library.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/library', component: Library },
  { path: '/playlists', component: () => import('./views/Playlists.vue') },
  { path: '/palettes', component: () => import('./views/ColorPalettes.vue') },
  {
    path: "/editor/:id?",
    name: "Editor",
    component: () => import("./views/PlaylistEditor.vue"),
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
