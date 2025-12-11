<script setup lang="ts">
import { ref } from 'vue';
import { Icon as RpaIcon } from '../../../Icon'
import { Button } from 'ant-design-vue'
import CreateTenantModal from './CreateTenantModal.vue'

interface Props {
  buttonType?: 'tag' | 'button'
  customClass?: string
}

const { buttonType = 'tag', customClass = '' } = defineProps<Props>()

const createTenantModalRef = ref<InstanceType<typeof CreateTenantModal> | null>(null)
const createTenantModal = () => {
  createTenantModalRef.value?.showModal()
}
 
</script>

<template>
  <div class="w-full tenant-upgrade-btn" :class="customClass">
    <div
      v-if="buttonType === 'tag'"
      class="tenant-upgrade-tag flex items-center justify-start cursor-pointer text-gradient-bg text-upgrader-bg !rounded-[12px] !h-[56px] !leading-[56px] !w-full text-center !text-[14px] !px-[18px] hover:!opacity-90"
      @click="createTenantModal()"
    >
      <RpaIcon class="w-[26px] h-[26px] mr-[8px]" name="upgrade-icon" />
      <span class="text-gradient">升级为专业版</span>
    </div>
    <Button v-else type="primary" ghost block class="border !border-[#0000001A] dark:!border-[#FFFFFF29]" @click="createTenantModal()">
      <span class="!flex items-center justify-center text-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
        <RpaIcon class="w-[16px] h-[16px] mr-[4px]" name="python-package-plus"/>
        <span>创建新的空间</span>
      </span>
    </Button>
    <CreateTenantModal ref="createTenantModalRef" />
  </div>
</template>
