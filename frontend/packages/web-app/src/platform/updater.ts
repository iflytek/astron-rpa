import type { UpdaterManager as UpdaterManagerType } from '@rpa/types'

const checkUpdate: UpdaterManagerType['checkUpdate'] = async () => {
  console.warn('checkUpdate not implemented')
  return {
    shouldUpdate: false,
    manifest: null,
  }
}

const installUpdate: UpdaterManagerType['installUpdate'] = (_progressCallback) => {
  console.warn('installUpdate not implemented')
  return Promise.resolve()
}

const UpdaterManager: UpdaterManagerType = {
  checkUpdate,
  installUpdate,
}

export default UpdaterManager
