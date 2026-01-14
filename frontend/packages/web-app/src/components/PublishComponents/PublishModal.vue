<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { useAsyncState } from '@vueuse/core'
import { Drawer, Spin } from 'ant-design-vue'

import { getRobotLastVersion } from '@/api/robot'

import Publish from './Publish.vue'
import { toFrontData } from './utils'

const props = defineProps<{ robotId: string }>()

const emits = defineEmits(['ok'])

const modal = NiceModal.useModal()
const { state, isLoading } = useAsyncState(() => getRobotLastVersion(props.robotId), null)

function handleSubmited() {
  emits('ok')
  modal.hide()
}
</script>

<template>
  <Drawer
    v-bind="NiceModal.antdDrawer(modal)"
    title="发布应用"
    class="no-drag"
    :body-style="{ padding: '0px' }"
    :width="568"
    :footer="null"
  >
    <div v-if="isLoading || !state" class="flex items-center justify-center min-h-[60vh]">
      <Spin />
    </div>
    <Publish v-else :robot-id="props.robotId" :default-data="toFrontData(state)" @submited="handleSubmited" />
  </Drawer>
</template>
