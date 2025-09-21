import fs from 'node:fs'

import archiver from 'archiver'
import { defineConfig } from 'vite'

import { generateManifest } from './manifest'
import pkg from './package.json'

export default defineConfig((env) => {
  generateManifest(env.mode)

  return {
    resolve: {
      alias: {
        '@': '/src',
      },
    },
    build: {
      minify: 'terser',
      outDir: 'dist',
      emptyOutDir: true,
      assetsDir: 'src/static',

      terserOptions: {
        compress: {
          drop_debugger: true,
          drop_console: env.mode === 'publish',
        },
        mangle: {
          keep_fnames: true,
        },
      },
      rollupOptions: {
        input: {
          background: 'src/background.ts',
          content: 'src/content.ts',
        },
        output: {
          entryFileNames: '[name].js',
          chunkFileNames: '[name].js',
          assetFileNames: '[name].[extname]',
        },
        plugins: [
          {
            name: 'extension-plugin',
            async buildStart() {

            },
            async closeBundle() {
              console.log('zip ...')
              const zipName = `rpa-extension-v3-${pkg.version}-${env.mode}.zip`
              const output = fs.createWriteStream(zipName)
              const archive = archiver('zip', {
                zlib: { level: 9 },
              })
              output.on('close', () => {
                console.log('zip done')
              })
              archive.on('error', (err) => {
                throw err
              })
              archive.pipe(output)
              archive.directory('dist', false)
              await archive.finalize()
            },
          },
        ],
      },
    },
  }
})
