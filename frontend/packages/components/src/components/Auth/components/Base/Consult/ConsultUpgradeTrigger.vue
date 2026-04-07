<script setup lang="ts">
import { Icon as RpaIcon } from '../../../../Icon'
import type { AuthType } from '../../../interface'

defineProps<{
  authType: AuthType
  buttonConf?: {
    buttonType: 'tag' | 'text' | 'button'
    buttonTxt?: string
    currentEdition?: 'personal' | 'professional' | 'enterprise'
    expirationDate?: string
    shouldAlert?: boolean
  }
}>()

const emit = defineEmits<{
  open: []
}>()

const tenantTypeMap: Record<'personal' | 'professional' | 'enterprise', string> = {
  personal: '个人免费版',
  professional: '专业版',
  enterprise: '企业版',
}

function onOpen() {
  emit('open')
}
</script>

<template>
  <div
    class="cursor-pointer flex items-center justify-start text-gradient-bg text-upgrader-bg !rounded-[12px] !w-full !text-[14px] hover:!opacity-90"
  >
    <div v-if="buttonConf?.currentEdition && buttonConf.currentEdition !== 'personal'">
      <div class="w-[fit-content] font-bold">
        <span class="text-gradient">{{ tenantTypeMap[buttonConf.currentEdition] }}</span>
      </div>
      <span v-if="buttonConf?.expirationDate" class="text-[12px] mt-[8px]">
        到期时间： {{ buttonConf.expirationDate }}
        <span
          v-if="buttonConf?.shouldAlert"
          class="bg-[#ec483e] text-white px-[6px] py-[1px] !text-[12px] rounded-[3px]"
        >即将到期</span>
      </span>
    </div>
    <div
      v-else
      class="w-full text-left"
      :class="{ 'min-h-[38px] leading-[38px]': !buttonConf?.currentEdition }"
      @click="onOpen"
    >
      <div v-if="buttonConf?.currentEdition" class="w-[fit-content] font-bold">
        <span class="text-gradient">{{ tenantTypeMap[buttonConf.currentEdition] }}</span>
      </div>
      <div
        v-if="authType !== 'casdoor'"
        class="flex items-center justify-start"
        :class="buttonConf?.currentEdition ? 'text-[12px] mt-[2px]' : ''"
      >
        <RpaIcon
          class="w-[26px] h-[26px] mr-[8px]"
          :class="buttonConf?.currentEdition ? '!w-[20px] !h-[20px] !mr-[4px]' : ''"
          name="upgrade-icon"
        />
        <span class="text-gradient">{{ buttonConf?.buttonTxt || '开通专业版/企业版' }}</span>
      </div>
    </div>
  </div>
</template>
