<script setup lang="ts">
import { ref } from 'vue'
import FormLayout from '../Base/FormLayout.vue'
import TenantItemComponent from '../Base/TenantItem.vue'
import type { TenantItem, InviteInfo } from '../../interface'

const props = defineProps({
  loading: { type: Boolean, default: false },
  tenants: { type: Array as () => TenantItem[], default: () => [] },
  inviteInfo: { type: Object as () => InviteInfo, default: () => null },
})

const emit = defineEmits<{
  submit: [tenantId: string]
  switchToLogin: []
}>()

const selectedTenant = ref('')
function handleSelect (tenant: TenantItem) {
  selectedTenant.value = tenant.id
  emit('submit', tenant.id)
}
</script>

<template>
  <FormLayout
    :wrap-class="'auth-tenant-select h-full relative'"
    :title="inviteInfo ? '请选择关联的空间' : ' 请选择空间'"
    :sub-title="inviteInfo ? '关联后即可在团队市场中共享和使用该空间的资产' : '您的账号与下列空间有关联，可进入任一空间'"
    show-back
    @back="() => emit('switchToLogin')"
  >
    <div class="mt-[-12px] max-h-[calc(100%-40px)] overflow-y-auto pr-[4px]">
      <TenantItemComponent
        :key="tenant.id"
        v-for="tenant in tenants"
        :is-active="selectedTenant ===  tenant.id "
        :tenant-item="tenant"
        @click="() => handleSelect(tenant)"
      />
    </div>
  </FormLayout> 
</template>
