import type { UpdateInfo } from '@rpa/shared/platform'

async function checkUpdate(): Promise<UpdateInfo> {
  console.warn('electron checkUpdate not implemented')
  return {
    shouldUpdate: false,
    manifest: null,
  }
}

async function installUpdate(_progressCallback: (percent: number) => void) {
  console.warn('electron installUpdate not implemented')
}

const UpdaterManager = {
  checkUpdate,
  installUpdate,
}

export default UpdaterManager
