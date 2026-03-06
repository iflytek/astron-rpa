<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import { computed, ref } from 'vue'

import type { AuthType, InviteInfo, TenantItem } from '../../interface'
import Consult from '../Base/Consult/Index.vue'
import FormLayout from '../Base/FormLayout.vue'
import TenantItemComponent from '../Base/TenantItem.vue'

const { tenants, inviteInfo, authType } = defineProps({
  authType: { type: String as () => AuthType, default: () => 'uap' },
  tenants: { type: Array as () => TenantItem[], default: () => [] },
  inviteInfo: { type: Object as () => InviteInfo, default: () => null },
})

const emit = defineEmits<{
  submit: [tenantId: string]
  switchToLogin: []
}>()

const { t } = useTranslation()

const tenantTypeMap = computed<Record<string, string>>(() => ({
  personal: t('components.auth.personalFree'),
  professional: t('components.auth.professional'),
  enterprise: t('components.auth.enterprise'),
}))
const selectedTenant = ref('')
const consultRef = ref<InstanceType<typeof Consult> | null>(null)

function handleSelect(tenant: TenantItem) {
  selectedTenant.value = tenant.id
  if (tenant.isExpired) {
    consultRef.value?.init({
      authType,
      trigger: 'modal',
      modalConfirm: {
        title: t('components.auth.tenantExpired'),
        content: t('components.auth.tenantExpiredDesc', { type: tenantTypeMap.value[tenant.tenantType] }),
        okText: t('components.auth.consultHandle'),
        cancelText: t('components.auth.iKnow'),
      },
      consult: {
        consultTitle: t('components.auth.renewal'),
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
    :title="inviteInfo ? t('components.auth.selectRelatedSpace') : t('components.auth.selectSpace')"
    :sub-title="inviteInfo ? t('components.auth.relatedSpaceDesc') : t('components.auth.selectSpaceDesc')"
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
    <Consult ref="consultRef" trigger="modal" :auth-type="authType" />
  </FormLayout>
</template>
