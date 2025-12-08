<script setup lang="ts">
import { ref } from 'vue'
import type { TenantItem } from '../../interface'
import TenantItemComponent from '../Base/TenantItem.vue'
import CreateTenantModal from './CreateTenantModal.vue'
import { Dropdown, Button } from 'ant-design-vue'
import { useRegisterForm } from './hooks/useRegisterForm.ts'
import type { RegisterMode, PersonalRegisterFormData, EnterpriseRegisterFormData } from '../../interface.ts'
import { registerProps } from '../../interface.ts'
 
const props = defineProps({
  tenants: { type: Array as () => TenantItem[], default: () => [] },
  selectedTenant: { type: Object as () => TenantItem, default: null },
  ...registerProps()
})
const emit = defineEmits<{
  submit: [data: PersonalRegisterFormData | EnterpriseRegisterFormData, mode: RegisterMode]
  switchToLogin: []
  sendCaptcha: [phone: string]
  toggleTenant: [tenantId: string]
}>()

const personal = useRegisterForm('personal', emit as any)
const enterprise = useRegisterForm('enterprise', emit as any)

const currentMode = ref<RegisterMode>('personal')

const changeMode = () => {
  const next: RegisterMode = currentMode.value === 'personal' ? 'enterprise' : 'personal'
  next === 'enterprise' ? personal.resetForm() : enterprise.resetForm()
  console.log('dddd')
  currentMode.value = next
}

 
const selectedTenant = ref<TenantItem | null>(props.selectedTenant)
function toggleTenant (tenant: TenantItem) {
  selectedTenant.value = tenant
  emit('toggleTenant', tenant.id)
}
const showModal = ref(false)
const createTenantModal = async () => {
  showModal.value = true
}
</script>

<template>
  <div class="bg-[#ffffff] w-[200px]">
    <Button type="primary" block @click="createTenantModal()">
      创建新的空间
    </Button>
    <Dropdown placement="bottom" :trigger="['click']">
      <TenantItemComponent
        v-if="selectedTenant"
        :is-active="true"
        :tenant-item="selectedTenant"
      />
      <template #overlay>
        <div class="bg-[#ffffff]">
          <TenantItemComponent
            :key="tenant.id"
            v-for="tenant in tenants"
            :is-active="selectedTenant?.id ===  tenant.id "
            :tenant-item="tenant"
            @click="() => toggleTenant(tenant)"
          />
          
        </div>
      </template>
    </Dropdown>
    <CreateTenantModal :show-modal="showModal" />
  </div>
</template>
