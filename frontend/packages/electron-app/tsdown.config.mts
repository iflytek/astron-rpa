import { defineConfig } from 'tsdown'

export default defineConfig({
  entry: 'src/sdk/index.ts',
  format: 'iife',
  dts: false,
  clean: false,
  platform: 'browser',
  sourcemap: true,
  outDir: '../../public/',
  minify: true,
  deps: {
    alwaysBundle: ['lodash-es', 'await-to-js'],
  },
  outputOptions: {
    entryFileNames: 'client-sdk.js',
  },
})
