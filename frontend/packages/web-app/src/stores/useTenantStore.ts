import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { TenantItem } from '@rpa/components/auth'

export const useTenantStore = defineStore('tenant', () => {
  const currentTenant = ref<TenantItem | null>(null) // 当前租户

  const setCurrentTenant = (val: TenantItem | null) => {
    console.log('setCurrentTenant', val)
    currentTenant.value = val
  }

  return {
    setCurrentTenant,
    currentTenant,
  }
})
