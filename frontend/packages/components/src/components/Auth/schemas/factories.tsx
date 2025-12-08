import { VNode, Component } from 'vue'
import type { JSX } from 'vue/jsx-runtime'
import AgreementTxt from '../components/Base/AgreementTxt.vue'
import { Checkbox, Button } from "ant-design-vue"

export type FieldType =  'input' | 'password' | 'code' | 'select' | 'checkbox' | 'textarea' | 'slot'

export interface FormConfig {
  fields: FieldSchema[]
  layout?: 'horizontal' | 'vertical'
  labelCol?: any
  wrapperCol?: any
  actionsRender: (ctx: {
    formData: Record<string, any>
    validate: () => Promise<boolean>
    emit?: (event: string, ...args: any[]) => void
  }) => VNode | JSX.Element | null
}

export interface FieldSchema {
  key: string
  label?: string
  type: FieldType
  placeholder?: string
  options?: { label: string; value: any }[]
  rules?: any[]
  props?: Record<string, any>
  visible?: (model: any) => boolean
  disabled?: (model: any) => boolean
  customRender?: (ctx?: {
    field?: FieldSchema;            
    value?: any;                  
    formData?: Record<string, any>;  
    validate?: () => Promise<boolean>;
    emit?: (event: string, ...args: any[]) => void;
  }) => VNode | Component | JSX.Element | string | number | null
  helperText?: string
  dependencies?: string[]
}

const required = (msg: string) => ({ required: true, message: msg, trigger: 'change' })

// 自定义验证器
const validators = {
  // 用户名验证
  username: (_rule: any, value: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!value) {
        reject(new Error('请输入用户名'))
        return
      }
      if (value.length < 2) {
        reject(new Error('用户名至少需要2个字符'))
        return
      }
      if (value.length > 20) {
        reject(new Error('用户名不能超过20个字符'))
        return
      }
      const pattern = /^[\w\u4E00-\u9FA5]+$/
      if (!pattern.test(value)) {
        reject(new Error('用户名只能包含字母、数字、下划线和中文'))
        return
      }
      resolve()
    })
  },

  // 密码强度验证
  password: (_rule: any, value: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!value) {
        reject(new Error('请输入密码'))
        return
      }
      if (value.length < 6) {
        reject(new Error('密码至少需要6个字符'))
        return
      }
      if (value.length > 20) {
        reject(new Error('密码不能超过20个字符'))
        return
      }
      // 密码强度检查：至少包含数字和字母
      const hasNumber = /\d/.test(value)
      const hasLetter = /[a-z]/i.test(value)
      if (!hasNumber || !hasLetter) {
        reject(new Error('密码必须包含数字和字母'))
        return
      }
      resolve()
    })
  },

  // 手机号验证
  phone: (_rule: any, value: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!value) {
        reject(new Error('请输入手机号'))
        return
      }
      const pattern = /^1[3-9]\d{9}$/
      if (!pattern.test(value)) {
        reject(new Error('请输入正确的手机号'))
        return
      }
      resolve()
    })
  }
}

export const fieldFactories = {
  username: (): FieldSchema => ({
    key: 'username',
    label: '用户名',
    type: 'input',
    placeholder: '请输入用户名',
    rules: [
      { validator: validators.username, trigger: 'change' }
    ]
  }),
  
  password: (): FieldSchema => ({
    key: 'password',
    label: '密码',
    type: 'password',
    placeholder: '请输入密码',
    rules: [
      { validator: validators.password, trigger: 'change' }
    ]
  }),
  confirmPassword: (formData: any): FieldSchema => ({
    key: 'confirmPassword',
    label: '确认密码',
    type: 'password',
    placeholder: '再次输入密码',
    rules: [{
      validator: (rule: any, value: string, callback: any) => {
        return new Promise<void>((resolve, reject) => {
          if (!formData.password) {
            reject(new Error('请先输入密码'))
            return
          }
          if (!value) {
            reject(new Error('请输入确认密码'))
            return
          }
          
          if (value !== formData.password) {
            reject(new Error('两次密码不一致'))
            return
          }
          
          resolve()
        })
      },
      trigger: 'change'
    }]
  }),

  agreement: (): FieldSchema => ({
    key: 'agreement',
    label: '用户协议',
    type: 'checkbox',
    rules: [
      {
        validator: (_rule: any, value: boolean): Promise<void> => {
          return new Promise((resolve, reject) => {
            if (!value) {
              reject(new Error('请阅读并同意用户协议'))
              return
            }
            resolve()
          })
        },
        trigger: 'change'
      }
    ],
    customRender: () => <AgreementTxt />
  }),
  phone: (): FieldSchema => ({
    key: 'phone',
    label: '手机号',
    type: 'input',
    placeholder: '请输入手机号',
    rules: [
      { validator: validators.phone, trigger: 'change' }
    ],
    props: {
      maxlength: 11
    }
  }),
  
  code: (): FieldSchema => ({
    key: 'code',
    label: '验证码',
    type: 'code',
    placeholder: '请输入验证码',
    rules: [
      required('请输入验证码'),
      { min: 4, max: 6, message: '验证码为4-6位', trigger: 'change' }
    ],
    props: {
      maxlength: 6
    }
  }),
  
  companyName: (): FieldSchema => ({
    key: 'companyName',
    label: '企业名称',
    type: 'input',
    placeholder: '请输入企业名称',
    rules: [
      required('请输入企业名称'),
      { min: 2, max: 100, message: '企业名称为2-100个字符', trigger: 'change' }
    ]
  }),
  
  teamSize: (): FieldSchema => ({
    key: 'teamSize',
    label: '团队规模',
    type: 'select',
    options: [
      { label: '1-10人', value: '1-10' },
      { label: '11-50人', value: '11-50' },
      { label: '51-100人', value: '51-100' },
      { label: '101-500人', value: '101-500' },
      { label: '500人以上', value: '500+' },
    ],
    placeholder: '请选择团队规模',
    rules: [required('请选择团队规模')]
  }),

  email: (): FieldSchema => ({
    key: 'email',
    label: '邮箱',
    type: 'input',
    placeholder: '请输入您的邮箱',
    rules: [
      { required: true, message: '请输入您的邮箱', trigger: 'change' },
      { type: 'email', message: '请输入正确的邮箱格式', trigger: 'change' }
    ]
  }),
  remember: (): FieldSchema => ({
    type: 'slot',
    key: 'remember',
    customRender: (ctx?: { formData?: any; emit?: any }) => {
      const { formData = {}, emit } = ctx ?? {}
      return (
        <div class="w-full flex justify-between items-center">
          <Checkbox v-model:checked={formData.remember} class="text-[#000000D9] dark:text-[#FFFFFFD9]">
            记住账号密码
          </Checkbox>
          <Button type="link" class="m-0 p-0 h-auto" onClick={() => emit && emit('forgetPassword')}>
            忘记密码
          </Button>
        </div>
      )
    }
  })
}

/**
 * 根据表单配置生成初始数据对象
 * @param config 表单配置
 * @param defaultValues 默认值覆盖
 * @returns 初始数据对象
 */
export const generateFormData = <T = Record<string, any>>(
  config: FormConfig, 
  defaultValues: Partial<T> = {}
): T => {
  const formData = {} as T
  
  config.fields.forEach(field => {
    // 根据字段类型设置默认值
    let defaultValue: any
    
    switch (field.type) {
      case 'checkbox':
        defaultValue = false
        break
      case 'select':
        defaultValue = field.options?.[0]?.value || ''
        break
      case 'input':
      case 'password':
      case 'code':
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