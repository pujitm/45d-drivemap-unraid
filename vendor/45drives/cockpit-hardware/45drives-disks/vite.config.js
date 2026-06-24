import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: "./",
  resolve: {
    alias: {
      // Vendored locally so the project builds without 45Drives' private
      // GitHub Packages registry. See src/lib/ for the reconstructions.
      '@45drives/cockpit-helpers': fileURLToPath(new URL('./src/lib/cockpitHelpers.js', import.meta.url)),
      // App.vue imports .../src/index.css (the full Tailwind entrypoint + tokens);
      // main.js imports .../dist/index.css, aliased to an empty entry so Tailwind
      // is not emitted twice. Neither lives under a `dist/` dir (which .gitignore
      // would swallow).
      '@45drives/cockpit-css/src/index.css': fileURLToPath(new URL('./src/lib/cockpit-css/index.css', import.meta.url)),
      '@45drives/cockpit-css/dist/index.css': fileURLToPath(new URL('./src/lib/cockpit-css/entry.css', import.meta.url)),
    },
  },
  build:{
    minify: false,
  }
})

