<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { Drawer } from 'ant-design-vue'

import { useProvideBasicStore } from './basicStore'
import Content from './Content.vue'

const props = defineProps<{ robotId: string, source: string }>()

const modal = NiceModal.useModal()

useProvideBasicStore(props.robotId, props.source)
</script>

<template>
  <Drawer
    v-bind="NiceModal.antdDrawer(modal)"
    title="机器人详情"
    class="robotDetailsModal"
    placement="right"
    :width="628"
    :footer="null"
  >
    <Content />
  </Drawer>
</template>

<style lang="scss" scoped>
.robotDetailsModal {
  .ant-modal-body {
    height: 560px;
    overflow-x: hidden;
    overflow-y: auto;
  }
}
</style>
