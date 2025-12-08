<script setup lang="ts">
import BackButton from './BackButton.vue'
import AuthHeader from './AuthHeader.vue'
import AgreementTxt from './AgreementTxt.vue'

defineProps<{
  wrapClass?: string
  showBack?: boolean
  showAgreement?: boolean
  agreementType?: 'login' | 'invite'
  title?: string
  subTitle?: string
  actionText?: string
}>()

const emit = defineEmits<{
  back: []
  action: []
}>()
</script>
<template>
  <div class="form-layout relative bg-[#ffffff] dark:bg-[#000000] shadow-lg rounded-[16px] w-[400px] h-[auto] p-[40px]" :class="wrapClass">
    <BackButton v-if="showBack" @click="() => emit('back')" />

    <slot name="header">
      <AuthHeader
        v-if="title"
        :title="title"
        :sub-title="subTitle"
        :action-text="actionText"
        @action-click="() => emit('action')"
      />
    </slot>

    <div class="h-[calc(100%-32px)]">
      <slot />
    </div>

    <AgreementTxt v-if="showAgreement" :type="agreementType" />
  </div>
</template>

