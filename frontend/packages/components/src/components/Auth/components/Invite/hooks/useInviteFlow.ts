import { useMediaQuery } from '@vueuse/core'
import { Modal } from 'ant-design-vue'
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { acceptEnterpriseInvite, acceptMarketInvite, queryEnterpriseInviteData, queryMarketInviteData } from '../../../api/invite'
import { loginStatus, userInfo } from '../../../api/login'
import type { InviteInfo } from '../../../interface'

type PageStatus = 'init' | 'linkExpired' | 'needLogin' | 'showUserInfo' | 'joinSuccess' | 'joined' | 'reachLimited' | 'marketFull'

export function useInviteFlow(emits: { (e: 'joinSuccess'): void }) {
  const isMobile = useMediaQuery('(max-width: 768px)')
  const route = useRoute()
  const inviteKey = ref(route.query.inviteKey as string)
  const currentStatus = ref<PageStatus>()
  const inviteInfo = ref<InviteInfo>({
    resultCode: '',
    inviteType: (route.query.inviteType || 'market') as 'market' | 'enterprise',
    deptName: '',
    marketName: '',
    inviterName: '',
  })
  const currentUser = ref<{ userName: string, phone: string }>({ userName: '', phone: '' })

  const switchPage = (status: PageStatus) => {
    currentStatus.value = status
  }

  const updateInviteInfo = async (data: InviteInfo, needLogin = true) => {
    inviteInfo.value = { ...inviteInfo.value, ...data }
    let pageStatus: PageStatus = 'needLogin'
    switch (data.resultCode) {
      case '101':
        pageStatus = 'reachLimited'
        break
      case '102':
        pageStatus = 'linkExpired'
        break
      case '100':
        pageStatus = 'marketFull'
        break
      case '001':
        pageStatus = 'joined'
        break
      case '000':
        pageStatus = 'joinSuccess'
        emits('joinSuccess')
        break
      default:
        break
    }
    if (pageStatus !== 'needLogin') {
      switchPage(pageStatus)
      return
    }
    if (needLogin)
      login()
  }

  const login = async () => {
    const isLogin = await loginStatus()
    if (!isLogin) {
      switchPage('needLogin')
      return
    }
    const user = await userInfo()
    currentUser.value = user
    switchPage('showUserInfo')
  }

  const getInviteInfo = async () => {
    if (!inviteKey.value) {
      switchPage('linkExpired')
      return
    }
    try {
      const func = inviteInfo.value.inviteType === 'market' ? queryMarketInviteData : queryEnterpriseInviteData
      const data = await func({ inviteKey: inviteKey.value })
      const needLogin = !isMobile.value
      updateInviteInfo(data, needLogin)
      if (isMobile.value) {
        switchPage('init')
      }
    }
    catch (e) {
      console.error('获取邀请信息失败', e)
      switchPage('linkExpired')
    }
  }

  const toJoin = async () => {
    try {
      const func = inviteInfo.value.inviteType === 'market' ? acceptMarketInvite : acceptEnterpriseInvite
      const data = await func({ inviteKey: inviteKey.value })
      updateInviteInfo(data, false)
    }
    catch (e) {
      console.error('加入失败', e)
    }
  }

  const tryOpenApp = (scheme: string, timeout = 2000) => {
    const start = Date.now()
    const clear: () => void = () => {
      clearTimeout(timer)
      window.removeEventListener('blur', clear)
    }
    window.addEventListener('blur', clear)

    window.location.href = scheme

    const timer = setTimeout(() => {
      if (Date.now() - start >= timeout + 100)
        return

      Modal.warn({
        title: '安装提示',
        content: '您当前未安装星辰RPA应用，是否前往下载？',
        okText: '去下载',
        onOk() {
          window.open('https://www.iflyrpa.com', '_blank')
        },
      })
    }, timeout)
  }

  const openApp = () => {
    tryOpenApp('astronrpa://')
  }

  watch(() => route.query, (val) => {
    if (val.inviteKey && val.inviteKey !== inviteKey.value) {
      inviteKey.value = val.inviteKey as string
      inviteInfo.value = {
        ...inviteInfo.value,
        inviteType: (val.inviteType || 'market') as 'market' | 'enterprise',
      }
      getInviteInfo()
    }
  })

  getInviteInfo()

  return {
    currentStatus,
    inviteInfo,
    currentUser,
    switchPage,
    login,
    toJoin,
    openApp,
  }
}
