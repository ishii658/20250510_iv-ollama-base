/// <reference types="vitest" />

import legacy from '@vitejs/plugin-legacy'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    legacy()
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/save_markdown': 'http://localhost:8000/',
      '/get_memo_list': 'http://localhost:8000/',
      '/get_memo': 'http://localhost:8000/',
      '/del_markdown': 'http://localhost:8000/'
    }
  },
  build:{
    minify: 'terser',
    sourcemap: true,
  },
  test: {
    globals: true,
    environment: 'jsdom'
  }
})
