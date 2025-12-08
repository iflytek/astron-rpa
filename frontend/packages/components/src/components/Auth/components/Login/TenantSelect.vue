<script setup lang="ts">
import { ref } from 'vue'
import FormLayout from '../Base/FormLayout.vue'
import type { TenantItem } from '../../interface'
import { Icon as RpaIcon } from '../../../Icon'

const props = defineProps({
  loading: { type: Boolean, default: false },
  tenants: { type: Array as () => TenantItem[], default: () => [] },
})

const tenantType = {
  0: '个人版',
  1: '企业版',
}

const emit = defineEmits<{
  submit: [tenantId: string]
  switchToLogin: []
}>()

// 表单数据
const selectedTenant = ref('')
function handleSelect (tenant: TenantItem) {
  selectedTenant.value = tenant.id
  emit('submit', tenant.id)
}
</script>

<template>
  <FormLayout
    :wrap-class="'auth-tenant-select h-full relative'"
    title="请选择空间"
    :sub-title="'您的账号与下列空间有关联，可进入任一空间'"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <div class="mt-[-12px] max-h-[calc(100%-80px)] overflow-y-auto pr-[4px]">
      <div
        v-for="tenant in tenants"
        :key="tenant.id"
        :class="[
          'relative flex items-center cursor-pointer px-[12px] py-[16px] mb-[12px] border rounded-[12px] hover:border-[#6366f1]/50',
          selectedTenant === tenant.id 
            ? 'border-[#6366f1] bg-[#6366f1]/5' 
            : 'border-[#e5e7eb] dark:border-[#4B556380] hover:border-[#6366f1]/50'
        ]"
        @click="handleSelect(tenant)"
      >
        <span class="w-[40px] h-[40px] text-center leading-[40px] bg-[#6366f1] rounded-[8px] text-[18px] text-[#ffffff] mr-[12px]">
          {{ tenant.name.substring(0, 1) }}
        </span>
        <div class="text-[#000000A6] dark:text-[#FFFFFFD9]">
          <div class="text-[14px] ">
            {{ tenant.name }}
          </div>
          <span class="text-[12px] text-[#6b7280] dark:text-[#9ca3af] inline-block px-[8px] h-[22px] leading-[20px] bg-[#00000005] border border-[#D9D9D9] dark:border-[#4B556380] rounded-[4px]">{{ tenantType[tenant.type as keyof typeof tenantType] }}</span>
          <RpaIcon class="absolute right-[12px] top-[50%] transform -translate-y-1/2 dark:text-[#FFFFFFD9]" name="right" />
        </div>
      </div>
    </div>
  </FormLayout>
</template>
