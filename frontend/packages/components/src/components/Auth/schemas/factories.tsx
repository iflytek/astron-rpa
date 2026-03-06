import { Button, Checkbox } from 'ant-design-vue'
import i18next from 'i18next'
import type { Component, VNode } from 'vue'
import type { JSX } from 'vue/jsx-runtime'

import AgreementTxt from '../components/Base/AgreementTxt.vue'

export type FieldType = 'input' | 'password' | 'captcha' | 'select' | 'checkbox' | 'textarea' | 'slot'

export interface FormConfig {
  fields: FieldSchema[]
  layout?: 'horizontal' | 'vertical'
  labelCol?: { span: number }
  wrapperCol?: { span: number }
  actionsRender: (ctx: {
    formData: Record<string, any>
    validate: () => Promise<boolean>
    loading?: boolean
    handleEvents?: (event: string, ...args: any[]) => void
  }) => VNode | JSX.Element | null
}

export interface FieldSchema {
  key: string
  label?: string
  type: FieldType
  placeholder?: string
  options?: { label: string, value: any }[]
  relationKey?: string
  rules?: any[]
  props?: Record<string, any>
  sendCaptcha?: (phone: string) => Promise<void>
  hidden?: (model: any) => boolean
  disabled?: boolean | ((model: any) => boolean)
  customRender?: (ctx?: {
    field?: FieldSchema
    value?: any
    formData?: Record<string, any>
    loading?: boolean
    validate?: () => Promise<boolean>
    handleEvents?: (event: string, ...args: any[]) => void
  }) => VNode | Component | JSX.Element | string | number | null
  helperText?: string
  dependencies?: string[]
}

const required = (msg: string) => ({ required: true, message: msg, trigger: 'change' })

// 自定义验证器
const validators = {
  loginName: (_rule: any, value: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!value) {
        reject(new Error(i18next.t('authForm.loginNamePlaceholder')))
        return
      }
      if (value.length > 30) {
        reject(new Error(i18next.t('authForm.nameLengthError')))
        return
      }
      const pattern = /^[\w\u4E00-\u9FA5-]{1,30}$/
      if (!pattern.test(value)) {
        reject(new Error(i18next.t('authForm.namePatternError')))
        return
      }
      resolve()
    })
  },

  // 密码验证
  password: (_rule: any, value: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!value) {
        reject(new Error(i18next.t('authForm.passwordPlaceholder')))
        return
      }
      // 长度 8-20
      if (value.length < 8) {
        reject(new Error(i18next.t('authForm.passwordLengthMinError')))
        return
      }
      if (value.length > 20) {
        reject(new Error(i18next.t('authForm.passwordLengthMaxError')))
        return
      }
      // 字符集：仅允许 大小写、数字、特殊字符
      if (!/^[\w!@#$%^&*()+\-=\]{};':"\\|,.<>?/~`]+$/.test(value)) {
        reject(new Error(i18next.t('authForm.passwordPatternError')))
        return
      }
      // 统计类型
      const types = [
        /[a-z]/, // 小写
        /[A-Z]/, // 大写
        /\d/, // 数字
        /[!@#$%^&*()_+\-=\]{};':"\\|,.<>?/~`]/, // 特殊字符
      ].filter(re => re.test(value)).length

      if (types < 2) {
        reject(new Error(i18next.t('authForm.passwordComplexityError')))
        return
      }
      resolve()
    })
  },

  // 手机号验证
  phone: (_rule: any, value: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!value) {
        reject(new Error(i18next.t('authForm.phoneRequired')))
        return
      }
      const pattern = /^1[3-9]\d{9}$/
      if (!pattern.test(value)) {
        reject(new Error(i18next.t('authForm.phonePatternError')))
        return
      }
      resolve()
    })
  },
}

