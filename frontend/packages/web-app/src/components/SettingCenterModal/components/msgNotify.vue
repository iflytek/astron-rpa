<script setup lang="ts">
import { Button, Checkbox, Form, Input, Switch } from 'ant-design-vue'

import { useNotify } from '../hooks/useMsgNotify'

import Card from './card.vue'

const {
  emailRef,
  email,
  emailFormRules,
  phoneRef,
  phone_msg,
  phoneFormRules,
  handleMsgTest,
} = useNotify()
</script>

<template>
  <div class="MsgNotify">
    <Card
      :title="$t('emailNotification')"
      :description="$t('runFailEmailNotification')"
      class="h-[84px] px-[20px] py-[17px]"
    >
      <template #suffix>
        <Switch v-model:checked="email.is_enable" />
      </template>
    </Card>
    <div v-if="email.is_enable" class="flex justify-between pl-[20px]">
      <Form
        ref="emailRef"
        label-align="right"
        :model="email"
        :rules="email.is_enable ? emailFormRules : {}"
        :colon="false"
        class="w-[calc(100%-140px)]"
        :label-col="{ span: 5 }"
        :wrapper-col="{ span: 19 }"
      >
        <Form.Item :label="$t('emailAddress')" name="receiver">
          <Input v-model:value="email.receiver" :placeholder="$t('settingCenter.msgNotify.inputReceiverMail')" />
        </Form.Item>
        <Form.Item :label="$t('sendingMethod')">
          <Checkbox v-model:checked="email.is_default">
            {{ $t('settingCenter.msgNotify.useDefaultSender') }}
          </Checkbox>
        </Form.Item>
        <div v-if="!email.is_default">
          <Form.Item :label="$t('settingCenter.msgNotify.mailServer')" name="mail_server">
            <Input v-model:value="email.mail_server" :placeholder="$t('settingCenter.msgNotify.inputMailServer')" />
          </Form.Item>
          <Form.Item :label="$t('settingCenter.msgNotify.mailPort')" name="mail_port">
            <Input v-model:value="email.mail_port" :placeholder="$t('settingCenter.msgNotify.inputMailPort')" />
          </Form.Item>
          <Form.Item :label="$t('settingCenter.msgNotify.senderMail')" name="sender_mail">
            <Input v-model:value="email.sender_mail" :placeholder="$t('settingCenter.msgNotify.inputSenderMail')" />
          </Form.Item>
          <Form.Item :label="$t('settingCenter.msgNotify.senderPassword')" name="password">
            <Input.Password v-model:value="email.password" :placeholder="$t('settingCenter.msgNotify.inputSenderPassword')" />
          </Form.Item>
          <Form.Item :label="$t('isSSL')">
            <Switch v-model:checked="email.use_ssl" />
          </Form.Item>
        </div>
        <Form.Item :label="$t('cc')">
          <Input v-model:value="email.cc" :placeholder="$t('settingCenter.msgNotify.ccPlaceholder')" />
        </Form.Item>
      </Form>
      <div class="w-[120px] flex flex-col justify-end">
        <Button type="primary" @click="() => handleMsgTest('mail')">
          {{ $t('sendTestEmail') }}
        </Button>
      </div>
    </div>
    <Card
      :title="$t('SMSNotification')"
      :description="$t('runFailSMSNotification')"
      class="h-[84px] px-[24px] py-[20px] mt-[24px]"
    >
      <template #suffix>
        <Switch v-model:checked="phone_msg.is_enable" />
      </template>
    </Card>
    <div v-if="phone_msg.is_enable" class="flex justify-between items-baseline pl-[20px]">
      <Form
        ref="phoneRef"
        label-align="right"
        :model="phone_msg"
        :rules="phone_msg.is_enable ? phoneFormRules : {}"
        :colon="false"
        class="w-[calc(100%-140px)]"
        :label-col="{ span: 5 }"
        :wrapper-col="{ span: 19 }"
      >
        <Form.Item :label="$t('mobilePhoneNumber')" name="receiver">
          <Input v-model:value="phone_msg.receiver" :placeholder="$t('enterPhoneNumber')" />
        </Form.Item>
      </Form>
      <div class="w-[120px] flex flex-col justify-end">
        <Button type="primary" @click="() => handleMsgTest('phone_msg')">
          {{ $t('sendTestSMS') }}
        </Button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.MsgNotify {
  font-size: 14px;
  :deep(.ant-form-item) {
    margin: 24px 0 0 0;
  }
}
</style>
