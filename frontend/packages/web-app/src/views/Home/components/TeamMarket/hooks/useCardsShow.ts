import { Icon, NiceModal } from '@rpa/components'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed, h, ref } from 'vue'

import { canAchieveApp, deleteApp, getPushHistoryVersions, useApplication } from '@/api/market'
import { useCommonOperate } from '@/views/Home/pages/hooks/useCommonOperate.tsx'

import type { resOption } from '../../../types'
import type { cardAppItem } from '../../../types/market'
import { DeployRobotModal, MarketAchieveModal, VersionPushModal } from '../index'

export function useCardsShow(emits) {
  const { t } = useTranslation()
  const { handleDeleteConfirm, useApplicationConfirm } = useCommonOperate()

  const appDrawerData = ref({
    visible: false,
    data: null,
  })

  function showAppDrawer(item) {
    console.log(item)
    appDrawerData.value = {
      visible: true,
      data: item,
    }
  }

  function closeAppDrawer(data: { appId: string, checkNum: number }) {
    appDrawerData.value = {
      visible: false,
      data: null,
    }
    emits('updateCheckNum', data)
  }

  function handleDeleteApp(item) {
    console.log(item)
    const { appId, marketId } = item
    handleDeleteConfirm(`将要下架：${item.appName}, 下架后将无法恢复，是否仍要下架？`, () => {
      deleteApp({ appId, marketId }).then(() => {
        message.success('下架成功')
        emits('refreshHomeTable')
      })
    })
  }

  async function handleAppAchieve(e: Event, item) {
    e.stopPropagation()
    const { appId, marketId } = item
    let needApplication = false
    let error = false
    try {
      const { data } = await canAchieveApp({ appId, marketId })
      needApplication = data === 0
    }
    catch (e) {
      error = true
      message.error(e?.message)
    }

    if (error)
      return
    // 红色密级和黄色密级但不是可使用部门的人员,需发起使用申请
    if (needApplication) {
      useApplicationConfirm(`当前权限不足，需发起申请批准后方可使用该应用，是否发起使用申请？`, () => {
        useApplication({ appId, marketId }).then(() => {
          message.success('申请已发送')
        }).catch((e) => {
          message.error(e?.message || '申请发送失败')
        })
      })
      return
    }

    getPushHistoryVersions(item).then((res: resOption) => {
      const { data } = res
      NiceModal.show(MarketAchieveModal, {
        record: item,
        versionLst: data,
        onRefresh: () => emits('refreshHomeTable'),
      })
    })
  }

  const menus = computed(() => [
    {
      key: 'deploy',
      label: t('common.deploy'),
      icon: h(Icon, { name: 'deploy' }),
    },
    {
      key: 'push',
      label: t('market.versionPush'),
      icon: h(Icon, { name: 'tools-publish' }),
    },
    {
      key: 'delete',
      label: t('unpublish'),
      icon: h(Icon, { name: 'market-del' }),
    },
  ],
  )

  function handleAppDeploy(cardItem: cardAppItem) {
    NiceModal.show(DeployRobotModal, { record: cardItem })
  }

  function handleAppPush(cardItem: cardAppItem) {
    NiceModal.show(VersionPushModal, { record: cardItem })
  }

  function menuItemClick(key, cardItem) {
    switch (key) {
      case 'deploy':
        handleAppDeploy(cardItem)
        break
      case 'push':
        handleAppPush(cardItem)
        break
      case 'delete':
        handleDeleteApp(cardItem)
        break
      default:
        break
    }
  }
  return {
    appDrawerData,
    showAppDrawer,
    closeAppDrawer,
    handleAppAchieve,
    menus,
    menuItemClick,
  }
}
