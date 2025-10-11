import { defineConfig } from '@rslib/core'

export default defineConfig({
  lib: [
    {
      format: 'esm',
      bundle: true,
      dts: true,
    },
  ],
  source: {
    entry: {
      index: './src/index.ts',
      platform: './src/platform.ts',
    },
  },
})
