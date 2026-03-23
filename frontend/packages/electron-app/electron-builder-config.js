const path = require('node:path')
const fs = require('node:fs')
const { platformFolder, knownPlatformDirs } = require('@rpa/shared/platform')

const resourcesRoot = path.resolve(__dirname, '../../../resources')

function createExtraFiles() {
  const rootOnlyFilter = [
    '**/*',
    ...knownPlatformDirs.map(dir => `!${dir}{,/**}`),
  ]

  if (!platformFolder) {
    throw new Error(`[electron-builder-config] Unsupported build target: ${platformFolder}`)
  }

  const platformDirPath = path.join(resourcesRoot, platformFolder)
  if (!fs.existsSync(platformDirPath)) {
    throw new Error(`[electron-builder-config] Missing resources folder: ${platformDirPath}`)
  }

  return [
    {
      from: resourcesRoot,
      to: 'resources',
      filter: rootOnlyFilter,
    },
    {
      from: platformDirPath,
      to: 'resources',
    },
  ]
}

/**
* @type {import('electron-builder').Configuration}
* @see https://www.electron.build/configuration
*/
const config = {
  appId: 'astron-rpa',
  productName: 'astron-rpa',
  artifactName: '星辰RPA-${version}-${arch}.${ext}',
  electronLanguages: ['zh-CN', 'en-US'],
  asar: false,
  files: ['node_modules/**', 'out/**', 'extensions/**', 'package.json'],
  extraFiles: createExtraFiles(),
  win: {
    target: 'nsis',
    icon: '../../public/icons/icon.ico',
    publisherName: 'astron-rpa',
    verifyUpdateCodeSignature: false,
    publish: {
      provider: 'generic',
      url: '',
    },
  },
  mac: {
    target: 'dmg',
    icon: '../../public/icons/icon.png',
    extendInfo: {
      CFBundleURLTypes: [
        {
          CFBundleURLName: 'com.iflytek.astronrpa',
          CFBundleURLSchemes: ['astronrpa'],
        },
      ],
    },
  },
  linux: {
    target: 'deb',
    icon: '../../public/icons/icon.png',
    category: 'Utility',
    desktop: {
      MimeType: 'x-scheme-handler/astronrpa;',
    },
  },
  nsis: {
    include: './installer.nsh',
    oneClick: false,
    allowElevation: true,
    allowToChangeInstallationDirectory: true,
    createDesktopShortcut: true,
    createStartMenuShortcut: true,
    shortcutName: '星辰RPA',
  },
}

module.exports = config
