<script setup lang="ts">
import type { InviteInfo } from '../../interface'

import AgreementTxt from './AgreementTxt.vue'
import AuthHeader from './AuthHeader.vue'
import BackButton from './BackButton.vue'
import InviteHeader from './InviteHeader.vue'

defineProps<{
  wrapClass?: string
  contentClass?: string
  showBack?: boolean
  showAgreement?: boolean
  agreementType?: 'show' | 'check'
  title?: string
  subTitle?: string
  actionText?: string
  inviteInfo?: InviteInfo
}>()

const emit = defineEmits<{
  back: []
  action: []
}>()
</script>

<template>
  <div class="login-form-layout bg-[#ffffff] dark:bg-[#000000] rounded-[16px] w-[400px] h-full p-[40px]" :class="wrapClass">
    <BackButton v-if="showBack" @click="() => emit('back')" />

    <slot name="header">
      <InviteHeader v-if="inviteInfo" :invite-info="inviteInfo" />
      <AuthHeader
        v-else-if="title"
        :title="title"
        :sub-title="subTitle"
        :action-text="actionText"
        @action-click="() => emit('action')"
      />
    </slot>

    <div
      class="inner-content relative h-[calc(100%-93px)]"
      :class="[
        { 'h-[calc(100%-113px)]': showAgreement },
        contentClass,
      ]"
    >
      <slot />
    </div>

    <AgreementTxt v-if="showAgreement" class="mt-[10px]" :type="agreementType" />
  </div>
</template>
