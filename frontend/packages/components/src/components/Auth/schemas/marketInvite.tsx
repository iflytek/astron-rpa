import { fieldFactories } from './factories'
import type { FormConfig } from './factories'
import { Button } from "ant-design-vue"

/**
 * 登录注册相关表单配置
*/

// 账号登录表单配置
export const marketInviteAccountLoginFormConfig: FormConfig = {
  fields: [
    fieldFactories.username(),
    fieldFactories.password(),
  ],
  actionsRender: ({ emit }) => (
    <div class="w-full">
      <Button type="primary" size="large" class="mt-[60px]" block onClick={() => emit && emit('submit')}>
        登录并加入
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
export const marketInvitePhoneLoginFormConfig: FormConfig = {
  fields: [
    fieldFactories.phone(),
    fieldFactories.code(),
  ],
  actionsRender: ({ emit }) => (
    <div class="w-full">
      <Button type="primary" size="large" class="mt-[60px]" block onClick={() => emit && emit('submit')}>
        登录并加入
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
export const marketInvitePersonalRegisterFormConfig: FormConfig = {
  layout: 'vertical',
  fields: [
    fieldFactories.username(),
    fieldFactories.phone(),
    fieldFactories.code(),
  ],
  actionsRender: ({ emit }) => (
    <div class="w-full">
      <Button type="primary" size="large" class="mt-[60px]" block onClick={() => emit && emit('submit')}>
        注册并加入
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
