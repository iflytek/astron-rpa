<script setup lang="ts">
import { Button, Modal } from 'ant-design-vue'
import { ref, watch } from 'vue'

import { Icon as RpaIcon } from '../../../../Icon'
import type { AuthType } from '../../../interface'

import ConsultModal from './ConsultModal.vue'
import ConsultUpgradeTrigger from './ConsultUpgradeTrigger.vue'

type TriggerType = 'button' | 'modal'

interface ButtonConf {
  buttonType: 'tag' | 'text' | 'button'
  buttonTxt?: string
  currentEdition?: 'personal' | 'professional' | 'enterprise'
  expirationDate?: string
  shouldAlert?: boolean
}

interface ModalConfirmConf {
  title: string
  content: string
  okText: string
  cancelText: string
}

interface ConsultConf {
  consultTitle?: string
  consultEdition?: 'professional' | 'enterprise'
  consultType: 'consult' | 'renewal'
}

interface Props {
  /** 仅挂载咨询弹窗，由外部通过 ref.openModal() 打开（与触发器 UI 解耦） */
  modalOnly?: boolean
  authType?: AuthType
  trigger?: TriggerType
  buttonConf?: ButtonConf
  customClass?: string
  modalConfirm?: ModalConfirmConf
  consult?: ConsultConf
}

const props = withDefaults(defineProps<Props>(), {
  modalOnly: false,
  authType: 'uap',
  trigger: 'button',
})

const confData = ref(props)

watch(
  () => props,
  (p) => {
    if (p.modalOnly)
      confData.value = { ...p }
  },
  { deep: true },
)

const consultModalRef = ref<InstanceType<typeof ConsultModal> | null>(null)

function openModal() {
  if (confData.value.authType !== 'casdoor')
    consultModalRef.value?.showModal()
}

function init(config: Omit<Props, 'modalOnly'>) {
  confData.value = { modalOnly: false, ...config }
  if (confData.value.trigger === 'modal') {
    Modal.confirm({
      ...confData.value.modalConfirm!,
      onOk: () => openModal(),
    })
  }
}

defineExpose({
  init,
  openModal,
})
</script>

<template>
  <template v-if="modalOnly">
    <ConsultModal ref="consultModalRef" v-bind="confData?.consult" />
  </template>
  <div v-else class="w-full" :class="confData?.customClass">
    <template v-if="confData?.trigger === 'button'">
      <ConsultUpgradeTrigger
        v-if="confData?.buttonConf?.buttonType === 'tag'"
        :auth-type="confData.authType"
        :button-conf="confData.buttonConf"
        @open="openModal"
      />
      <span v-else-if="confData?.buttonConf?.buttonType === 'text'" @click="openModal">{{ confData?.buttonConf?.buttonTxt }}</span>
      <Button v-else type="primary" ghost block class="border !border-[#0000001A] dark:!border-[#FFFFFF29]" @click="openModal">
        <span class="!flex items-center justify-center text-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]">
          <RpaIcon class="w-[16px] h-[16px] mr-[4px]" name="python-package-plus" />
          <span>{{ confData?.buttonConf?.buttonTxt || $t('components.auth.createWorkspace') }}</span>
        </span>
      </Button>
    </template>
    <ConsultModal ref="consultModalRef" v-bind="confData?.consult" />
  </div>
</template>
