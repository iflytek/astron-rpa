<script setup lang="ts">
import { ToolOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { Empty, Spin } from 'ant-design-vue'

import useVersionManage from './useVersionManage'

const props = defineProps<{ robotId: string }>()

const emit = defineEmits(['refresh'])

const modal = NiceModal.useModal()
const {
  spinning,
  versionLst,
  getVersionDes,
  getTimeDes,
  publish,
  recoverEdit,
  enableVersion,
} = useVersionManage(props)

const CURRENT_VERSION_VALUE = 0

function handleClose() {
  emit('refresh')
  modal.hide()
}

function handleAfterOpenChange(v: boolean) {
  if (!v) {
    modal.resolveHide()
    modal.remove()
  }
}
</script>

<template>
  <a-drawer
    :open="modal.visible"
    class="versionHistoryModal"
    :width="560"
    title="版本管理"
    :footer="null"
    @close="handleClose"
    @after-open-change="handleAfterOpenChange"
  >
    <div v-if="spinning" class="versionHistoryModal-spin">
      <Spin />
    </div>
    <template v-else>
      <div v-if="versionLst?.length" class="versionHistory w-[496px]">
        <div v-for="version, index in versionLst" :key="index" class="border-b border-[rgba(0,0,0,0.10)] dark:border-[rgba(255,255,255,0.10)] flex flex-col justify-between pb-[20px] mb-[16px]">
          <div class="header flex justify-between items-center my-[8px]">
            <div class="header-left-info h-[22px] flex justify-start text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]">
              <div class="mr-[8px] h-[22px] leading-[22px] text-[16px] font-semibold">
                {{ getVersionDes(version.versionNum) }}
              </div>
              <div v-if="['enable'].includes(version.online)" class="w-[52px] h-[22px] flex items-center justify-center rounded-[4px] bg-[#e6f4ff] dark:bg-[#111a2c] text-[#726fff]">
                启用中
              </div>
              <div v-if="version.versionNum === CURRENT_VERSION_VALUE" class="w-[52px] h-[22px] flex items-center justify-center rounded-[4px] bg-[#fff7e6] dark:bg-[#2b1d11] text-[#fa8c16] dark:text-[#d87a16]">
                编辑中
              </div>
            </div>
            <div class="header-right-tools flex items-center">
              <a-button v-if="version.versionNum === CURRENT_VERSION_VALUE" class="flex items-center cursor-pointer" @click="() => { publish(version) }">
                <rpa-icon name="publish" class="mr-[5px]" />发版
              </a-button>
              <a-button v-else class="flex items-center cursor-pointer ml-[8px]" @click="() => { recoverEdit(version) }">
                <rpa-icon name="edit" class="mr-[5px]" />恢复编辑
              </a-button>
              <a-button v-if="version.online === 'disable' && version.versionNum !== CURRENT_VERSION_VALUE" class="cursor-pointer ml-[8px]" @click="() => { enableVersion(version) }">
                <div><ToolOutlined class="mr-[5px]" />启用版本</div>
              </a-button>
            </div>
          </div>
          <div class="time h-[24px] leading-[24px] font-normal text-[12px] text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)] mb-[8px]">
            {{ getTimeDes(version.updateTime) }}
          </div>
          <div class="desc max-h-[71px] text-[12px] leading-6 text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)] overflow-hidden text-ellipsis line-clamp-3 ">
            <a-tooltip :title="version?.updateLog || '暂无描述信息'">
              {{ version?.updateLog || '暂无描述信息' }}
            </a-tooltip>
          </div>
        </div>
      </div>
      <div v-else class="versionHistoryModal-default">
        <Empty />
      </div>
    </template>
  </a-drawer>
</template>

<style lang="scss">
@import './index.scss';
</style>
