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
  <div
    class="login-form-layout md:bg-[#ffffff] dark:md:bg-[#000000] h-full
      w-full max-w-full p-[24px] rounded-t-[24px]
      md:p-[40px] md:rounded-[16px]
      flex flex-col"
    :class="wrapClass"
  >
    <BackButton v-if="showBack" class="flex-shrink-0" @click="() => emit('back')" />

    <slot name="header">
      <InviteHeader v-if="inviteInfo" class="flex-shrink-0 hidden md:block" :invite-info="inviteInfo" />
      <AuthHeader
        v-else-if="title"
        class="flex-shrink-0"
        :title="title"
        :sub-title="subTitle"
        :action-text="actionText"
        @action-click="() => emit('action')"
      />
    </slot>

    <div
      class="inner-content relative flex-1 min-h-0"
      :class="contentClass"
    >
      <slot />
    </div>

    <AgreementTxt v-if="showAgreement" class="mt-[10px] flex-shrink-0" :type="agreementType" />
  </div>
</template>
