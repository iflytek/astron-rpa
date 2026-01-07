<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { Drawer } from 'ant-design-vue'
import { computed, onMounted, provide, ref, watch } from 'vue'

import { blob2Text, text2LogArray } from '@/utils/common'

import { getlogs } from '@/api/record'
import { fileRead } from '@/api/resource'
import GlobalModal from '@/components/GlobalModal'
import RunLog from '@/components/RunLog/index.vue'
import { useRunlogStore } from '@/stores/useRunlogStore'
import type { AnyObj } from '@/types/common'

import ReadonlyDataTable from './ReadonlyDataTable.vue'

type ModalType = 'modal' | 'drawer'
enum SegmentValue {
  Log = 'log',
  Table = 'table',
}

const segmentOptions = [
  { label: '详细日志', value: SegmentValue.Log },
  { label: '数据表格', value: SegmentValue.Table },
]

const props = withDefaults(
  defineProps<{
    record?: AnyObj
    logPath?: string
    dataTablePath?: string
    type?: ModalType // 新增 type 属性来控制显示类型
  }>(),
  { type: 'modal' },
)
const emit = defineEmits(['clearLogs'])

const modal = NiceModal.useModal()
const runlogStore = useRunlogStore()

const loaded = ref(false)
const segmentValue = ref(segmentOptions[0].value)

if (props.type === 'drawer') {
  provide('logTableHeight', window.innerHeight - 100)
}

watch(() => modal.visible, (newVal) => {
  if (!newVal) {
    emit('clearLogs')
  }
})

async function handLogFormat() {
  const res = await getlogs({ executeId: props.record.executeId })
  const detailLogs = JSON.parse(res.data).map((item) => {
    const { event_time } = item
    return { ...item.data, event_time }
  })
  runlogStore.setLogs(detailLogs)
  loaded.value = true
}

async function fileLogFormat() {
  const { data } = await fileRead({ path: props.logPath })
  const result = await blob2Text<string>(data)
  const logs = text2LogArray(result)
  runlogStore.setLogs(logs)
  loaded.value = true
}

onMounted(() => {
  if (props.logPath) { // 立即获取的日志
    fileLogFormat()
  }
  else {
    handLogFormat()
  }
})

// 组件配置
const modalConfigProps: Record<ModalType, Record<string, any>> = {
  modal: {
    width: 600,
  },
  drawer: {
    width: 628,
    placement: 'right',
  },
}

const isDrawer = computed(() => props.type === 'drawer')

const componentProps = computed(() => {
  const bindProps = isDrawer.value ? NiceModal.antdDrawer(modal) : NiceModal.antdModal(modal)
  return { ...modalConfigProps[props.type], ...bindProps }
})
</script>

<template>
  <component v-bind="componentProps" :is="isDrawer ? Drawer : GlobalModal" :footer="null">
    <template #title>
      <a-segmented v-if="props.dataTablePath" v-model:value="segmentValue" :options="segmentOptions" />
      <template v-else>
        {{ `详细日志${props.record?.robotName ? ` - ${props.record.robotName}` : ''}` }}
      </template>
    </template>

    <div v-show="segmentValue === SegmentValue.Log" class="h-[320px] overflow-hidden flex items-center justify-center">
      <RunLog v-if="loaded" class="w-full" size="small" />
      <a-spin v-else :tip="$t('loading')" />
    </div>

    <template v-if="props.dataTablePath">
      <ReadonlyDataTable
        v-show="segmentValue === SegmentValue.Table"
        :class="isDrawer ? 'h-full' : 'h-[320px]'"
        :data-table-path="props.dataTablePath"
      />
    </template>
  </component>
</template>
