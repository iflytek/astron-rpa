<script setup lang="ts">
import { Button, Modal } from 'ant-design-vue'
import { ref } from 'vue'

import { Icon as RpaIcon } from '../../../../Icon'

import ConsultModal from './ConsultModal.vue'

const props = defineProps({
  trigger: {
    type: String as () => 'button' | 'modal',
    default: 'button',
  },
  buttonConf: {
    type: Object as () => {
      buttonType: 'tag' | 'text' | 'button'
      buttonTxt?: string
      currentEdition?: 'personal' | 'professional' | 'enterprise'
      expirationDate?: string
      shouldAlert?: boolean
    } | undefined,
    default: undefined,
  },
  customClass: {
    type: String,
    default: undefined,
  },
  modalConfirm: {
    type: Object as () => {
      title: string
      content: string
      okText: string
      cancelText: string
    } | undefined,
    default: undefined,
  },
  consult: {
    type: Object as () => {
      consultTitle?: string
      consultEdition?: 'professional' | 'enterprise'
      consultType: 'consult' | 'renewal'
    } | undefined,
    default: undefined,
  },
})

const tenantTypeMap = {
  personal: '个人免费版',
  professional: '专业版',
  enterprise: '企业版',
}

const confData = ref(props)
const consultModalRef = ref<InstanceType<typeof ConsultModal> | null>(null)
function openModal() {
  consultModalRef.value?.showModal()
}

function init(config: typeof props) {
  confData.value = config
  if (confData.value.trigger === 'modal') {
    Modal.confirm({
      ...confData.value.modalConfirm!,
      onOk() {
        openModal()
      },
    })
  }
}

defineExpose({
  init,
})
</script>

<template>
  <div class="w-full" :class="confData?.customClass">
    <template v-if="confData?.trigger === 'button'">
      <div
        v-if="confData?.buttonConf?.buttonType === 'tag'"
        class="tenant-upgrade-tag cursor-pointer flex items-center justify-start text-gradient-bg text-upgrader-bg !rounded-[12px] !min-h-[56px] !w-full !text-[14px] hover:!opacity-90"
      >
        <div v-if="confData?.buttonConf?.currentEdition && confData?.buttonConf?.currentEdition !== 'personal'">
          <div class="w-[fit-content] h-[22px] leading-[22px] font-bold">
            <span class="text-gradient">{{ tenantTypeMap[confData?.buttonConf?.currentEdition] }}</span>
          </div>
          <span v-if="confData?.buttonConf?.expirationDate" class="text-[12px] mt-[4px]">
            到期时间： {{ confData?.buttonConf?.expirationDate }}
            <span v-if="confData?.buttonConf?.shouldAlert" class="bg-[#ec483e] text-white px-[6px] py-[1px] !text-[12px] rounded-[3px]">即将到期</span>
          </span>
        </div>
        <div v-else class="w-full text-left" @click="openModal">
          <div v-if="confData?.buttonConf?.currentEdition" class="w-[fit-content] h-[22px] leading-[22px] font-bold">
            <span class="text-gradient">{{ tenantTypeMap[confData?.buttonConf?.currentEdition] }}</span>
          </div>
          <div class="flex items-center justify-start" :class="confData?.buttonConf?.currentEdition ? 'text-[12px] mt-[2px]' : ''">
            <RpaIcon class="w-[26px] h-[26px] mr-[8px]" :class="confData?.buttonConf?.currentEdition ? '!w-[20px] !h-[20px] !mr-[4px]' : ''" name="upgrade-icon" />
            <span class="text-gradient">{{ confData?.buttonConf?.buttonTxt || '开通专业版/企业版' }}</span>
          </div>
        </div>
      </div>
      <span v-else-if="confData?.buttonConf?.buttonType === 'text'" @click="openModal">{{ confData?.buttonConf?.buttonTxt }}</span>
      <Button v-else type="primary" ghost block class="border !border-[#0000001A] dark:!border-[#FFFFFF29]" @click="openModal">
        <span class="!flex items-center justify-center text-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
          <RpaIcon class="w-[16px] h-[16px] mr-[4px]" name="python-package-plus" />
          <span>{{ confData?.buttonConf?.buttonTxt || '创建新的空间' }}</span>
        </span>
      </Button>
    </template>
    <ConsultModal ref="consultModalRef" v-bind="confData?.consult" />
  </div>
</template>
