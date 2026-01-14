import { defineConfig } from 'electron-vite'

export default defineConfig({
  main: {
    define: {
      __BUILD_MODE__: JSON.stringify(process.env.BUILD_MODE || 'dev'),
    },
  },
  preload: {},
})
