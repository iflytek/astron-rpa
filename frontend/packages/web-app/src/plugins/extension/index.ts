import { getExtensions, initializePluginManager, loadPlugins } from './utils'

export let extensions: ReturnType<typeof getExtensions> = null

const init = async () => {
  await initializePluginManager()
  await loadPlugins()

  extensions = getExtensions()
}

init()
