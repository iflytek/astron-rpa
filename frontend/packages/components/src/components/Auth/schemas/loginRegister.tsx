import { Button, Checkbox } from 'ant-design-vue'

import { sendCaptcha } from '../api/login'

import { fieldFactories } from './factories'
import type { FormConfig } from './factories'

/**
 * 登录注册相关表单配置
 */

// 账号登录表单配置
export function accountLoginFormConfig(isInvite = false, edition = 'saas', authType = 'uap'): FormConfig | null {
  const type = `${edition}_${authType}`
  let conf: FormConfig | null = null
  switch (type) {
    case 'saas_uap': // uap账号登录（手机号）、支持注册、忘记密码(通过手机号验证码找回密码)
      conf = {
        fields: [
          { ...fieldFactories.phone(), placeholder: '请输入账号(手机号)' },
          fieldFactories.password(true),
          fieldFactories.agreement(),
          fieldFactories.remember(),
        ],
        actionsRender: ({ handleEvents, loading }: { handleEvents?: (event: string) => void, loading?: boolean }) => (
          <div class="w-full absolute bottom-0">
            <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')} loading={loading}>
              { loading ? '登录中' : (isInvite ? '登录并加入' : '登录') }
            </Button>
            <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
              还没有讯飞账号？
              <Button type="link" class="!m-0 !p-0 h-auto" onClick={() => handleEvents && handleEvents('switchToRegister')}>
                立即注册
              </Button>
            </div>
          </div>
        ),
      }
      break
    case 'enterprise_uap': // 企业版无注册、忘记密码功能，支持修改密码
      conf = {
        fields: [
          fieldFactories.phone(),
          fieldFactories.password(true),
          fieldFactories.agreement(),
          {
            ...fieldFactories.remember(),
            customRender: (ctx?: { formData?: any, handleEvents?: any }) => {
              const { formData = {}, handleEvents } = ctx ?? {}
              return (
                <div class="w-full flex justify-between items-center">
                  <Checkbox v-model:checked={formData.remember} class="text-[#000000D9] dark:text-[#FFFFFFD9]">
                    记住账号密码
                  </Checkbox>
                  <Button type="link" class="m-0 p-0 h-auto" onClick={() => handleEvents && handleEvents('modifyPassword')}>
                    修改密码
                  </Button>
                </div>
              )
            },
          },
        ],
        actionsRender: ({ handleEvents, loading }: { handleEvents?: (event: string) => void, loading?: boolean }) => (
          <div class="w-full absolute bottom-0">
            <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')} loading={loading}>
              { loading ? '登录中' : (isInvite ? '登录并加入' : '登录') }
            </Button>
          </div>
        ),
      }
      break
    case 'saas_casdoor': // casdoor账号登录（非手机号）、不支持忘记密码
      conf = {
        fields: [
          { ...fieldFactories.account(), key: 'loginName' },
          fieldFactories.password(true),
          fieldFactories.agreement(),
          {
            ...fieldFactories.remember(),
            customRender: (ctx?: { formData?: any, handleEvents?: any }) => {
              const { formData = {} } = ctx ?? {}
              return (
                <div class="w-full flex justify-between items-center">
                  <Checkbox v-model:checked={formData.remember} class="text-[#000000D9] dark:text-[#FFFFFFD9]">
                    记住账号密码
                  </Checkbox>
                </div>
              )
            },
          },
        ],
        actionsRender: ({ handleEvents, loading }: { handleEvents?: (event: string) => void, loading?: boolean }) => (
          <div class="w-full absolute bottom-0">
            <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')} loading={loading}>
              { loading ? '登录中' : (isInvite ? '登录并加入' : '登录') }
            </Button>
            <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
              还没有讯飞账号？
              <Button type="link" class="!m-0 !p-0 h-auto" onClick={() => handleEvents && handleEvents('switchToRegister')}>
                立即注册
              </Button>
            </div>
          </div>
        ),
      }
      break
    case 'enterprise_casdoor': // casdoor无企业版
      break
    default:
      break
  }
  return conf
}

