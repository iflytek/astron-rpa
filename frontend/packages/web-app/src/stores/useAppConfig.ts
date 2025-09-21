import type { BasicColorMode } from '@vueuse/core'
import { useAsyncState, useColorMode } from '@vueuse/core'
import { useTranslation } from 'i18next-vue'
import { defineStore } from 'pinia'
import { computed, h, reactive } from 'vue'

import { checkBrowerPlugin, getSupportBrowser } from '@/api/plugin'
import GlobalModal from '@/components/GlobalModal/index.ts'
import type { PLUGIN_ITEM } from '@/constants/plugin'
import { BROWER_PLUGIN_LIST } from '@/constants/plugin'
import { updaterManager, utilsManager } from '@/platform'

// app config 信息
export const useAppConfigStore = defineStore('appConfig', () => {
  let updateModal: ReturnType<typeof GlobalModal.confirm> = null

  const colorMode = useColorMode({ emitAuto: true, initialValue: 'light' })
  const { t } = useTranslation()
  const updaterState = reactive({
    shouldUpdate: false, // 是否需要更新
    manifest: null as any, // 最新版本
    checkLoading: false, // 检查更新loading
    progress: 0, // 下载进度
    installLoading: false, // 安装更新loading
  })

  const colorTheme = computed<BasicColorMode>(() => {
    return colorMode.value === 'auto' ? colorMode.system.value : colorMode.value
  })

  const isDark = computed(() => colorTheme.value === 'dark')

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
    appVersion: appVersion.value,
    appPath: appPath.value,
    buildInfo: buildInfo.value,
    systemInfo: systemInfo.value,
    userPath: userPath.value,
  }))

  const setColorMode = (theme: BasicColorMode) => {
    colorMode.value = theme
  }

  const checkUpdate = async () => {
    if (updaterState.checkLoading)
      return

    updaterState.checkLoading = true
    const { shouldUpdate, manifest = null } = await updaterManager.checkUpdate()
    updaterState.checkLoading = false

    updaterState.shouldUpdate = shouldUpdate
    updaterState.manifest = manifest

    installUpdate()
  }

  const installUpdate = async () => {
    if (updateModal || !updaterState.shouldUpdate)
      return

    updateModal = GlobalModal.confirm({
      title: '有新版本可更新！',
      content: h('div', [
        h('div', `${t('app')} ${updaterState.manifest?.version} 可更新（已安装版本 ${appInfo.value.appVersion}）。`),
        h('div', '立即下载并安装？'),
      ]),
      onOk: async () => {
        updaterState.installLoading = true
        await updaterManager.installUpdate(percent => (updaterState.progress = percent))
      },
      afterClose: () => {
        updateModal.destroy()
        updateModal = null
      },
      centered: true,
      keyboard: false,
    })
  }

  return {
    colorMode: colorMode.store,
    colorTheme,
    isDark,
    browserPlugins,
    appInfo,
    updaterState,
    setColorMode,
    checkUpdate,
    installUpdate,
    refreshBrowserPluginStatus,
  }
})
