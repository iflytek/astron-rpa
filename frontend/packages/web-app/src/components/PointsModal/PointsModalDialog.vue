<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { computed, ref } from 'vue'

import { useUserStore } from '@/stores/useUserStore'

import PointsModalHeader from './components/PointsModalHeader.vue'
import ConsumeDetailPanel from './components/panels/ConsumeDetailPanel.vue'
import OrderManagePanel from './components/panels/OrderManagePanel.vue'
import PointsManagePanel from './components/panels/PointsManagePanel.vue'
import type { PointsModalTabKey } from './types'

const props = withDefaults(
  defineProps<{
    workspaceName?: string
  }>(),
  {},
)

const modal = NiceModal.useModal()
const userStore = useUserStore()
const activeTab = ref<PointsModalTabKey>('manage')

const displayWorkspaceName = computed(
  () => props.workspaceName ?? userStore.currentTenant?.name ?? '星辰科技工作空间',
)

function handleClose() {
  modal.hide()
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :width="980"
    :footer="null"
    :closable="false"
    :z-index="1100"
    centered
    :body-style="{ padding: 0, overflow: 'hidden' }"
    wrap-class-name="points-modal-wrap"
    class="points-modal"
  >
    <div
      class="points-modal-inner flex h-full min-h-0 w-full min-w-0 flex-1 flex-col gap-6 overflow-hidden bg-white dark:bg-[#141414]"
    >
      <div class="shrink-0 px-6 pt-6">
        <PointsModalHeader v-model:active-tab="activeTab" @close="handleClose" />
      </div>

      <div
        v-if="activeTab === 'manage'"
        class="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden"
      >
        <PointsManagePanel
          class="min-h-0 flex-1"
          :workspace-name="displayWorkspaceName"
        />
      </div>
      <div
        v-else-if="activeTab === 'consume'"
        class="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden px-6 pb-6"
      >
        <ConsumeDetailPanel class="min-h-0 flex-1" />
      </div>
      <div
        v-else
        class="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden px-6 pb-6"
      >
        <OrderManagePanel class="min-h-0 flex-1" />
      </div>
    </div>
  </a-modal>
</template>

<style lang="scss">
/* 弹窗定高 980×680，wrap 上下留白；充值底栏在 PointsManagePanel 内贴内容区底全宽 */
.points-modal-wrap.ant-modal-wrap {
  align-items: center;
}

.points-modal-wrap .ant-modal {
  top: 0 !important;
  width: 980px !important;
  max-width: 980px;
  height: 680px;
  max-height: 680px;
  margin: 0 auto;
  padding-bottom: 0;
}

.points-modal-wrap .ant-modal-content {
  display: flex;
  height: 680px;
  max-height: 680px;
  flex-direction: column;
  padding: 0 !important;
  overflow: hidden;
}

.points-modal-wrap .ant-modal-body {
  display: flex;
  min-height: 0;
  flex: 1;
  flex-direction: column;
  padding: 0 !important;
  overflow: hidden;
}

.points-modal-inner {
  box-sizing: border-box;
  min-height: 0;
  height: 100%;
}
</style>
