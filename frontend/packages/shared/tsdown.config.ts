import { defineConfig } from 'tsdown'

export default defineConfig({
  entry: ['src/index.ts', 'src/platform.ts'],
  format: ['esm', 'commonjs'],
  inlineOnly: false,
  dts: {
    sourcemap: true,
  },
})
