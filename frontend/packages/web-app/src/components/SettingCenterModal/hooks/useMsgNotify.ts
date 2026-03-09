import { message } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import { useTranslation } from 'i18next-vue'
import { isEmpty } from 'lodash-es'
import { onBeforeUnmount, ref } from 'vue'
import type { Ref } from 'vue'

import { toolsInterfacePost } from '@/api/setting'
import useUserSettingStore from '@/stores/useUserSetting.ts'

function initEmailData(): RPA.EmailFormMap {
  return {
    is_enable: false, // 是否启用, 默认不启用
    receiver: '', // 收件人
    is_default: true, // 默认不起用其他邮箱
    mail_server: '', // 发件服务器
    mail_port: '', // 端口
    sender_mail: '', // 邮件账号
    password: '', // 邮件密码(需要使用密钥，存储的也是密钥名称)
    use_ssl: true, // 是否SSL
    cc: '', // 抄送
  }
}

function initPhoneData(): RPA.PhoneFormMap {
  return {
    is_enable: false, // 是否启用, 默认不启用
    receiver: '', // 收件人手机号
    phone_msg_url: 'https://pretest.xfpaas.com/dripsms/smssafe',
  }
}

export function useNotify() {
  const { t } = useTranslation()
  const emailRef = ref()

  const email: Ref<RPA.EmailFormMap> = ref(initEmailData())
  const emailFormRules: Record<string, Rule[]> = {
    receiver: [
      { required: true, trigger: 'change' },
      {
        pattern: /\w[-\w.+]*@([A-Z0-9][-A-Z0-9]+\.)+[A-Z]{2,14}/i,
        message: t('settingCenter.msgNotify.mailFormatError'),
        trigger: 'blur',
      },
    ],
    mail_server: [{ required: true, message: t('settingCenter.msgNotify.inputMailServer'), trigger: 'blur' }],
    mail_port: [{ required: true, message: t('settingCenter.msgNotify.inputMailPort'), trigger: 'blur' }],
    sender_mail: [
      { required: true, message: t('settingCenter.msgNotify.inputSenderMail'), trigger: 'blur' },
      {
        pattern: /\w[-\w.+]*@([A-Z0-9][-A-Z0-9]+\.)+[A-Z]{2,14}/i,
        message: t('settingCenter.msgNotify.mailFormatError'),
        trigger: 'blur',
      },
    ],
    password: [{ required: true, message: t('settingCenter.msgNotify.inputSenderPassword'), trigger: 'blur' }],
  }
  const phoneRef = ref()
  const phone_msg: Ref<RPA.PhoneFormMap> = ref(initPhoneData())
  const phoneFormRules: Record<string, Rule[]> = {
    receiver: [
      // /0?(13|14|15|18)[0-9]{9}/
      { required: true, trigger: 'change' },
      {
        pattern: /^1([3-9])\d{9}$/,
        message: t('settingCenter.msgNotify.phoneFormatError'),
        trigger: 'blur',
      },
    ],
  }

  function handleMsgTest(key: string) {
    handleValidateSave().then(() => {
      toolsInterfacePost({
        alert_type: key,
      }).then((res) => {
        message.success(res.msg || t('settingCenter.msgNotify.testSuccess'))
      })
      message.info(t('settingCenter.msgNotify.testSent', { type: key === 'mail' ? t('settingCenter.msgNotify.email') : t('settingCenter.msgNotify.sms') }))
    })
  }
  function errorSave() {
    let newSetting
    if (email.value.is_enable) {
      newSetting = {
        msgNotifyForm: {
          email: initEmailData(),
          phone_msg: phone_msg.value,
        },
      }
    }
    else {
      newSetting = {
        msgNotifyForm: {
          email: email.value,
          phone_msg: initPhoneData(),
        },
      }
    }
    useUserSettingStore().saveUserSetting(newSetting)
  }
  function handleValidateSave() {
    return new Promise((resolve, reject) => {
      const currRef = email.value.is_enable ? emailRef : phoneRef
      currRef.value.validate().then(() => {
        const newSetting = {
          msgNotifyForm: {
            email: email.value,
            phone_msg: phone_msg.value,
          },
        }
        useUserSettingStore().saveUserSetting(newSetting)
        resolve({})
      }).catch(() => {
        reject(new Error(t('common.validationFailed')))
      })
    })
  }

  function initData() {
    const msgNotifyForm = useUserSettingStore().userSetting?.msgNotifyForm || {} as RPA.MessageFormMap
    const { email: emailData, phone_msg: phoneData } = msgNotifyForm
    if (emailData && !isEmpty(emailData)) {
      email.value = emailData
    }
    if (phoneData && !isEmpty(phoneData)) {
      phone_msg.value = phoneData
    }
  }
  initData()

  onBeforeUnmount(() => {
    handleValidateSave().catch(() => { errorSave() })
  })
  return {
    emailRef,
    email,
    emailFormRules,
    phoneRef,
    phone_msg,
    phoneFormRules,
    handleValidateSave,
    handleMsgTest,
  }
}
