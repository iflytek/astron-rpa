import type { SegmentedProps } from 'ant-design-vue'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import {
  acceptJoinTeam,
  getNewMessage,
  messageList,
  refuseJoinTeam,
  setAllRead,
  setMessageReadById,
} from '@/api/market'
import { EDITORPAGE, TEAMMARKETS, APPLICATIONMARKET } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { useRoute } from 'vue-router'
import { useMarketStore } from '@/stores/useMarketStore'
import { useProcessStore } from '@/stores/useProcessStore'

import { ALLREADNUM, JOINNUM, NOREADNUM, READNUM, REFUSENUM, TEAMMARKETUPDATE } from '../config'

export function useMessageTip() {
  const processStore = useProcessStore()
  const { t } = useTranslation()
  const route = useRoute()
  let loopTimer = null
  const showMessage = ref(false)
  const messageData = ref([])
  const messageBoxRef = ref(null)
  const page = ref({
    pageNo: 1,
    pageSize: 10,
    total: 0,
    totalPages: 1,
  })
  const hasBadage = ref('0')
  const loading = ref(false) // 用于消息数据节流，防止一直滚动，多次触发请求
  const spinStatus = ref(false) // 用于打开消息列表时，展示spin
  const readType = ref('all')

  const tabs = computed<SegmentedProps['options']>(() => ([
    {
      label: t('settingCenter.message.unreadMessage'),
      value: 'noread',
    },
    {
      label: t('settingCenter.message.allMessage'),
      value: 'all',
    },
  ]))

  function extractBracketContent(messageInfo: string): string {
    if (!messageInfo || typeof messageInfo !== 'string') {
      return ''
    }
    // 使用正则表达式匹配方括号内容
    const regex = /\[([^\]]+)\]/g
    const content = messageInfo.replace(regex, match => `<span class="font-semibold">${match}</span>`)

    return content
  }
  function handleTabChange(value: string) {
    console.log('value++++', value)
    if (value === 'noread') {
      checkNoread()
    }
    else {
      checkAll()
    }
  }

  const getMessageList = () => {
    if (page.value.pageNo > page.value.totalPages)
      return
    const { pageNo, pageSize } = page.value
    // 获取消息列表
    messageList({ pageNo, pageSize }).then((data) => {
      if (data) {
        const { records, pages, total } = data
        page.value.totalPages = pages
        page.value.total = total
        messageData.value = [...messageData.value, ...records]
      }
    }).finally(() => {
      spinStatus.value = false
      loading.value = false
    })
  }

  const scroll = () => {
    const { clientHeight, scrollHeight, scrollTop } = messageBoxRef.value
    if (clientHeight + scrollTop + 60 >= scrollHeight && !loading.value) {
      loading.value = true
      page.value.pageNo++
      getMessageList()
    }
  }

  // 刷新消息
  const refresh = async () => {
    hasBadage.value = await getNewMessage()
  }

  const toastMessage = (data, custom, id?) => {
    if (data)
      message.success('操作成功')
    messageData.value = messageData.value.map((item) => {
      if (item.id === id)
        item.operateResult = custom
      if (custom === ALLREADNUM && item.operateResult === NOREADNUM)
        item.operateResult = READNUM
      return item
    })
  }
  
  const toMarket = (id: string) => {
    useMarketStore().refreshTeamList(id)
    useRoutePush({ name: TEAMMARKETS, query: { marketId: id } })
  }

  // 点击消息
  const readMessage = async ({ operateResult, id, messageType, marketId }) => {
    if (messageType === TEAMMARKETUPDATE) {
      // 编排页面，点击消息，保存编排页面数据，并跳转到对应市场应用
      if (route.name === EDITORPAGE) {
        await processStore.saveProject()
      }
      toMarket(marketId)
      showMessage.value = false
    }
    if (operateResult !== NOREADNUM)
      return
    const data = await setMessageReadById({ notifyId: id })
    toastMessage(data, READNUM, id)
    refresh()
  }

  // 查看未读
  const checkNoread = () => {
    messageData.value = messageData.value.filter(i => i.operateResult === NOREADNUM)
  }

  // 全部消息
  const checkAll = () => {
    messageData.value = []
    getMessageList()
  }

  // 全部已读
  const allRead = async () => {
    const data = await setAllRead()
    toastMessage(data, ALLREADNUM)
    refresh()
  }

  // 加入团队
  const joinTeam = async (id) => {
    const data = await acceptJoinTeam({ notifyId: id })
    toastMessage(data, JOINNUM, id)
    if (route.meta.resource === APPLICATIONMARKET) {
      useMarketStore().refreshTeamList()
    }
  }

  // 拒绝加入团队
  const refuseTeam = async (id) => {
    const data = await refuseJoinTeam({ notifyId: id })
    toastMessage(data, REFUSENUM, id)
  }

  // 打开弹窗，获取消息
  watch(showMessage, (val) => {
    if (val) {
      spinStatus.value = true
      getMessageList()
    }
    else {
      page.value.pageNo = 1
      page.value.totalPages = 1
      messageData.value = []
      spinStatus.value = false
    }
  }, { immediate: true })

  onMounted(() => {
    // 开启轮询 是否有新消息
    loopTimer && clearInterval(loopTimer)
    loopTimer = setInterval(refresh, 20000)
  })

  onBeforeUnmount(() => {
    loopTimer && clearInterval(loopTimer)
  })

  return {
    hasBadage,
    showMessage,
    spinStatus,
    readType,
    tabs,
    handleTabChange,
    messageData,
    messageBoxRef,
    page,
    scroll,
    readMessage,
    checkNoread,
    checkAll,
    allRead,
    joinTeam,
    refuseTeam,
    extractBracketContent,
  }
}
