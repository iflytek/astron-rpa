import { functionType, stringType } from '../../utils/type'

export type LoginMode = 'PASSWORD' | 'CODE'
export type RegisterMode = 'PERSONAL' | 'ENTERPRISE'
export type AuthFormMode = 'login' | 'register' | 'forgotPassword' | 'setPassword' | 'tenantSelect' | 'forgotPasswordWithSysUpgrade' | 'setPasswordWithSysUpgrade'
export type AsyncAction = 'IDLE' | 'PASSWORD' | 'CODE' | 'PERSONAL' | 'ENTERPRISE' | 'FORGOT_PASSWORD' | 'SET_PASSWORD' | 'CHOOSE_TENANT'
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
  isDelete?: number
  isDefaultTenant?: number
  createTime?: string
  updateTime?: string
}

export interface MarketInviteInfo {
  userId: string
  userName: string
  marketId: string
  marketName: string
}

export interface EnterpriseInviteInfo {
  userId: string
  userName: string
  enterpriseId: string
  enterpriseName: string
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

export interface AuthResponse {
  token: string
  user: {
    id: string
    loginName: string
    email: string
  }
}

export interface EnterpriseInvitFormData {
  password: string
  confirmPassword: string
  loginName: string | undefined
}

export function loginProps() {
  return {
    loading: { type: Boolean, default: false },
    mode: stringType<LoginMode>('PASSWORD'),
    onSubmit: functionType<(data: LoginFormData, mode: LoginMode) => void | Promise<void>>(),
    onSwitchToRegister: functionType<() => void>(),
    onModeChange: functionType<(mode: LoginMode) => void>(),
    onSendCode: functionType<(phone: string) => void | Promise<void>>(),
  }
}

export function registerProps() {
  return {
    loading: { type: Boolean, default: false },
    mode: stringType<RegisterMode>('PERSONAL'),
    onSubmit: functionType<(data: RegisterFormData, mode: RegisterMode) => void | Promise<void>>(),
    onSwitchToLogin: functionType<() => void>(),
    onModeChange: functionType<(mode: RegisterMode) => void>(),
  }
}

export function personalRegisterProps() {
  return {
    loading: { type: Boolean, default: false },
    onSubmit: functionType<(data: PersonalRegisterFormData) => void | Promise<void>>(),
    onSwitchToLogin: functionType<() => void>(),
  }
}

export function enterpriseRegisterProps() {
  return {
    loading: { type: Boolean, default: false },
    onSubmit: functionType<(data: EnterpriseRegisterFormData) => void | Promise<void>>(),
    onSwitchToLogin: functionType<() => void>(),
  }
}

export function forgotPasswordProps() {
  return {
    loading: { type: Boolean, default: false },
    onSubmit: functionType<(data: LoginFormData) => void | Promise<void>>(),
    onSwitchToLogin: functionType<() => void>(),
    onSendCode: functionType<(account: string) => void | Promise<void>>(),
  }
}

export function setPasswordProps() {
  return {
    loading: { type: Boolean, default: false },
    onSubmit: functionType<(data: LoginFormData) => void | Promise<void>>(),
    onSwitchToLogin: functionType<() => void>(),
  }
}

export function marketInviteProps() {
  return {
    inviteInfo: { type: Object as () => MarketInviteInfo, default: () => ({ userId: '', userName: '', marketId: '', marketName: '' }) },
    tenants: { type: Array as () => TenantItem[], default: () => [] },
    onSubmit: functionType<(tenantId: string) => void | Promise<void>>(),
    onSwitchToLogin: functionType<() => void>(),
  }
}

export function enterpriseInviteProps() {
  return {
    inviteInfo: { type: Object as () => EnterpriseInviteInfo, default: () => ({ userId: '', userName: '', enterpriseId: '', enterpriseName: '' }) },
    tenants: { type: Array as () => TenantItem[], default: () => [] },
    onSubmit: functionType<(tenantId: string) => void | Promise<void>>(),
    onSwitchToLogin: functionType<() => void>(),
  }
}
