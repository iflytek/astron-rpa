import { build } from 'esbuild'

build({
  entryPoints: ['src/sdk/index.ts'],
  bundle: true,
  outfile: '../../public/client-sdk.js',
  platform: 'browser',
  format: 'iife',
  globalName: '',
  minify: true,
  sourcemap: false,
  target: ['es2021'],
}).then(() => console.log('Tauri SDK build succeeded.')).catch(() => process.exit(1))
