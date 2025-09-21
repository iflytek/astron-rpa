<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { ref } from 'vue'

import { utilsManager } from '@/platform'

const { stepImgs, stepInfo } = defineProps<{
  stepImgs: Array<string>
  stepInfo: Array<string>
}>()

const modal = NiceModal.useModal()
const step = ref(0)

function nextOrPrevStep(forward: number = 1) {
  step.value += forward
}

function openPluginFolder() {
  utilsManager.openPlugins()
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    class="pluginTipModal"
    :z-index="101"
    :width="700"
    :mask-closable="false"
    title="提示"
  >
    <template #footer>
      <a-button v-if="step > 0" @click="() => { nextOrPrevStep(-1) }">
        上一步
      </a-button>
      <a-button v-if="step < stepImgs.length - 1" @click="() => { nextOrPrevStep(1) }">
        下一步
      </a-button>
      <a-button v-if="step === stepImgs.length - 1" @click="openPluginFolder">
        打开插件路径
      </a-button>
      <a-button type="primary" @click="modal.hide">
        完成
      </a-button>
    </template>
    <div class="pluginTipModal-tip">
      {{ stepInfo[step] }}
    </div>
    <div class="pluginTipModal-content">
      <div class="updateImage">
        <img :src="`images/pluginInstall/${stepImgs[step]}`">
      </div>
    </div>
  </a-modal>
</template>

<style lang="scss" scoped>
.pluginTipModal {
  .ant-modal {
    top: 60px;
    padding-bottom: 0;
  }

  .ant-modal-body {
    height: 368px;
    overflow-x: hidden;
    overflow-y: auto;
    padding: 16px 20px;
  }

  &-tip {
    margin-bottom: 5px;
    font-size: $font-size;
    font-weight: bold;
  }

  &-content {
    .item {
      width: 100%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      margin-bottom: 5px;
    }
  }

  .updateImage {
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: #e2e2e2 0px 0px 5px;
  }
}
</style>
