/**
 * 积分弹层等 Header 区域使用的租户套餐（文案与 Consult 等处可各自维护，改弹层只改本文件即可）
 */
export const TENANT_EDITION = {
  Personal: 'personal',
  Professional: 'professional',
  Enterprise: 'enterprise',
} as const

export type TenantEditionKey = (typeof TENANT_EDITION)[keyof typeof TENANT_EDITION]

export const TENANT_EDITION_LABEL: Record<TenantEditionKey, string> = {
  personal: '免费版',
  professional: '专业版',
  enterprise: '企业版',
}
