import { NiceModal } from '@rpa/components'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { onBeforeMount, ref } from 'vue'

import { browerPluginInstall, checkBrowerRunning, installAllUpdateBrowerPlugin } from '@/api/plugin'
import GlobalModal from '@/components/GlobalModal/index.ts'
import type { PLUGIN_ITEM } from '@/constants/plugin'
import { BROWER_LIST } from '@/constants/plugin'
import { useAppConfigStore } from '@/stores/useAppConfig'

import _PluginTipModal from '../PluginTipModal.vue'
import _PluginUpdateModal from '../pluginUpdateModal.vue'
import { storage } from '@/utils/storage'

const PluginTipModal = NiceModal.create(_PluginTipModal)
const PluginUpdateModal = NiceModal.create(_PluginUpdateModal)

export function useBrowerPlugin() {
  const appConfigStore = useAppConfigStore()
  const pluginList = ref(appConfigStore.browserPlugins)
  const { t } = useTranslation()

  onBeforeMount(() => {
    appConfigStore.refreshBrowserPluginStatus()
  })

  // 强制关闭浏览器，再重新安装
  const killBrowerReinstall = (pluginItem: PLUGIN_ITEM) => {
    const type = pluginItem.isNewest ? '安装' : '更新'
    const modelConf = {
      title: '提示',
      zIndex: 100,
      content: `${t(pluginItem.title)}正在运行(后台进程可能存在)，请关闭浏览器后再${type}插件`,
      okText: '强制关闭',
      cancelText: '取消',
      onOk: () => {
        installBrowerPlugin(pluginItem, 'brower_install_killBrower')
      },
      centered: true,
      keyboard: false,
    }

    GlobalModal.confirm(modelConf)
  }

  // 安装成功提示, 并展示开启插件步骤的弹窗
  const successTipOpenStep = (pluginItem: PLUGIN_ITEM) => {
    pluginItem.isInstall = true
    pluginItem.isNewest = true

    if (pluginItem.oparateStepImgs?.length > 0) {
      NiceModal.show(PluginTipModal, {
        stepImgs: pluginItem.oparateStepImgs,
        stepInfo: pluginItem.stepDescription,
      })
      return
    }

    const type = pluginItem.isNewest ? '安装' : '更新'

    GlobalModal.confirm({
      title: '提示',
      zIndex: 100,
      content: `${t(pluginItem.title)}插件${type}成功`,
      okText: '确定',
      cancelText: '取消',
      centered: true,
      keyboard: false,
    })
  }

  // 安装失败提示，并重新安装
  const failTipWithReinstall = (pluginItem: PLUGIN_ITEM) => {
    const type = pluginItem.isInstall ? '更新' : '安装'

    GlobalModal.confirm({
      title: '提示',
      zIndex: 100,
      content: `${t(pluginItem.title)}插件${type}失败，请检查该浏览器是否存在或重新${type}`,
      okText: `重新${type}`,
      okType: 'primary',
      onOk: () => installBrowerPlugin(pluginItem),
      centered: true,
      keyboard: false,
    })
  }

  // 安装
  const install = (pluginItem: PLUGIN_ITEM, action = 'install') => {
    pluginItem.loading = true
    browerPluginInstall({ ...pluginItem, action }).then(
      () => {
        successTipOpenStep(pluginItem)
        pluginItem.isInstall = true
        pluginItem.isNewest = true
      },
    ).catch(() => failTipWithReinstall(pluginItem)).finally(() => {
      pluginItem.loading = false
    })
  }

  // 安装插件
  const installBrowerPlugin = (pluginItem: PLUGIN_ITEM, action: 'install' | 'brower_install_killBrower' = 'install') => {
    switch (pluginItem.type) {
      case BROWER_LIST.CHROME:
      case BROWER_LIST.EDGE:
      case BROWER_LIST.FIREFOX:
      case BROWER_LIST['360SE']:
      case BROWER_LIST['360X']:
        install(pluginItem, action)
        break
      default:
        message.info('敬请期待')
    }
  }

  // 安装前检测浏览器是否运行
  const safeInstallBrowerPlugin = async (pluginItem: PLUGIN_ITEM) => {
    pluginItem.loading = true
    try {
      const { data } = await checkBrowerRunning({ type: pluginItem.type })
      if (data && data.running) {
        pluginItem.loading = false
        killBrowerReinstall(pluginItem)
      }
      else {
        installBrowerPlugin(pluginItem)
      }
    }
    catch (error) {
      console.error('checkBrowerRunning error: ', error)
      // 出错则默认浏览器未运行，直接安装
      installBrowerPlugin(pluginItem)
    }
  }

  // 有更新的插件一键安装
  const pluginUpdateModal = () => {
    const lastUpdateTimestamp = storage.get('browserPluginUpdateTimestamp')
    // 一天内只提示一次
    if (lastUpdateTimestamp && Date.now() - Number(lastUpdateTimestamp) < 24 * 60 * 60 * 1000) {
      return
    }
    appConfigStore.browserPlugins.forEach((plugin) => {
      if (plugin.isInstall && !plugin.isNewest) {
        NiceModal.show(PluginUpdateModal, {}).then(async () => {
          await installAllUpdateBrowerPlugin()
          appConfigStore.refreshBrowserPluginStatus()
        })
        storage.set('browserPluginUpdateTimestamp', Date.now())
      }
    })
  }

  return { pluginList, install: installBrowerPlugin, safeInstallBrowerPlugin, pluginUpdateModal }
}
