import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createRequire } from 'node:module'

const require = createRequire(import.meta.url)
const vueVersion = require('vue/package.json').version
const piniaVersion = require('pinia/package.json').version

import { RpaResolver } from '@rpa/components/resolver'
import { sentryVitePlugin } from '@sentry/vite-plugin'
import type { SentryVitePluginOptions } from '@sentry/vite-plugin'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
// import Inspect from 'vite-plugin-inspect' 开发时查看编译代码
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers'
import Components from 'unplugin-vue-components/vite'
import { defineConfig } from 'vite'
import { analyzer } from 'vite-bundle-analyzer'
import { lazyImport, VxeResolver } from 'vite-plugin-lazy-import'
import PageHtml from 'vite-plugin-page-html'
import { svg4VuePlugin } from 'vite-plugin-svg4vue'

import { ModalReplacementResolver } from './src/plugins/component-resolver'

const baseSrc = fileURLToPath(new URL('./src', import.meta.url))
const basePublic = fileURLToPath(new URL('../../public', import.meta.url))
const nodeModules = fileURLToPath(new URL('./node_modules', import.meta.url))

const sentryConfig: SentryVitePluginOptions = {
  authToken: process.env.SENTRY_AUTH_TOKEN,
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
  url: process.env.SENTRY_URL,
}

// https://vitejs.dev/config/
export default defineConfig((env) => {
  const isPublish = env.mode === 'publish'
  const isDebug = env.mode === 'debug'

  const enableAnalyze = env.mode === 'analyze'
  const enableSentry = isPublish && sentryConfig.authToken && sentryConfig.org && sentryConfig.project

  return {
    publicDir: basePublic,
    define: {
      __VUE_VERSION__: JSON.stringify(vueVersion),
      __PINIA_VERSION__: JSON.stringify(piniaVersion),
    },
    build: {
      sourcemap: isDebug ? 'inline' : isPublish,
      minify: 'oxc',
    },
    plugins: [
      vue(),
      vueJsx(),
      svg4VuePlugin({ 
        assetsDirName: false,
        svgoConfig: false,
      }),
      // Inspect(),
      Components({
        dirs: [],
        dts: './src/components.d.ts',
        resolvers: [
          ModalReplacementResolver(), // 优先级最高，用于替换 a-modal
          AntDesignVueResolver({
            importStyle: false, // css in js
          }),
          RpaResolver(),
        ],
      }),
      lazyImport({
        resolvers: [
          VxeResolver({
            libraryName: 'vxe-table',
          }),
          VxeResolver({
            libraryName: 'vxe-pc-ui',
          }),
        ],
      }),
      PageHtml({
        template: 'src/index.html',
        page: { // Note: paths here must be absolute from project root, starting with '/src/...'
          index: '/src/views/Home/index.ts',
          boot: '/src/views/Boot/index.ts',
          logwin: '/src/views/Log/index.ts',
          batch: '/src/views/Batch/index.ts',
          multichat: '/src/views/MultiChat/index.ts',
          userform: '/src/views/UserForm/index.ts',
          record: '/src/views/Record/index.ts',
          recordmenu: '/src/views/RecordMenu/index.ts',
          smartcompickmenu: '/src/views/SmartCompPickMenu/index.ts'
        }
      }),
      enableSentry ? sentryVitePlugin(sentryConfig) : null,
      enableAnalyze ? analyzer() : null,
    ],
    resolve: {
      alias: [
        {
          find: '@',
          replacement: baseSrc,
        },
        {
          find: 'dayjs',
          replacement: 'dayjs/esm',
        },
        {
          find: /^dayjs\/locale/,
          replacement: 'dayjs/esm/locale',
        },
        {
          find: /^dayjs\/plugin/,
          replacement: 'dayjs/esm/plugin',
        },
        {
          find: /^ant-design-vue\/es$/,
          replacement: resolve(nodeModules, 'ant-design-vue/es'),
        },
        {
          find: /^ant-design-vue\/dist$/,
          replacement: resolve(nodeModules, 'ant-design-vue/dist'),
        },
        {
          find: /^ant-design-vue\/lib$/,
          replacement: resolve(nodeModules, 'ant-design-vue/es'),
        },
        {
          find: /^ant-design-vue$/,
          replacement: resolve(nodeModules, 'ant-design-vue/es'),
        },
        {
          find: 'lodash',
          replacement: 'lodash-es',
        },
      ],
    },

    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `
            @import "@rpa/shared/tokens/variables.scss";
          `,
        },
      },
    },

    clearScreen: false,
    server: {
      port: 1420,
      strictPort: true,
      host: '0.0.0.0', // 指定监听所有网络接口
      watch: {
        // 3. tell vite to ignore watching `src-tauri`
        ignored: ['**/src-tauri/**', '**/node_modules/**', '**/src-electron/**', '**/dist/**', '**/dist-electron/**'],
      },
    },
  }
})
