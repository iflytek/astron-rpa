import { fileURLToPath } from 'node:url'

import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import { defineConfig } from 'vite'

const basePublic = fileURLToPath(new URL('../../public', import.meta.url))

// https://vite.dev/config/
export default defineConfig({
  publicDir: basePublic,
  base: './',
  plugins: [
    vue({
      include: [/\.vue$/, /\.md$/],
    }),
    vueJsx(),
  ],
  server: {
    hmr: true,
    watch: {
      usePolling: false,
      ignored: ['!**/node_modules/@rpa/**'],
    },
    host: true,
    port: 3000,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://dev.iflyrpa.private:31680',
        changeOrigin: true,
        secure: false,
        // rewrite: path => path.replace(/^\/api/, ''),
      },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  optimizeDeps: {
    exclude: ['@rpa/components', '@rpa/shared'],
    include: ['vue', 'ant-design-vue'],
    force: true,
  },
  esbuild: {
    target: 'esnext',
  },
})
