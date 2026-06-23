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
      '@45drives/cockpit-css': fileURLToPath(new URL('./src/lib/cockpit-css', import.meta.url)),
    },
  },
  build:{
    minify: false,
  }
})

