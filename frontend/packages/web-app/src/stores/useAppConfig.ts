import { useAsyncState, watchOnce, useLocalStorage } from '@vueuse/core'
import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'
import { parse } from 'yaml'
import type { UpdateInfo } from '@rpa/shared/platform'
import { NiceModal } from '@rpa/components'

import { checkBrowerPlugin, getSupportBrowser } from '@/api/plugin'
import type { PLUGIN_ITEM } from '@/constants/plugin'
import { BROWER_PLUGIN_LIST } from '@/constants/plugin'
import { updaterManager, utilsManager } from '@/platform'
import { UpdaterModal } from '@/components/Updater'
import { CLOSE_UPDATE_MODAL_VERSION } from '@/constants'

const ENV = import.meta.env

interface UpdaterState extends UpdateInfo {
  checkLoading: boolean, // 检查更新loading
}

// app config 信息
export const useAppConfigStore = defineStore('appConfig', () => {
  // 关闭更新提示弹窗的版本号
  const closeUpdateModalVersion = useLocalStorage<string[]>(CLOSE_UPDATE_MODAL_VERSION, [])

  const updaterState = reactive<UpdaterState>({
    couldUpdate: false, // 是否需要更新
    downloaded: false, // 是否下载完成
    manifest: null, // 最新版本
    checkLoading: false, // 检查更新loading
  })

  // 当前版本
  const { state: appVersion } = useAsyncState<string>(utilsManager.getAppVersion, '')
  // 安装路径
  const { state: appPath } = useAsyncState<string>(utilsManager.getAppPath, '')
  // 构建版本
  const { state: buildInfo } = useAsyncState<string>(utilsManager.getBuildInfo, '')
  // 系统环境
  const { state: systemInfo } = useAsyncState<string>(utilsManager.getSystemEnv, '')
  // 用户目录
  const { state: userPath } = useAsyncState<string>(utilsManager.getUserPath, '')
  const { state: resourcePath } = useAsyncState<string>(utilsManager.getResourcePath, '')

  const { state: yamlData, execute } = useAsyncState(
    async () => {
      const path = resourcePath.value
      if (!path)
        return {}
      const yamlContent  = await utilsManager.readFile(`conf.yaml`, `${path}`)
      return parse(yamlContent)
    },
    {},
    { immediate: true, resetOnExecute: false },
  )

  watchOnce(resourcePath, () => execute())

  const updateBrowserPluginStatus = async (plugins: PLUGIN_ITEM[]) => {
    if (plugins.length === 0)
      return plugins

    // 查询浏览器插件并修改pluginList中相应浏览器插件的状态--isInstall和IsNewest
    const { data } = await checkBrowerPlugin(plugins.map(it => it.type))
    return plugins.map((it) => {
      const target = data[it.type]

      if (!target)
        return it

      return {
        ...it,
        isInstall: target.installed,
        isNewest: target.latest,
        installVersion: target.installed_version,
      }
    })
  }

  // 浏览器插件列表
  const { state: browserPlugins } = useAsyncState<PLUGIN_ITEM[]>(async () => {
    const browser = await getSupportBrowser()
    const plugins = BROWER_PLUGIN_LIST.filter(it => browser.includes(it.type))
    return updateBrowserPluginStatus(plugins)
  }, [])

  // 刷新浏览器插件状态
  const refreshBrowserPluginStatus = async () => {
    if (browserPlugins.value.length > 0) {
      browserPlugins.value = await updateBrowserPluginStatus(browserPlugins.value)
    }
  }

  const appInfo = computed(() => ({
    appEdition: ['saas', 'enterprise'].includes(yamlData.value.app_edition) ? yamlData.value.app_edition : (ENV.VITE_EDITION || 'saas'),
    appAuthType: ['casdoor', 'uap'].includes(yamlData.value.app_auth_type) ? yamlData.value.app_auth_type : (ENV.VITE_AUTH_TYPE || 'casdoor'),
    appVersion: appVersion.value,
    appPath: appPath.value,
    buildInfo: buildInfo.value,
    systemInfo: systemInfo.value,
    userPath: userPath.value,
    remotePath: yamlData.value.remote_addr,
  }))

  /**
   * 检查更新
   * @param manualCheck 是否手动检查更新
   * @returns 
   */
  const checkUpdate = async (manualCheck = false) => {
    if (updaterState.checkLoading)
      return

    updaterState.checkLoading = true
    const { couldUpdate, downloaded, manifest = null } = await updaterManager.checkUpdate()

    updaterState.checkLoading = false
    updaterState.couldUpdate = couldUpdate
    updaterState.downloaded = downloaded
    updaterState.manifest = manifest

    manualCheck && showUpdaterModal()
  }

  const quitAndInstall = async () => {
    updaterManager.quitAndInstall()
  }

  const showUpdaterModal = () => {
    const needUpdate = updaterState.couldUpdate && updaterState.downloaded;
    const latestVersion = needUpdate ? updaterState.manifest?.version : appInfo.value.appVersion

    NiceModal.show(UpdaterModal, {
      needUpdate,
      latestVersion: latestVersion || appInfo.value.appVersion,
      updateNote: updaterState.manifest?.body,
    })
  }

  const onUpdaterDownloaded = () => {
    updaterState.downloaded = true

    // 下载完成后，如果新的版本已经被拒绝更新，则不提示
    if (closeUpdateModalVersion.value.includes(updaterState.manifest?.version)) {
      console.log('新的版本已经被拒绝更新，不提示')
      return
    }

    showUpdaterModal()
  }

  // 拒绝更新
  const rejectUpdate = (version: string) => {
    closeUpdateModalVersion.value.push(version)
  }

  return {
    browserPlugins,
    appInfo,
    updaterState,
    checkUpdate,
    quitAndInstall,
    showUpdaterModal,
    rejectUpdate,
    refreshBrowserPluginStatus,
    onUpdaterDownloaded,
  }
})
