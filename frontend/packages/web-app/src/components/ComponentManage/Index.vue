<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { useAsyncState } from '@vueuse/core'
import { Empty } from 'ant-design-vue'
import { isEmpty } from 'lodash-es'

import { getComponentManageList } from '@/api/robot'
import { useProcessStore } from '@/stores/useProcessStore'

import Panel from './Panel.vue'

const props = defineProps<{ robotId: string }>()

const modal = NiceModal.useModal()
const processStore = useProcessStore()
const { state: componentList, execute } = useAsyncState(() => getComponentManageList(props.robotId), [])

function handleRefresh() {
  execute()
  processStore.componentTree.refresh()
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="$t('moduleManagement')"
    width="75%"
    class="max-w-[1138px]"
    :keyboard="false"
    :mask-closable="false"
    :footer="null"
    destroy-on-close
    centered
  >
    <div
      class="mt-5 h-[520px]"
      :class="{ 'flex items-center justify-center': isEmpty(componentList) }"
    >
      <a-empty
        v-if="isEmpty(componentList)"
        :image="Empty.PRESENTED_IMAGE_SIMPLE"
      />
      <div v-else class="grid grid-cols-3 gap-4">
        <Panel
          v-for="item in componentList"
          :key="item.componentId"
          :data="item"
          :robot-id="robotId"
          @refresh="handleRefresh"
        />
      </div>
    </div>
  </a-modal>
</template>
