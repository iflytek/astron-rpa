import type { UpdateInfo, UpdaterManager as UpdaterManagerType } from '@rpa/shared/platform'

const { ipcRenderer } = window.electron

async function checkUpdate(): Promise<UpdateInfo> {
  return await ipcRenderer.invoke('check-for-updates')
}

async function installUpdate(_progressCallback: (percent: number) => void) {
  ipcRenderer.send('quit-and-install-updates')
}

const UpdaterManager: UpdaterManagerType = {
  checkUpdate,
  installUpdate,
}

export default UpdaterManager
