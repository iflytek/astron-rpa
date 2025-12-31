<script setup lang="ts">
import { ref } from 'vue'

import type { InviteInfo, TenantItem } from '../../interface'
import Consult from '../Base/Consult/Index.vue'
import FormLayout from '../Base/FormLayout.vue'
import TenantItemComponent from '../Base/TenantItem.vue'

const { tenants, inviteInfo } = defineProps({
  tenants: { type: Array as () => TenantItem[], default: () => [] },
  inviteInfo: { type: Object as () => InviteInfo, default: () => null },
})

const emit = defineEmits<{
  submit: [tenantId: string]
  switchToLogin: []
}>()

const tenantTypeMap = {
  personal: '个人免费版',
  professional: '专业版',
  enterprise: '企业版',
}
const selectedTenant = ref('')
const consultRef = ref<InstanceType<typeof Consult> | null>(null)

function handleSelect(tenant: TenantItem) {
  selectedTenant.value = tenant.id
  if (tenant.isExpired) {
    consultRef.value?.init({
      trigger: 'modal',
      modalConfirm: {
        title: '租户已过期',
        content: `该${tenantTypeMap[tenant.tenantType]}空间已到期，请续费办理`,
        okText: '咨询办理',
        cancelText: '我知道了',
      },
      consult: {
        consultTitle: `续费`,
        consultEdition: tenant.tenantType as 'professional' | 'enterprise',
        consultType: 'renewal',
      },
    })
    return
  }
  emit('submit', tenant.id)
}
</script>

<template>
  <FormLayout
    wrap-class="auth-tenant-select h-full relative"
    :title="inviteInfo ? '请选择关联的空间' : ' 请选择空间'"
    :sub-title="inviteInfo ? '关联后即可在团队市场中共享和使用该空间的资产' : '您的账号与下列空间有关联，可进入任一空间'"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <div class="mt-[-12px] max-h-[calc(100%-40px)] overflow-y-auto pr-[4px]">
      <TenantItemComponent
        v-for="tenant in tenants"
        :key="tenant.id"
        :is-active="selectedTenant === tenant.id "
        :tenant-item="tenant"
        @click="() => handleSelect(tenant)"
      />
    </div>
    <Consult ref="consultRef" trigger="modal" />
  </FormLayout>
</template>