// 手机登录表单配置
export function phoneLoginFormConfig(isInvite = false, edition = 'saas', authType = 'uap'): FormConfig | null {
  const type = `${edition}_${authType}`
  if (type !== 'saas_uap')
    return null
  // 仅saas版uap认证体系支持手机号验证码登录
  return {
    fields: [
      fieldFactories.phone(),
      {
        ...fieldFactories.captcha(),
        sendCaptcha: async (phone: string) => {
          await sendCaptcha(phone, false)
        },
      },
      fieldFactories.agreement(),
    ],
    actionsRender: ({ handleEvents, loading }: { handleEvents?: (event: string) => void, loading?: boolean }) => (
      <div class="w-full absolute bottom-0">
        <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')} loading={loading}>
          { loading ? '登录中' : (isInvite ? '登录并加入' : '登录') }
        </Button>
        <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
          还没有讯飞账号？
          <Button type="link" class="!m-0 !p-0 h-auto" onClick={() => handleEvents && handleEvents('switchToRegister')}>
            立即注册
          </Button>
        </div>
      </div>
    ),
  }
}

// 个人注册表单配置
export function personalRegisterFormConfig(formData: any, isInvite = false, edition = 'saas', authType = 'uap'): FormConfig | null {
  const type = `${edition}_${authType}`
  let conf: FormConfig | null = null
  switch (type) {
    case 'saas_uap': // uap账号注册（手机号）
      conf = {
        layout: 'vertical',
        fields: [
          fieldFactories.loginName(),
          fieldFactories.phone(),
          {
            ...fieldFactories.captcha(),
            sendCaptcha: async (phone: string) => {
              await sendCaptcha(phone, true)
            },
          },
          fieldFactories.agreement(),
        ],
        actionsRender: ({ handleEvents, loading }: { handleEvents?: (event: string) => void, loading?: boolean }) => (
          <div class="w-full absolute bottom-0">
            <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')} loading={loading}>
              { loading ? '注册中' : (isInvite ? '注册并加入' : '注册') }
            </Button>
            <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
              已有讯飞账号？
              <Button type="link" class="!m-0 !p-0 h-auto" onClick={() => handleEvents && handleEvents('switchToLogin')}>
                立即登录
              </Button>
            </div>
          </div>
        ),
      }
      break
    case 'enterprise_uap': // 企业版无注册功能
      break
    case 'saas_casdoor': // casdoor账号注册（非手机号）
      conf = {
        layout: 'vertical',
        fields: [
          { ...fieldFactories.account(), key: 'loginName' },
          fieldFactories.phone(),
          fieldFactories.password(),
          fieldFactories.confirmPassword(formData),
          fieldFactories.agreement(),
        ],
        actionsRender: ({ handleEvents, loading }: { handleEvents?: (event: string) => void, loading?: boolean }) => (
          <div class="w-full absolute bottom-0">
            <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')} loading={loading}>
              { loading ? '注册中' : (isInvite ? '注册并加入' : '注册') }
            </Button>
            <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
              已有讯飞账号？
              <Button type="link" class="!m-0 !p-0 h-auto" onClick={() => handleEvents && handleEvents('switchToLogin')}>
                立即登录
              </Button>
            </div>
          </div>
        ),
      }
      break
    case 'enterprise_casdoor': // casdoor无企业版 企业版无注册功能
      break
    default:
      break
  }
  return conf
}

// 通过手机号验证码找回密码表单配置，仅saas版uap认证体系有找回密码功能
export const forgotPasswordFormConfig: FormConfig = {
  layout: 'vertical',
  fields: [
    fieldFactories.phone(),
    {
      ...fieldFactories.captcha(),
      sendCaptcha: async (phone: string) => {
        await sendCaptcha(phone, false)
      },
    },
  ],
  actionsRender: ({ handleEvents }) => (
    <div class="w-full absolute bottom-0">
      <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')}>
        下一步
      </Button>
    </div>
  ),
}

