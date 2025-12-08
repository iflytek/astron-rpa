<script setup lang="ts">
import type { TenantItem } from '../../interface'
import { Icon as RpaIcon } from '../../../Icon'

const props = defineProps({
  isActive: { type: Boolean, default: false },
  tenantItem: { type: Object as () => TenantItem, required: true },
})

const tenantType = {
  0: '个人版',
  1: '企业版',
}

const emit = defineEmits<{
  click: []
 }>()

function handleClick () {
  emit('click')
}
</script>

<template>
  <div
    :class="[
      'relative flex items-center cursor-pointer px-[12px] py-[16px] mb-[12px] border rounded-[12px] hover:border-[#6366f1]/50',
      isActive 
        ? 'border-[#6366f1] bg-[#6366f1]/5' 
        : 'border-[#e5e7eb] dark:border-[#4B556380] hover:border-[#6366f1]/50'
    ]"
    @click="handleClick"
  >
    <span class="w-[40px] h-[40px] text-center leading-[40px] bg-[#6366f1] rounded-[8px] text-[18px] text-[#ffffff] mr-[12px]">
      {{ tenantItem.name.substring(0, 1) }}
    </span>
    <div class="text-[#000000A6] dark:text-[#FFFFFFD9]">
      <div class="text-[14px] ">
        {{ tenantItem.name }}
      </div>
      <span class="text-[12px] text-[#6b7280] dark:text-[#9ca3af] inline-block px-[8px] h-[22px] leading-[20px] bg-[#00000005] border border-[#D9D9D9] dark:border-[#4B556380] rounded-[4px]">{{ tenantType[tenantItem.type as keyof typeof tenantType] }}</span>
      <RpaIcon class="absolute right-[12px] top-[50%] transform -translate-y-1/2 dark:text-[#FFFFFFD9]" name="right" />
    </div>
  </div>
</template>
