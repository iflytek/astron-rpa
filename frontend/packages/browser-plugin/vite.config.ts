import fs from 'node:fs'

import archiver from 'archiver'
import { defineConfig, loadEnv } from 'vite'

import { generateManifest } from './manifest'
import pkg from './package.json'

export default defineConfig((env) => {
  const environment = loadEnv(env.mode, process.cwd(), '')

  generateManifest(env.mode, environment)

  return {
    define: {
      __BUILD_MODE__: JSON.stringify(env.mode),
    },
    resolve: {
      alias: {
        '@': '/src',
      },
    },
    build: {
      minify: 'terser',
      outDir: 'dist',
      emptyOutDir: !environment.BUILD_ENTRY || environment.BUILD_ENTRY === 'background',
      assetsDir: 'src/static',
      cssCodeSplit: false,
      chunkSizeWarningLimit: 1000,
      terserOptions: {
        module: false,
        compress: {
          drop_debugger: true,
          drop_console: env.mode === 'publish',
        },
        mangle: {
          keep_classnames: true,
          keep_fnames: true,
        },
      },
      rollupOptions: {
        input: environment.BUILD_ENTRY === 'content'
          ? 'src/content.ts'
          : environment.BUILD_ENTRY === 'background'
            ? 'src/background.ts'
            : {
                background: 'src/background.ts',
                content: 'src/content.ts',
              }, // entry points for background and content scripts,build twice for single js file
        output: {
          entryFileNames: '[name].js',
          chunkFileNames: '[name]-[hash].js',
          assetFileNames: '[name].[extname]',
          format: 'es',
          inlineDynamicImports: !!environment.BUILD_ENTRY,
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
    test: {
      name: 'background',
      environment: 'node',
      setupFiles: ['./tests/chrome.vitest.js'],
      include: [
        'src/test/background.*.{test,spec}.js',
      ],
      exclude: [
        'src/test/content.*.{test,spec}.js',
      ],
      coverage: {
        provider: 'v8', // or 'istanbul'
      },
    },
  }
})