// 通过手机号验证码设置密码表单，仅saas版uap认证体系有手机号验证码设置密码功能
export function createSetPasswordFormConfig(formData: any, isInvite: boolean): FormConfig {
  return {
    layout: 'vertical',
    fields: [
      fieldFactories.password(),
      fieldFactories.confirmPassword(formData),
      {
        type: 'slot',
        key: 'tip',
        customRender: () => {
          return (
            <div class="text-[14px] text-[#000000A6] dark:text-[#FFFFFFD9] mt-[12px] mb-[20px]">
              密码长度不少于 8 位，仅可包含大小写字母、数字和特殊字符，至少包含两种类型。
            </div>
          )
        },
      },
    ],

    actionsRender: ({ handleEvents }) => (
      <div class="w-full absolute bottom-0">
        <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')}>
          { isInvite ? '完成并加入' : '完成' }
        </Button>
      </div>
    ),
  }
}

// 通过手机号旧密码修改密码表单，仅企业版uap认证体系有手机号旧密码修改密码功能
export function modifyPasswordFormConfig(formData: any, isInvite: boolean): FormConfig {
  return {
    layout: 'vertical',
    fields: [
      { ...fieldFactories.account(), key: 'loginName' },
      { ...fieldFactories.password(true), key: 'oldPassword' },
      { ...fieldFactories.password(), key: 'newPassword', placeholder: '请输入新密码' },
      { ...fieldFactories.confirmPassword(formData, 'newPassword'), placeholder: '再次输入新密码' },
      {
        type: 'slot',
        key: 'tip',
        customRender: () => {
          return (
            <div class="text-[14px] text-[#000000A6] dark:text-[#FFFFFFD9] mt-[12px] mb-[20px]">
              密码长度不少于 8 位，仅可包含大小写字母、数字和特殊字符，至少包含两种类型。
            </div>
          )
        },
      },
    ],

    actionsRender: ({ handleEvents }) => (
      <div class="w-full absolute bottom-0">
        <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')}>
          { isInvite ? '完成并加入' : '完成' }
        </Button>
      </div>
    ),
  }
}

// 企咨询表单配置, 仅saas版uap认证体系有企业版注册咨询功能
export function consultFormConfig(consultType: 'renewal' | 'consult' = 'consult', consultEdition: 'professional' | 'enterprise'): FormConfig {
  if (consultType === 'renewal') {
    // 企业咨询续费表单配置
    return {
      layout: 'vertical',
      fields: [
        fieldFactories.companyName(),
        {
          ...fieldFactories.phone(),
          key: 'mobile',
          placeholder: '请输入您的或者负责人的手机号',
        },
        fieldFactories.renewalDuration(consultEdition),
      ],
      actionsRender: ({ handleEvents, loading }: { handleEvents?: (event: string) => void, loading?: boolean }) => (
        <div class="w-full absolute bottom-0">
          <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')} loading={loading}>
            {loading ? '提交中...' : '提交申请'}
          </Button>
          <div class="text-center text-[14px] mt-[12px] text-[#00000040] dark:text-[#FFFFFFD9]">
            稍后会有工作人员联系
          </div>
        </div>
      ),
    }
  }
  return {
    layout: 'vertical',
    fields: [
      {
        ...fieldFactories.loginName(),
        key: 'contactName',
      },
      fieldFactories.companyName(),
      fieldFactories.teamSize(),
      {
        ...fieldFactories.phone(),
        key: 'mobile',
        placeholder: '请输入您的或者负责人的手机号',
      },
      fieldFactories.email(),
    ],
    actionsRender: ({ handleEvents, loading }: { handleEvents?: (event: string) => void, loading?: boolean }) => (
      <div class="w-full absolute bottom-0">
        <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')} loading={loading}>
          {loading ? '提交中...' : '提交申请'}
        </Button>
        <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
          稍后会有工作人员联系
        </div>
      </div>
    ),
  }
}
