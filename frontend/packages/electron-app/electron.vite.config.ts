import { defineConfig, externalizeDepsPlugin } from 'electron-vite'

export default defineConfig({
  main: {
    plugins: [externalizeDepsPlugin()],
    define: {
      __BUILD_MODE__: JSON.stringify(process.env.BUILD_MODE || 'dev'),
    },
  },
  preload: {
    plugins: [externalizeDepsPlugin()],
  },
})
