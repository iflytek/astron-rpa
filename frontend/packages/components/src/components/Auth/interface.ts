export type Platform = 'client' | 'admin'
export type Edition = 'saas' | 'enterprise'
export type AuthType = 'uap' | 'casdoor'
export type LoginMode = 'PASSWORD' | 'CODE'
export type RegisterMode = 'REGISTER' | 'CONSULT'
export type AuthFormMode = 'login' | 'register' | 'forgotPassword' | 'setPassword' | 'tenantSelect' | 'forgotPasswordWithSysUpgrade' | 'setPasswordWithSysUpgrade' | 'modifyPassword'
export type AsyncAction = 'IDLE' | 'PASSWORD' | 'CODE' | 'REGISTER' | 'CONSULT' | 'FORGOT_PASSWORD' | 'SET_PASSWORD' | 'MODIFY_PASSWORD' | 'CHOOSE_TENANT'

export interface LoginFormData {
  loginName?: string
  password?: string
  remember?: boolean
  agreement?: boolean
  phone?: string
  captcha?: string
  loginType?: 'CODE' | 'PASSWORD'
  tenantId?: string
  confirmPassword?: string
  oldPassword?: string
  newPassword?: string
}

export interface TenantItem {
  id: string
  name: string
  description?: string
  memberCount?: number
  tenantCode: string
  tenantType: 'personal' | 'professional' | 'enterprise'
  status: number
  remark?: string
  creator?: string
  isExpired?: boolean
  shouldAlert?: boolean
  expiredDate?: string
  expirationDate?: string
  remainingDays: number
  isDelete?: number
  isDefaultTenant?: number
  createTime?: string
  updateTime?: string
}

export type InviteCode = '000' | '001' | '101' | '102' | '100' | '' // "000"-成功 "001"-重复加入 "101"-超出上限 "102"-链接失效 "100"-市场人数已满
export interface InviteInfo {
  resultCode?: InviteCode
  inviteType?: 'market' | 'enterprise'
  inviterName: string
  marketName?: string
  enterpriseName?: string
}

export interface RegisterFormData {
  loginName: string
  phone?: string
  captcha?: string
  password?: string
  confirmPassword?: string
  agreement?: boolean
  code?: string
}

export interface ConsultFormData {
  contactName: string
  companyName: string
  teamSize: string | undefined | number
  email: string
  mobile: string
  agreement?: boolean
  renewalDuration?: string
  formType?: number
}
