<script setup lang="ts">
import { NiceModal } from '@rpa/components'

import { useAppConfigStore } from '@/stores/useAppConfig'

import bgImage from '@/assets/img/updater/bg.svg'
import iconImage from '@/assets/img/updater/icon.svg'
// import cloudLeftImage from '@/assets/img/updater/cloud-1.png'
// import cloudRightImage from '@/assets/img/updater/cloud-2.png'

const modal = NiceModal.useModal()
const appStore = useAppConfigStore()

interface UpdaterModalProps {
  needUpdate: boolean
  latestVersion: string
  updateNote?: string
}

const props = defineProps<UpdaterModalProps>()

const handleClose = () => modal.hide()

const handleQuitAndInstall = () => appStore.quitAndInstall()

const handleRejectUpdate = () => {
  appStore.rejectUpdate(props.latestVersion)
  handleClose()
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    class="updater-modal"
    :footer="null"
    :width="props.needUpdate ? 600 : 400"
  >
    <div class="h-[317px] w-full overflow-hidden relative">
      <img :src="bgImage" class="absolute top-0 left-0 w-[600px] h-full max-w-max" />
      <!-- <img :src="cloudLeftImage" class="absolute left-0 bottom-0" /> -->
      <!-- <img :src="cloudRightImage" class="absolute right-0 bottom-0" /> -->
    </div>

    <div class="absolute top-[60px] w-full flex flex-col items-center gap-2">
      <img :src="iconImage" class="w-[120px] h-[120px]" />
      <div class="text-[28px] font-semibold leading-[39px]">
        {{ props.needUpdate ? '发现新版本！' : '你使用的已是最新版本' }}
      </div>
      <div class="text-[14px] leading-5 text-text-secondary">
        {{ props.needUpdate ? `v${props.latestVersion} 体验全新升级，更新包已就绪` : `v${props.latestVersion}` }}
      </div>
    </div>

    <div v-if="props.updateNote && props.needUpdate" class="p-4">
      {{ props.updateNote }}
    </div>

    <div class="p-4 flex gap-[10px]">
      <template v-if="props.needUpdate">
        <div class="flex-1 action-button" @click="handleRejectUpdate">
          稍后更新
        </div>
        <div class="flex-1 action-button action-button__confirm" @click="handleQuitAndInstall">
          重启升级
        </div>
      </template>
      <div v-else class="flex-1 action-button action-button__confirm" @click="handleClose">
        好
      </div>
    </div>
  </a-modal>
</template>

<style lang="scss">
.updater-modal {
  .ant-modal-content {
    position: relative;
    padding: 0;
    overflow: hidden;
  }

  .action-button {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    height: 40px;
    background-color: #F3F3F7;
    font-size: 14px;
    font-style: normal;
    font-weight: 500;
    cursor: pointer;

    &:hover {
      opacity: 0.8;
    }
  }

  .action-button__confirm {
    background: linear-gradient(108deg, #599EFF 0%, #726FFF 30.23%, #856FFF 56.48%, #986ADC 98.95%);
    color: #fff;
  }
}
</style>
