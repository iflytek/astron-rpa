import type { UpdateInfo, UpdaterManager as UpdaterManagerType } from '@rpa/shared/platform'

const { ipcRenderer } = window.electron

async function checkUpdate(): Promise<UpdateInfo> {
  return await ipcRenderer.invoke('check-for-updates')
}

async function quitAndInstall() {
  ipcRenderer.send('quit-and-install-updates')
}

const UpdaterManager: UpdaterManagerType = {
  checkUpdate,
  quitAndInstall,
}

export default UpdaterManager
