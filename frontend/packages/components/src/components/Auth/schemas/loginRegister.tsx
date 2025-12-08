import { fieldFactories } from './factories'
import type { FormConfig } from './factories'
import { Button } from "ant-design-vue"

/**
 * 登录注册相关表单配置
*/

// 账号登录表单配置
export const accountLoginFormConfig: FormConfig = {
  fields: [
    fieldFactories.username(),
    fieldFactories.password(),
    fieldFactories.agreement(),
    fieldFactories.remember(),
  ],
  actionsRender: ({ emit }) => (
    <div class="w-full">
      <Button type="primary" size="large" class="mt-[60px]" block onClick={() => emit && emit('submit')}>
        登录
      </Button>
      <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
        还没有账号？
        <Button type="link" class="!m-0 !p-0 h-auto" onClick={() => {console.log("switchToRegisterswitchToRegisterswitchToRegister");emit && emit('switchToRegister')}}>
          立即注册
        </Button>
      </div>
    </div>
  )
}

// 手机登录表单配置
export const phoneLoginFormConfig: FormConfig = {
  fields: [
    fieldFactories.phone(),
    fieldFactories.code(),
    fieldFactories.agreement(),
  ],
  actionsRender: ({ emit }) => (
    <div class="w-full">
      <Button type="primary" size="large" class="mt-[60px]" block onClick={() => emit && emit('submit')}>
        登录
      </Button>
      <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
        还没有账号？
        <Button type="link" class="!m-0 !p-0 h-auto" onClick={() => emit && emit('switchToRegister')}>
          立即注册
        </Button>
      </div>
    </div>
  )
}

// 个人注册表单配置
export const personalRegisterFormConfig: FormConfig = {
  layout: 'vertical',
  fields: [
    fieldFactories.username(),
    fieldFactories.phone(),
    fieldFactories.code(),
    fieldFactories.agreement()
  ],
  actionsRender: ({ emit }) => (
    <div class="w-full">
      <Button type="primary" size="large" class="mt-[60px]" block onClick={() => emit && emit('submit')}>
        注册
      </Button>
      <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
        已有账号？
        <Button type="link" class="!m-0 !p-0 h-auto" onClick={() => emit && emit('switchToLogin')}>
          立即登录
        </Button>
      </div>
    </div>
  )
}

// 企业注册表单配置
export const enterpriseRegisterFormConfig: FormConfig = {
  layout: 'vertical',
  fields: [
    {
      ...fieldFactories.username(),
      key: 'contactName',
      placeholder: '请输入您的姓名',
    },
    fieldFactories.companyName(),
    fieldFactories.teamSize(),
    fieldFactories.email(),
    {
      ...fieldFactories.phone(), 
      placeholder: '请输入您的或者负责人的手机号'
    },
  ],
  actionsRender: ({ emit }) => (
    <div class="w-full">
      <Button type="primary" size="large" class="mt-[60px]" block onClick={() => emit && emit('submit')}>
        提交申请
      </Button>
      <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
        企业已开通？请联系管理员为您创建账号
      </div>
    </div>
  )
}

// 忘记密码表单配置
export const forgotPasswordFormConfig: FormConfig = {
  layout: 'vertical',
  fields: [
    fieldFactories.phone(),
    fieldFactories.code(),
  ],
  actionsRender: ({ emit }) => (
    <div class="w-full">
      <Button type="primary" size="large" class="mt-[60px]" block onClick={() => emit && emit('submit')}>
        下一步
      </Button>
    </div>
  )
}

// 设置密码表单
export const createSetPasswordFormConfig = (formData: any): FormConfig => ({
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
      }
    }
  ],

  actionsRender: ({ emit }) => (
    <div class="w-full">
      <Button type="primary" size="large" class="mt-[60px]" block onClick={() => emit && emit('submit')}>
        完成
      </Button>
    </div>
  )
})
