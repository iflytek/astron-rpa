<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import useRequest from '@vue-hooks-plus/use-request'
import { Drawer, Spin } from 'ant-design-vue'
import { computed } from 'vue'

import { getRobotLastVersion } from '@/api/robot'

import Publish from './Publish.vue'
import { toFrontData } from './utils'

const props = defineProps({
  robotId: {
    type: String,
    required: true,
  },
})

const emits = defineEmits(['ok'])

const modal = NiceModal.useModal()
const { data, loading } = useRequest(() => getRobotLastVersion(props.robotId))

const frontData = computed(() => toFrontData(data.value))

function handleSubmited() {
  emits('ok')
  modal.hide()
}
</script>

<template>
  <Drawer
    v-bind="NiceModal.antdDrawer(modal)"
    title="发布机器人"
    class="publish-modal"
    :width="568"
    :footer="null"
  >
    <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
      <Spin />
    </div>
    <Publish v-else :robot-id="props.robotId" :default-data="frontData" @submited="handleSubmited" />
  </Drawer>
</template>

<style lang="scss">
.publish-modal {
  padding: 0;

  .ant-drawer-body {
    padding: 0;
  }
}
</style>
