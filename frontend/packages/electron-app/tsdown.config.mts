import { defineConfig } from 'tsdown'

export default defineConfig({
  entry: 'src/sdk/index.ts',
  format: 'iife',
  dts: false,
  clean: false,
  platform: 'browser',
  sourcemap: true,
  outDir: '../../public/',
  noExternal: ['lodash-es'],
  minify: true,
  outputOptions: {
    entryFileNames: 'client-sdk.js',
  },
})
