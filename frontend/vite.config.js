import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3103,
    host: true,
    allowedHosts: ['demo-gauntlet.test', 'localhost'],
    proxy: {
      '/ingestion': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
      },
      '/research': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
      },
      '/challenges': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
      },
      '/evaluation': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
      },
    }
  }
})
