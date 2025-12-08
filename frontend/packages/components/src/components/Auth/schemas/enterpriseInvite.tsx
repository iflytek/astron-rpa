import { fieldFactories } from './factories'
import type { FormConfig } from './factories'
import { Button } from "ant-design-vue"
import AgreementTxt from '../components/Base/AgreementTxt.vue'

/**
 * 企业邀请相关表单配置
 */

// 企业邀请填写用户信息表单配置
export const enterpriseInviteFillUserInfoFormConfig: FormConfig = {
  layout: 'vertical',
  fields: [
    fieldFactories.username(),
    fieldFactories.phone(),
    fieldFactories.email(),
    {
      ...fieldFactories.agreement(),
      customRender: () => <AgreementTxt />
    },
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
        确认加入
      </Button>
      <AgreementTxt type='invite' />
    </div>
  )
}

export const enterprisePhoneLoginFormConfig: FormConfig = {
  fields: [
    fieldFactories.phone(),
    fieldFactories.code(),
  ],
  actionsRender: ({ emit }) => (
    <div class="w-full ">
      <Button type="primary" size="large" class="mt-[60px]" block onClick={() => emit && emit('submit')}>
        下一步
      </Button>
    </div>
  )
}

// 企业邀请设置密码表单配置工厂函数
export const createEnterpriseInviteSetPasswordFormConfig = (formData: any): FormConfig => ({
  layout: 'vertical',
  fields: [
    fieldFactories.username(),
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
    <div class="w-full ">
      <Button type="primary" size="large" class="mt-[60px]" block onClick={() => emit && emit('submit')}>
        确认加入
      </Button>
    </div>
  )
})
