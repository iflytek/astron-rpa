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
          <Input v-model:value="email.receiver" placeholder="请输入收件箱地址" />
        </Form.Item>
        <Form.Item :label="$t('sendingMethod')">
          <Checkbox v-model:checked="email.is_default">
            使用默认发件箱
          </Checkbox>
        </Form.Item>
        <div v-if="!email.is_default">
          <Form.Item label="发件箱服务器" name="mail_server">
            <Input v-model:value="email.mail_server" placeholder="请输入发件箱服务器" />
          </Form.Item>
          <Form.Item label="发件箱端口" name="mail_port">
            <Input v-model:value="email.mail_port" placeholder="请输入发件箱端口号" />
          </Form.Item>
          <Form.Item label="发件箱地址" name="sender_mail">
            <Input v-model:value="email.sender_mail" placeholder="请输入发件箱地址" />
          </Form.Item>
          <Form.Item label="发件箱密码" name="password">
            <Input.Password v-model:value="email.password" placeholder="请输入发件箱密码" />
          </Form.Item>
        </div>
        <Form.Item :label="$t('isSSL')">
          <Switch v-model:checked="email.use_ssl" />
        </Form.Item>
        <Form.Item :label="$t('cc')">
          <Input v-model:value="email.cc" placeholder="多个邮箱请以英文;分割，例如：aaa@163.com;bbbQqq.com" />
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
