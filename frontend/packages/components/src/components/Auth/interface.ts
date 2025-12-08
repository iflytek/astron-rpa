import { functionType, stringType } from '../../utils/type'

export type LoginMode = 'account' | 'phone'
export type RegisterMode = 'personal' | 'enterprise'

export interface ForgotPasswordFormData {
  phone: string // 手机号或邮箱
  code: string
}

export interface SetPasswordFormData {
  password: string
  confirmPassword: string
}

export interface TenantItem {
  id: string
  name: string
  type: number // 0-个人版、1-企业版
  memberCount?: number
}

export interface ForgotPasswordFormData {
  phone: string // 手机号或邮箱
  code: string
}

export interface SetPasswordFormData {
  password: string
  confirmPassword: string
}

export interface TenantItem {
  id: string
  name: string
  avatar?: string
  description?: string
  memberCount?: number
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

export interface AccountLoginFormData {
  username: string
  password: string
  remember?: boolean
  agreement?: boolean
}

export interface PhoneLoginFormData {
  phone: string
  code: string
  agreement?: boolean
}

export type LoginFormData = AccountLoginFormData | PhoneLoginFormData

export interface PersonalRegisterFormData {
  username: string
  email?: string
  phone?: string
  code?: string
  password?: string
  confirmPassword?: string
  agreement?: boolean
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
    username: string
    email: string
  }
}

export interface EnterpriseInvitFormData {
  password: string
  confirmPassword: string
  username: string | undefined
}

export function authFormProps() {
  return {
    mode: stringType<'login' | 'register' | 'forgotPassword' | 'setPassword' | 'tenantSelect'>('login'),
    loginMode: stringType<LoginMode>('account'),
    registerMode: stringType<RegisterMode>('personal'),
    title: String,
    onLogin: functionType<(data: LoginFormData, mode: LoginMode) => void | Promise<void>>(),
    onRegister: functionType<(data: RegisterFormData, mode: RegisterMode) => void | Promise<void>>(),
    onModeChange: functionType<(mode: 'login' | 'register' | 'forgotPassword' | 'setPassword' | 'tenantSelect') => void>(),
    onLoginModeChange: functionType<(mode: LoginMode) => void>(),
    onRegisterModeChange: functionType<(mode: RegisterMode) => void>(),
    onSendCode: functionType<(phone: string) => void | Promise<void>>(),
    onForgotPassword: functionType<(data: ForgotPasswordFormData) => void | Promise<void>>(),
    onSetPassword: functionType<(data: SetPasswordFormData) => void | Promise<void>>(),
    onTenantSelect: functionType<(tenantId: string) => void | Promise<void>>(),
  }
}

export function loginProps() {
  return {
    loginBtnText: { type: String, default: '登录' },
    loading: { type: Boolean, default: false },
    prefixCls: { type: String, default: 'auth-login' },
    mode: stringType<LoginMode>('account'),
    onSubmit: functionType<(data: LoginFormData, mode: LoginMode) => void | Promise<void>>(),
    onSwitchToRegister: functionType<() => void>(),
    onModeChange: functionType<(mode: LoginMode) => void>(),
    onSendCode: functionType<(phone: string) => void | Promise<void>>(),
  }
}

export function registerProps() {
  return {
    loading: { type: Boolean, default: false },
    registerBtnText: { type: String, default: '注册' },
    prefixCls: { type: String, default: 'auth-register' },
    mode: stringType<RegisterMode>('personal'),
    onSubmit: functionType<(data: RegisterFormData, mode: RegisterMode) => void | Promise<void>>(),
    onSwitchToLogin: functionType<() => void>(),
    onModeChange: functionType<(mode: RegisterMode) => void>(),
  }
}

export function personalRegisterProps() {
  return {
    loading: { type: Boolean, default: false },
    prefixCls: { type: String, default: 'auth-register-personal' },
    onSubmit: functionType<(data: PersonalRegisterFormData) => void | Promise<void>>(),
    onSwitchToLogin: functionType<() => void>(),
  }
}

export function enterpriseRegisterProps() {
  return {
    loading: { type: Boolean, default: false },
    prefixCls: { type: String, default: 'auth-register-enterprise' },
    onSubmit: functionType<(data: EnterpriseRegisterFormData) => void | Promise<void>>(),
    onSwitchToLogin: functionType<() => void>(),
  }
}

export function forgotPasswordProps() {
  return {
    loading: { type: Boolean, default: false },
    prefixCls: { type: String, default: 'auth-forgot-password' },
    onSubmit: functionType<(data: ForgotPasswordFormData) => void | Promise<void>>(),
    onSwitchToLogin: functionType<() => void>(),
    onSendCode: functionType<(account: string) => void | Promise<void>>(),
  }
}

export function setPasswordProps() {
  return {
    loading: { type: Boolean, default: false },
    prefixCls: { type: String, default: 'auth-set-password' },
    onSubmit: functionType<(data: SetPasswordFormData) => void | Promise<void>>(),
    onSwitchToLogin: functionType<() => void>(),
  }
}

export function tenantSelectProps() {
  return {
    loading: { type: Boolean, default: false },
    prefixCls: { type: String, default: 'auth-tenant-select' },
    tenants: { type: Array as () => TenantItem[], default: () => [] },
    onSubmit: functionType<(tenantId: string) => void | Promise<void>>(),
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
