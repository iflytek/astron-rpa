import { Modal } from 'ant-design-vue'
import { ref } from 'vue'

import { acceptInvite, queryInviteData } from '../../../api/invite'
import { loginStatus, userInfo } from '../../../api/login'
import type { InviteInfo } from '../../../interface'
import { getQuery } from '../../../utils/index'

type PageStatus = 'linkExpired' | 'needLogin' | 'showUserInfo' | 'joinSuccess' | 'joined' | 'reachLimited' | 'marketFull'

export function useInviteFlow(emits: { (e: 'joinSuccess'): void }) {
  const inviteKey = getQuery().inviteKey as string
  const currentStatus = ref<PageStatus>()
  const inviteInfo = ref<InviteInfo>({
    resultCode: '',
    inviteType: 'market',
    enterpriseName: '',
    marketName: '',
    inviterName: '',
  })
  const currentUser = ref<{ userName: string, phone: string }>({ userName: '', phone: '' })

  const switchPage = (status: PageStatus) => {
    currentStatus.value = status
  }

  const updateInviteInfo = async (data: InviteInfo, needLogin = true) => {
    inviteInfo.value = { ...data, inviteType: data.inviteType || 'market' }
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
    if (needLogin) {
      const isLogin = await loginStatus()
      if (!isLogin) {
        switchPage('needLogin')
        return
      }
      const user = await userInfo()
      currentUser.value = user
      switchPage('showUserInfo')
    }
  }

  const getInviteInfo = async () => {
    if (!inviteKey) {
      switchPage('linkExpired')
      return
    }
    try {
      const data = await queryInviteData({ inviteKey })
      updateInviteInfo(data)
    }
    catch (e) {
      console.error('获取邀请信息失败', e)
      switchPage('linkExpired')
    }
  }

  const switchToLogin = () => {
    switchPage('needLogin')
  }

  const toJoin = async () => {
    try {
      const data = await acceptInvite({ inviteKey })
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

  getInviteInfo()

  return {
    currentStatus,
    inviteInfo,
    currentUser,
    switchToLogin,
    toJoin,
    openApp,
  }
}