export const fieldFactories = {
  loginName: (): FieldSchema => ({
    key: 'loginName',
    label: i18next.t('userName'),
    type: 'input',
    placeholder: i18next.t('authForm.loginNamePlaceholder'),
    rules: [
      { validator: validators.loginName, trigger: 'change' },
    ],
  }),
  account: (): FieldSchema => ({
    key: 'account',
    label: i18next.t('account'),
    type: 'input',
    placeholder: i18next.t('authForm.accountPlaceholder'),
    rules: [
      required(i18next.t('authForm.accountPlaceholder')),
    ],
  }),
  password: (onlyRequired: boolean = false): FieldSchema => ({
    key: 'password',
    label: i18next.t('password'),
    type: 'password',
    placeholder: i18next.t('authForm.passwordPlaceholder'),
    rules: [
      onlyRequired ? required(i18next.t('authForm.passwordPlaceholder')) : { validator: validators.password, trigger: 'change' },
    ],
  }),
  confirmPassword: (formData: any, relationKey = 'password'): FieldSchema => ({
    key: 'confirmPassword',
    label: i18next.t('confirmPassword'),
    type: 'password',
    placeholder: i18next.t('authForm.confirmPasswordPlaceholder'),
    rules: [{
      validator: (_rule: any, value: string) => {
        return new Promise<void>((resolve, reject) => {
          if (!formData[relationKey]) {
            reject(new Error(i18next.t('authForm.passwordPlaceholder')))
            return
          }
          if (!value) {
            reject(new Error(i18next.t('authForm.confirmPasswordPlaceholder')))
            return
          }

          if (value !== formData[relationKey]) {
            reject(new Error(i18next.t('authForm.passwordMismatch')))
            return
          }

          resolve()
        })
      },
      trigger: 'change',
    }],
  }),

  agreement: (): FieldSchema => ({
    key: 'agreement',
    label: i18next.t('authForm.userAgreement'),
    type: 'checkbox',
    rules: [
      {
        validator: (_rule: any, value: boolean): Promise<void> => {
          return new Promise((resolve, reject) => {
            if (!value) {
              reject(new Error(i18next.t('authForm.agreementRequired')))
              return
            }
            resolve()
          })
        },
        trigger: 'change',
      },
    ],
    customRender: () => <AgreementTxt />,
  }),
  phone: (): FieldSchema => ({
    key: 'phone',
    label: i18next.t('mobilePhoneNumber'),
    type: 'input',
    placeholder: i18next.t('authForm.phoneRequired'),
    rules: [
      { validator: validators.phone, trigger: 'change' },
    ],
    props: {
      maxlength: 11,
    },
  }),

  captcha: (): FieldSchema => ({
    key: 'captcha',
    label: i18next.t('verificationCode'),
    type: 'captcha',
    placeholder: i18next.t('authForm.captchaPlaceholder'),
    relationKey: 'phone',
    sendCaptcha: () => Promise.resolve(),
    rules: [
      required(i18next.t('authForm.captchaRequired')),
    ],
    props: {
      maxlength: 6,
    },
  }),

  companyName: (): FieldSchema => ({
    key: 'companyName',
    label: i18next.t('authForm.companyName'),
    type: 'input',
    placeholder: i18next.t('authForm.enterCompanyName'),
    rules: [
      required(i18next.t('authForm.enterCompanyName')),
      { min: 1, max: 50, message: i18next.t('authForm.companyNameMaxLength'), trigger: 'change' },
    ],
  }),

  teamSize: (): FieldSchema => ({
    key: 'teamSize',
    label: i18next.t('authForm.teamSize'),
    type: 'select',
    options: [
      { label: i18next.t('authForm.teamSizeOptions.1-10'), value: '1-10人' },
      { label: i18next.t('authForm.teamSizeOptions.11-50'), value: '11-50人' },
      { label: i18next.t('authForm.teamSizeOptions.51-100'), value: '51-100人' },
      { label: i18next.t('authForm.teamSizeOptions.101-500'), value: '101-500人' },
      { label: i18next.t('authForm.teamSizeOptions.500plus'), value: '500人以上' },
    ],
    placeholder: i18next.t('authForm.selectTeamSize'),
    rules: [required(i18next.t('authForm.selectTeamSize'))],
  }),

  email: (): FieldSchema => ({
    key: 'email',
    label: i18next.t('email'),
    type: 'input',
    placeholder: i18next.t('userForm.enterEmail'),
    rules: [
      { type: 'email', message: i18next.t('settingCenter.msgNotify.mailFormatError'), trigger: 'change' },
    ],
  }),
  remember: (): FieldSchema => ({
    type: 'slot',
    key: 'remember',
    customRender: (ctx?: { formData?: any, handleEvents?: any }) => {
      const { formData = {}, handleEvents } = ctx ?? {}
      return (
        <div class="w-full flex justify-between items-center">
          <Checkbox v-model:checked={formData.remember} class="text-[#000000D9] dark:text-[#FFFFFFD9]">
            {i18next.t('authForm.rememberPassword')}
          </Checkbox>
          <Button type="link" class="m-0 p-0 h-auto" onClick={() => handleEvents && handleEvents('forgotPassword')}>
            {i18next.t('auth.forgetPassword')}
          </Button>
        </div>
      )
    },
  }),
  renewalDuration: (consultEdition: 'professional' | 'enterprise'): FieldSchema => ({
    key: 'renewalDuration',
    label: i18next.t('authForm.renewalDuration'),
    type: 'select',
    options: [
      { label: i18next.t('authForm.durationOptions.6months'), value: '6个月', consultEditions: ['professional'] },
      { label: i18next.t('authForm.durationOptions.1year'), value: '1年', consultEditions: ['professional', 'enterprise'] },
      { label: i18next.t('authForm.durationOptions.2years'), value: '2年', consultEditions: ['professional', 'enterprise'] },
      { label: i18next.t('authForm.durationOptions.3years'), value: '3年', consultEditions: ['enterprise'] },
    ].filter(opt => opt.consultEditions.includes(consultEdition)),
    placeholder: i18next.t('authForm.selectRenewalDuration'),
    rules: [required(i18next.t('authForm.selectRenewalDuration'))],
  }),
}

/**
 * 根据表单配置生成初始数据对象
 * @param config 表单配置
 * @param defaultValues 默认值覆盖
 * @returns 初始数据对象
 */
export function generateFormData<T = Record<string, any>>(config: FormConfig, defaultValues: Partial<T> = {}): T {
  const formData = {} as T

  config.fields.forEach((field) => {
    // 根据字段类型设置默认值
    let defaultValue: any

    switch (field.type) {
      case 'checkbox':
        defaultValue = false
        break
      case 'select':
        defaultValue = undefined
        break
      case 'input':
      case 'password':
      case 'captcha':
      case 'textarea':
      case 'slot':
      default:
        defaultValue = ''
        break
    }

    // 使用提供的默认值覆盖，否则使用类型默认值
    ;(formData as any)[field.key] = defaultValues[field.key as keyof T] ?? defaultValue
  })

  return formData
}
