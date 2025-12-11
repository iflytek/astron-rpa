<script setup lang="ts">
import BackButton from './BackButton.vue'
import InviteHeader from './InviteHeader.vue'
import AgreementTxt from './AgreementTxt.vue'

defineProps<{
  wrapClass?: string
  showBack?: boolean
  showAgreement?: boolean
  targetName?: string
  userName?: string
  type?: 'market' | 'enterprise'
}>()

const emit = defineEmits<{
  back: []
  action: []
}>()
</script>
<template>
  <div class="invite-form-layout relative bg-[#ffffff] dark:bg-[#000000] rounded-[16px] w-[400px] h-[auto] p-[40px]" :class="wrapClass">
    <BackButton v-if="showBack" @click="() => emit('back')" />

    <slot name="header">
      <InviteHeader v-if="userName && targetName" :type="type" :userName="userName" :targetName="targetName" />
    </slot>

    <div class="h-[calc(100%-32px)]">
      <slot />
    </div>

    <AgreementTxt v-if="showAgreement" :type="'invite'" />
  </div>
</template>

