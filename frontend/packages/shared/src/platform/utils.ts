const argv = process.argv.slice(2)

export const knownPlatformDirs = [
  'win-x64',
  'win-ia32',
  'win-arm64',
  'linux-amd64',
  'linux-arm64',
  'linux-armv7l',
  'mac',
]

function getPlatformFolder(platform: string, arch: string) {
  if (platform === 'darwin') return 'mac'

  if (platform === 'win32') {
    if (arch === 'x64') return 'win-x64'
    if (arch === 'ia32') return 'win-ia32'
    if (arch === 'arm64') return 'win-arm64'
  }

  if (platform === 'linux') {
    if (arch === 'x64') return 'linux-amd64'
    if (arch === 'arm64') return 'linux-arm64'
  }

  return ''
}


function hasFlag(flag: string) {
  return argv.includes(flag)
}

function parsePlatformFromArgv() {
  if (hasFlag('--win')) return 'win32'
  if (hasFlag('--mac')) return 'darwin'
  if (hasFlag('--linux')) return 'linux'
  return process.platform
}

function parseArchFromArgv() {
  if (hasFlag('--ia32')) return 'ia32'
  if (hasFlag('--x64')) return 'x64'
  if (hasFlag('--arm64')) return 'arm64'
  if (hasFlag('--armv7l') || hasFlag('--armv7')) return 'armv7l'
  if (hasFlag('--universal')) return 'universal'
  return process.arch
}

const platform = parsePlatformFromArgv()
const arch = parseArchFromArgv()

/**
 * 平台文件夹名称
 */
export const platformFolder = getPlatformFolder(platform, arch)
