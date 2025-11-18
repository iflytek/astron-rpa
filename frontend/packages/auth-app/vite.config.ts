import { fileURLToPath } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

const basePublic = fileURLToPath(new URL('../../public', import.meta.url))

// https://vite.dev/config/
export default defineConfig({
  publicDir: basePublic,
  plugins: [vue()],
})
