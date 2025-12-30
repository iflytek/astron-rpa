<script setup lang="ts">
import { Dropdown, Menu } from 'ant-design-vue'
import { ref } from 'vue'

import { switchTenant, tenantList } from '../../api/login'
import type { TenantItem } from '../../interface'
import { getSelectedTenant } from '../../utils/remember'
import Consult from '../Base/Consult/Index.vue'
import Loading from '../Base/Loading.vue'
import TenantItemComponent from '../Base/TenantItem.vue'

const { beforeSwitch } = defineProps<{
  beforeSwitch?: () => Promise<void> | void
}>()

const emit = defineEmits<{
  switchTenant: [tenant: TenantItem]
}>()

const tenants = ref<TenantItem[]>([])

const loadingRef = ref<InstanceType<typeof Loading>>()
const selectedTenant = ref<TenantItem | null>(null)

async function getTenants() {
  const data = await tenantList()
  tenants.value = data
  const selectedId = getSelectedTenant()
  const matchedTenant = tenants.value.find(tenant => tenant.id === selectedId)
  if (!matchedTenant) {
    tenants.value[0] && toggleTenant(tenants.value[0])
    return
  }
  selectedTenant.value = matchedTenant
  emit('switchTenant', matchedTenant)
}

getTenants()

async function toggleTenant(tenant: TenantItem) {
  if (selectedTenant.value?.id === tenant.id) {
    return
  }
  if (beforeSwitch) {
    await beforeSwitch()
  }
  loadingRef.value?.isLoading({ isLoading: true, text: '环境加载中', timeout: 200 })
  try {
    await switchTenant({ tenantId: tenant.id })
  }
  catch (e) {
    console.log(e)
    loadingRef.value?.isLoading({ isLoading: false, immediate: true })
    return
  }
  selectedTenant.value = tenant
  await emit('switchTenant', tenant)
  loadingRef.value?.isLoading({ isLoading: false, immediate: true })
}

const open = ref(false)
</script>

<template>
  <div class="w-full px-[20px] tenant-dropdown relative">
    <Consult v-if="selectedTenant?.tenantType === 'personal'" trigger="button" :button-conf="{ buttonType: 'tag' }" class="!w-[calc(100%-40px)] absolute top-[-60px] left-[20px]" />
    <Dropdown v-model:open="open" placement="bottom">
      <div class="relative">
        <TenantItemComponent
          v-if="selectedTenant"
          :custom-class="`!border-0 !mb-0 ${open ? '!bg-[#00000008] dark:!bg-[#FFFFFF08]' : 'dark:!bg-[transparent]'}`"
          :right-icon="open ? 'tenant-arrow-down' : 'tenant-arrow-up'"
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
              :custom-class="`!border-0 ${idx === tenants.length - 1 ? '!mb-0' : '!mb-[8px] '} ${selectedTenant?.id === tenant.id ? '!bg-[#F3F3F7] dark:!bg-[#FFFFFF14]' : 'dark:!bg-[transparent]'}`"
              :tenant-item="tenant"
              :right-icon="selectedTenant?.id === tenant.id ? 'checked' : ''"
              @click="() => toggleTenant(tenant)"
            />
          </Menu.Item>
          <Menu.Item class="!border-0 !p-[0] !mt-[8px]">
            <Consult trigger="button" :button-conf="{ buttonType: 'button', buttonTxt: '创建新的工作空间' }" :consult="{ consultTitle: '创建新的工作空间', consultType: 'consult' }" />
          </Menu.Item>
        </Menu>
      </template>
    </Dropdown>
    <Loading ref="loadingRef" />
  </div>
</template>
