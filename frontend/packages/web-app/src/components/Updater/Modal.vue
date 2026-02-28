<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { StyleValue } from 'vue'

import bgImage from '@/assets/img/updater/bg.svg'
import cloudRightImage from '@/assets/img/updater/cloud-1.webp'
import cloudLeftImage from '@/assets/img/updater/cloud-2.webp'
import iconImage from '@/assets/img/updater/icon.svg'
import { useAppConfigStore } from '@/stores/useAppConfig'

const props = defineProps<UpdaterModalProps>()
const modal = NiceModal.useModal()
const appStore = useAppConfigStore()

interface UpdaterModalProps {
  needUpdate: boolean
  latestVersion: string
  updateNote?: string
}

const handleClose = () => modal.hide()

const handleQuitAndInstall = () => appStore.quitAndInstall()

function handleRejectUpdate() {
  appStore.rejectUpdate(props.latestVersion)
  handleClose()
}

function genCloudStyle(imgUrl: string): StyleValue {
  return {
    background: `url(${imgUrl}) lightgray 50% / cover no-repeat`,
    mixBlendMode: 'screen',
    filter: 'blur(2.0677084922790527px)',
  }
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
      <img :src="bgImage" class="absolute top-0 left-0 w-[600px] h-full max-w-max">
      <rpa-star-motion class="absolute w-full h-full left-0 top-0" />
      <div class="absolute -left-[125px] -bottom-[49.82px] w-[303.953px] h-[202.635px] aspect-[3/2]" :style="genCloudStyle(cloudLeftImage)" />
      <div class="absolute -right-[49px] -bottom-[65px] w-[268px] h-[214px] aspect-[134/107]" :style="genCloudStyle(cloudRightImage)" />
    </div>

    <div class="absolute top-[60px] w-full flex flex-col items-center gap-2">
      <img :src="iconImage" class="w-[120px] h-[120px]">
      <div class="text-[28px] font-semibold leading-[39px]">
        {{ props.needUpdate ? $t('updater.newVersionFound') : $t('updater.alreadyLatest') }}
      </div>
      <div class="text-[14px] leading-5 text-text-secondary">
        {{ props.needUpdate ? `v${props.latestVersion} ${$t('updater.updateReady')}` : `v${props.latestVersion}` }}
      </div>
    </div>

    <div v-if="props.updateNote && props.needUpdate" class="p-4">
      {{ props.updateNote }}
    </div>

    <div class="p-4 flex gap-[10px]">
      <template v-if="props.needUpdate">
        <div class="flex-1 action-button" @click="handleRejectUpdate">
          {{ $t('updater.updateLater') }}
        </div>
        <div class="flex-1 action-button action-button__confirm" @click="handleQuitAndInstall">
          {{ $t('updater.restartToUpgrade') }}
        </div>
      </template>
      <div v-else class="flex-1 action-button action-button__confirm" @click="handleClose">
        {{ $t('updater.ok') }}
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
    background-color: #f3f3f7;
    font-size: 14px;
    font-style: normal;
    font-weight: 500;
    cursor: pointer;

    &:hover {
      opacity: 0.8;
    }
  }

  .action-button__confirm {
    background: linear-gradient(108deg, #599eff 0%, #726fff 30.23%, #856fff 56.48%, #986adc 98.95%);
    color: #fff;
  }
}
</style>
