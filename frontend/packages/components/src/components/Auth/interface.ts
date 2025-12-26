export type Platform = 'client' | 'admin'
export type Edition = 'saas' | 'enterprise'
export type AuthType = 'uap' | 'casdoor'
export type LoginMode = 'PASSWORD' | 'CODE'
export type RegisterMode = 'PERSONAL' | 'ENTERPRISE'
export type AuthFormMode = 'login' | 'register' | 'forgotPassword' | 'setPassword' | 'tenantSelect' | 'forgotPasswordWithSysUpgrade' | 'setPasswordWithSysUpgrade' | 'modifyPassword'
export type AsyncAction = 'IDLE' | 'PASSWORD' | 'CODE' | 'PERSONAL' | 'ENTERPRISE' | 'FORGOT_PASSWORD' | 'SET_PASSWORD' | 'MODIFY_PASSWORD' | 'CHOOSE_TENANT'

export interface LoginFormData {
  loginName?: string
  password?: string
  remember?: boolean
  agreement?: boolean
  phone?: string,
  captcha?: string,
  loginType?: "CODE" | "PASSWORD",
  tenantId?: string
  confirmPassword?: string
  oldPassword?: string
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
  expiredDate?: string
  isDelete?: number
  isDefaultTenant?: number
  createTime?: string
  updateTime?: string
}

export interface InviteInfo {
  linkExpired?: boolean
  isJoined?: boolean
  isLimit?: boolean
  inviteType?: 'market' | 'enterprise'
  userId: string
  userName: string
  marketId?: string
  marketName?: string
  enterpriseId?: string
  enterpriseName?: string
}

export interface PersonalRegisterFormData {
  loginName: string
  phone?: string
  captcha?: string
  password?: string
  confirmPassword?: string
  agreement?: boolean
  code?: string
}

export interface EnterpriseRegisterFormData {
  contactName: string
  companyName: string
  teamSize: string | undefined | number
  email: string
  phone: string
  agreement?: boolean
}

export type RegisterFormData = PersonalRegisterFormData | EnterpriseRegisterFormData
