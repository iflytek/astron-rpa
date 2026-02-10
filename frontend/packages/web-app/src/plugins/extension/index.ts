import { getExtensions, initializePluginManager, loadPlugins } from './utils'

class ExtensionManager {
  public extensions: ReturnType<typeof getExtensions> = null

  constructor() {
    this.init()
  }

  async init() {
    await initializePluginManager()
    await loadPlugins()

    this.extensions = getExtensions()
  }
}

export default new ExtensionManager()
