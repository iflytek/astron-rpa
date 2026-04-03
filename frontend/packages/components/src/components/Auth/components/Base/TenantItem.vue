<script setup lang="ts">
import { Tooltip } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed } from 'vue'

import { Icon as RpaIcon } from '../../../Icon'
import type { TenantItem } from '../../interface'

const { isActive, tenantItem, customClass, rightIcon } = defineProps({
  isActive: { type: Boolean, default: false },
  tenantItem: { type: Object as () => TenantItem, required: true },
  customClass: { type: String, default: '' },
  rightIcon: { type: String, default: 'right' },
})

const emit = defineEmits<{
  click: []
}>()

const { t } = useTranslation()

const tenantTypeMap = computed<Record<string, string>>(() => ({
  personal: t('components.auth.personalFree'),
  professional: t('components.auth.professional'),
  enterprise: t('components.auth.enterprise'),
}))

function handleClick() {
  emit('click')
}
</script>

<template>
  <div
    class="tenant-item relative flex items-center cursor-pointer px-[12px] py-[8px] mb-[12px] border rounded-[12px] hover:border-[#6366f1]/50" :class="[
      customClass,
      isActive
        ? 'border-[#6366f1] bg-[#6366f1]/5'
        : 'border-[#e5e7eb] dark:border-[#4B556380] hover:border-[#6366f1]/50',
    ]"
    @click="handleClick"
  >
    <span class="w-[40px] h-[40px] text-center leading-[40px] bg-[#6366f1] rounded-[8px] text-[18px] text-[#ffffff] mr-[12px]">
      {{ tenantItem.name.substring(0, 1) }}
    </span>
    <div class="w-[calc(100%-40px)] text-[#000000D9] dark:text-[#FFFFFFD9]">
      <Tooltip :title="tenantItem.name" class="text-[14px] font-[500] mb-[4px] text-ellipsis inline-block whitespace-nowrap overflow-hidden max-w-[calc(100%-20px)]">
        {{ tenantItem.name }}
      </Tooltip>
      <div class="w-[fit-content] text-gradient-bg !py-[1px]">
        <span class="text-gradient">{{ tenantTypeMap[tenantItem.tenantType] }}</span>
      </div>
    </div>
    <RpaIcon class="absolute right-[13px] top-[50%] transform -translate-y-1/2" :name="rightIcon" />
  </div>
</template>
