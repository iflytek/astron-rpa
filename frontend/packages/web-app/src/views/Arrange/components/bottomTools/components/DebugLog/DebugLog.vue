<script lang="ts" setup>
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { inject, onBeforeMount, ref, watch } from 'vue'

import RpaVxeTable from '@/components/RpaVxeTable.vue'
import { clipboardManager } from '@/platform'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'

const columns = [
  {
    title: '变量名',
    field: 'variableName',
    width: 120,
  },
  {
    title: '变量值',
    field: 'variableValue',
  },
  {
    title: '变量类型',
    field: 'variableType',
    width: 120,
  },
]

const { t } = useTranslation()
const useRunning = useRunningStore()
const processStore = useProcessStore()

const dataSource = ref<any[]>([])
const height = inject('logTableHeight', 200) // 若没有注入，默认值为200

let tempData: { [key: string]: { value: any, types: string } } = {}

function menuClickHandle({ menu, row, column }) {
  if (menu.code === 'copy' && row && column) {
    const text = row[column.field]
    clipboardManager.writeClipboardText(text)
    message.info(t('contentCopied'))
  }
}

watch(() => useRunning.debugDataVar, (newVal) => {
  tempData = newVal || {}
  dataSource.value = Object.entries(tempData).map(([key, { value, types }]) => ({
    variableName: key,
    variableValue: value,
    variableType: processStore.globalVarTypeList[types]?.desc || types,
  }))
})
onBeforeMount(() => {
  tempData = {}
})
</script>

<template>
  <div class="logs-manager">
    <RpaVxeTable
      :height="height"
      :columns="columns"
      :data-source="dataSource"
      :is-scroll-bottom="true"
      @menu-click="menuClickHandle"
    />
  </div>
</template>
