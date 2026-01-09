import { defineConfig } from 'tsdown'

export default defineConfig({
  entry: ['src/index.ts', 'src/platform.ts'],
  format: ['esm', 'commonjs'],
  dts: {
    sourcemap: true,
  },
})