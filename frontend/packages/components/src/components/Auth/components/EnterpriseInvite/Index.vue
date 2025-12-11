<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import PhoneLogin from './PhoneLogin.vue'
import FillUserInfo from './FillUserInfo.vue'
import InviteUserInfo from '../Base/InviteUserInfo.vue'
import StatusCard from '../Base/StatusCard.vue'

import type { 
  LoginFormData, 
  LoginMode, 
  RegisterFormData, 
  RegisterMode,
} from '../../interface'

const emit = defineEmits<{
  login: [data: LoginFormData, mode: LoginMode]
  register: [data: RegisterFormData, mode: RegisterMode]
  joinMarket: [marketId: string]
  sendCaptcha: [phone: string]
}>()

// 页面状态管理
type PageStatus = 'checking' | 'linkExpired' | 'needLogin' | 'showUserInfo' | 'fillUserInfo' | 'joinSuccess' | 'alreadyJoined'
const currentStatus = ref<PageStatus>('fillUserInfo')

import type { EnterpriseInviteInfo } from '../../interface'

const inviteInfo = ref<EnterpriseInviteInfo>({
  enterpriseId: '12',
  enterpriseName: '团队企业',
  userId: '用户ID',
  userName: '用户1'
})

// 用户相关状态
const currentUser = ref<{
  name?: string
  phone?: string
} | undefined>({
  name: '张三',
  phone: '138****8888',
})

// 邀请链接状态
const joinLoading = ref(false)

// 检查邀请链接有效性
const checkInviteLink = async () => {
  try {
    // 模拟API调用检查链接有效性
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // if (false) {
    //   currentStatus.value = 'linkExpired'
    //   return
    // }
    
    // 模拟检查邀请码有效性（实际应该调用后端API）
    // checkUserLoginStatus()
    
  } catch (error) {
    currentStatus.value = 'linkExpired'
  }
}

// 检查用户登录状态
const checkUserLoginStatus = async () => {
  try {
    // 模拟检查用户登录状态（实际应该检查token或调用API）
    // const token = localStorage.getItem('authToken')
    
    // if (token) {
      // 模拟获取用户信息
      currentUser.value = {
        name: '张三',
        phone: '138****8888',
      }
      
      // 检查用户是否已经加入该市场
      // await checkJoinStatus()
    // } else {
      currentStatus.value = 'needLogin'
    // }
  } catch (error) {
    currentStatus.value = 'needLogin'
  }
}

// 检查用户是否已加入市场
const checkJoinStatus = async () => {
  try {
    // 模拟检查用户是否已加入市场（实际应该调用API）
    const hasJoined = false // 这里应该通过API检查
    
    if (hasJoined) {
      currentStatus.value = 'alreadyJoined'
    } else {
      currentStatus.value = 'showUserInfo'
    }
  } catch (error) {
    currentStatus.value = 'showUserInfo'
  }
}

// 处理登录成功
const handleLoginSuccess = async (data: LoginFormData, mode: LoginMode) => {
  try {
    emit('login', data, mode)
      // 模拟登录成功后获取用户信息
    currentUser.value = {
      name: '张三',
      phone: (data as LoginFormData).loginName || (data as LoginFormData).phone || '未知',
    }
    
    // 登录成功后检查加入状态
    await checkJoinStatus()
    
  } catch (error) {
    message.error('登录失败，请重试')
  }
}

// 处理注册成功
const handleRegisterSuccess = async (data: RegisterFormData, mode: RegisterMode) => {
  try {
    emit('register', data, mode)    // 注册成功后自动登录
    currentUser.value = {
      name: (data as any).loginName || '用户',
      phone: data.phone || '未知',
    }
    currentStatus.value = 'showUserInfo'
  } catch (error) {
    message.error('注册失败，请重试')
  }
}

// 处理加入企业
const handleJoinEnterprise = async () => {
  joinLoading.value = true
  try {
    // emit('joinMarket')
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    currentStatus.value = 'joinSuccess'
    // currentStatus.value = 'linkExpired'
    message.success('加入市场成功！')
  } catch (error) {
    message.error('加入市场失败，请重试')
  } finally {
    joinLoading.value = false
  }
}

const openApp = () => {

}

const handleBack = () => {

}

// 页面初始化
onMounted(() => {
  checkInviteLink()
})
</script>

<template>
  <div class="auth-container-content invite-container ">   
    <StatusCard v-if="currentStatus === 'linkExpired'"
      :title="'邀请链接已失效'"
      :desc="`该邀请链接已失效，请与邀请你的人联系，获得新的链接。`"
     /> 
    <PhoneLogin v-else-if="currentStatus === 'needLogin'" :invite-info="inviteInfo"  />
    <FillUserInfo v-else-if="currentStatus === 'fillUserInfo'" :invite-info="inviteInfo" />
    <InviteUserInfo v-else-if="currentStatus === 'showUserInfo'" 
      :type="'enterprise'" 
      :user-name="inviteInfo.userName" 
      :target-name="inviteInfo.enterpriseName" 
      :current-user="currentUser"
      @back="handleBack"  
      @join-enterprise="handleJoinEnterprise"
    />
    <StatusCard v-else-if="currentStatus === 'joinSuccess'"
      :title="'加入成功！'"
      :desc="`您已加入「${inviteInfo.enterpriseName}」，快进入晓悟RPA，与同事开启协作吧！`"
      :buttonTxt="'进入星辰RPA'"
      @click="openApp"
    />
    <StatusCard v-else-if="currentStatus === 'alreadyJoined'"
      :title="'您已加入该企业'"
      :desc="`您已加入该企业，无需重复加入。<br />登录晓悟RPA并进入该企业，即可与同事开启协作。`"
      :buttonTxt="'进入星辰RPA'"
      @click="openApp"
    />
  </div>
</template>
