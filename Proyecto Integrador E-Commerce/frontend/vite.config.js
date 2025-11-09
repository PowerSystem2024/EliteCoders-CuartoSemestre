import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// Vite config: use absolute base '/' for built assets so that when the user
// opens a nested SPA route directly (e.g. /payments/success/3) the browser
// will request assets from /assets/... instead of /payments/success/3/assets/...
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  // Force absolute base for production builds
  base: '/',
  server: {
    port: 5173, // solo para dev local
    strictPort: false,
  },
})
