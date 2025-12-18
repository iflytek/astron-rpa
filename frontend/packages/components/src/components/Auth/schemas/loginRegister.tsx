import { fieldFactories } from './factories'
import type { FormConfig } from './factories'
import { Button } from "ant-design-vue"

/**
 * 登录注册相关表单配置
*/

// 账号登录表单配置
export const accountLoginFormConfig: FormConfig = {
  fields: [
    {...fieldFactories.phone(), placeholder: '请输入账号(手机号)'},
    fieldFactories.password(true),
    fieldFactories.agreement(),
    fieldFactories.remember(),
  ],
  actionsRender: ({ handleEvents, loading }) => (
    <div class="w-full absolute bottom-0">
      <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')} loading={loading}>
        { loading ? '登录中' : '登录' }
      </Button>
      <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
        还没有讯飞账号？
        <Button type="link" class="!m-0 !p-0 h-auto" onClick={() => {console.log("switchToRegisterswitchToRegisterswitchToRegister");handleEvents && handleEvents('switchToRegister')}}>
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
    fieldFactories.captcha(),
    fieldFactories.agreement(),
  ],
  actionsRender: ({ handleEvents, loading  }) => (
    <div class="w-full absolute bottom-0">
      <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')} loading={loading}>
        { loading ? '登录中' : '登录' }
      </Button>
      <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
        还没有讯飞账号？
        <Button type="link" class="!m-0 !p-0 h-auto" onClick={() => handleEvents && handleEvents('switchToRegister')}>
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
    fieldFactories.loginName(),
    fieldFactories.phone(),
    fieldFactories.captcha(),
    fieldFactories.agreement()
  ],
  actionsRender: ({ handleEvents, loading }) => (
    <div class="w-full absolute bottom-0">
      <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')}  loading={loading}>
        { loading ? '注册中' : '注册' }
      </Button>
      <div class="text-center text-[14px] mt-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
        已有讯飞账号？
        <Button type="link" class="!m-0 !p-0 h-auto" onClick={() => handleEvents && handleEvents('switchToLogin')}>
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
      ...fieldFactories.loginName(),
      key: 'contactName',
    },
    fieldFactories.companyName(),
    fieldFactories.teamSize(),
    {
      ...fieldFactories.phone(), 
      placeholder: '请输入您的或者负责人的手机号'
    },
    fieldFactories.email(),
  ],
  actionsRender: ({ handleEvents, loading }) => (
    <div class="w-full absolute bottom-0">
      <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')} loading={loading}>
        {loading ? '提交中...' : '提交申请'}
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
    fieldFactories.captcha(),
  ],
  actionsRender: ({ handleEvents }) => (
    <div class="w-full absolute bottom-0">
      <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')}>
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

  actionsRender: ({ handleEvents }) => (
    <div class="w-full absolute bottom-0">
      <Button type="primary" size="large" block onClick={() => handleEvents && handleEvents('submit')}>
        完成
      </Button>
    </div>
  )
})
