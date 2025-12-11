<script setup lang="ts">
import { ref } from 'vue'
import type { TenantItem } from '../../interface'
import TenantItemComponent from '../Base/TenantItem.vue'
import Loading from '../Base/Loading.vue'
import { Dropdown, Menu, message } from 'ant-design-vue'
import { tenantList, switchTenant } from '../../api/login'
import { getSelectedTenant } from '../../utils/remember'
import TenantUpgradeBtn from '../Base/TenantUpgradeBtn.vue'

const tenants = ref<TenantItem[]>([])

const { beforeSwitch } = defineProps<{
  beforeSwitch?: () => Promise<void> | void
}>()

const emit = defineEmits<{
  switchTenant: [tenant: TenantItem]
}>()

const loadingRef = ref<InstanceType<typeof Loading>>()
const selectedTenant = ref<TenantItem | null>(null)

const getTenants = async () => {
  const data = await tenantList()
  tenants.value = data
  const selectedId = getSelectedTenant()
  const matchedTenant = tenants.value.find(tenant => tenant.id === selectedId)
  if(!matchedTenant) {
    toggleTenant(tenants.value[0])
    return
  }
  selectedTenant.value = matchedTenant
  emit('switchTenant', matchedTenant)
}

getTenants()

const toggleTenant = async (tenant: TenantItem) => {
  if(selectedTenant.value?.id === tenant.id) {
    return
  }
  if(beforeSwitch) {
    await beforeSwitch()
  }
  selectedTenant.value = tenant
  loadingRef.value?.isLoading({ isLoading: true, text: '环境加载中', timeout: 200 })
  try {
    await switchTenant({ tenantId: tenant.id })
  } catch (e) {
    loadingRef.value?.isLoading({ isLoading: false, immediate: true })
    return
  }
  await emit('switchTenant', tenant)
  loadingRef.value?.isLoading({ isLoading: false, immediate: true })
}

const open = ref(false)
</script>

<template>
  <div class="w-full px-[20px] tenant-dropdown relative">
    <!-- TODO 专业版申请 -->
    <!-- <TenantUpgradeBtn v-if="selectedTenant?.tenantType === 'personal'" class="absolute top-[-60px] left-0" /> -->
    <Dropdown placement="bottom" v-model:open="open">
      <div class="relative">
        
        <TenantItemComponent
          :custom-class="`!border-0 !mb-0 ${open ? '!bg-[#00000008] dark:!bg-[#FFFFFF08]' : 'dark:!bg-[transparent]'}`"
          v-if="selectedTenant"
          :right-icon="open ? 'tenant-arrow-down': 'tenant-arrow-up'"
          :tenant-item="selectedTenant"
         />
      </div>
      <template #overlay>
        <Menu class="tenant-dropdown-menu !p-0 !rounded-[12px] !p-[8px]">
          <Menu.Item 
            v-for="(tenant, idx) in tenants" 
            :key="tenant.id" 
            class="text-[14px] text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)] !p-[0] hover:!bg-[transparent]" 
            >
            <TenantItemComponent
              :custom-class="`!border-0 ${idx === tenants.length -1 ? '!mb-0' : '!mb-[8px] '} ${selectedTenant?.id ===  tenant.id ? '!bg-[#F3F3F7] dark:!bg-[#FFFFFF14]' : 'dark:!bg-[transparent]'}`"
              :tenant-item="tenant"
              :right-icon="selectedTenant?.id ===  tenant.id ? 'checked' : ''"
              @click="() => toggleTenant(tenant)"
            />
          </Menu.Item>
          <!-- TODO 专业版申请 -->
          <!-- <Menu.Item class="!border-0 !p-[0] !mt-[8px]">
            <TenantUpgradeBtn :button-type="'button'" />
          </Menu.Item> -->
        </Menu>
       </template>
    </Dropdown>
    <Loading ref="loadingRef" />
  </div>
</template>
