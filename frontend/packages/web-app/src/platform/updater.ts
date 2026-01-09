import type { UpdaterManager as UpdaterManagerType } from '@rpa/shared/platform'

const checkUpdate: UpdaterManagerType['checkUpdate'] = async () => {
  console.warn('checkUpdate not implemented')
  return {
    couldUpdate: false,
    downloaded: false,
    manifest: null,
  }
}

const quitAndInstall: UpdaterManagerType['quitAndInstall'] = () => {
  console.warn('quitAndInstall not implemented')
  return Promise.resolve()
}

const UpdaterManager: UpdaterManagerType = {
  checkUpdate,
  quitAndInstall,
}

export default UpdaterManager
