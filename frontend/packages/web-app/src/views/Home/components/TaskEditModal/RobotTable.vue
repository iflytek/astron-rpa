<script setup>
import { PlusCircleOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { Popconfirm } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { throttle } from 'lodash-es'
import { h, reactive, ref, watch } from 'vue'

import VxeGrid from '@/plugins/VxeTable'

import { RobotConfigTaskModal } from '@/components/RobotConfigTaskModal'
import { RobotSelectModal } from '@/components/RobotSelectModal'

const props = defineProps({
  robots: {
    type: Array,
    default: () => [],
  },
})
const emit = defineEmits(['update:robots'])
const gridRef = ref()
const { t } = useTranslation()

/**
 * 表格配置
 */
const gridOptions = reactive({
  headerClassName: 'bg-fill',
  border: false,
  height: 180,
  rowConfig: {
    drag: true,
  },
  rowDragConfig: {
    slots: {
      tip: 'dragRowTip',
    },
  },
  size: 'small',
  columns: [
    { field: 'none', title: '', width: 80, dragSort: true },
    { field: 'index', title: t('sort'), width: 80, slots: { default: 'index' } },
    { field: 'robotName', title: t('robot') },
    { field: 'robotVersion', title: t('packageVersion'), slots: { default: 'robotVersion' } },
    { field: 'action', title: t('operate'), slots: { default: 'action' }, minWidth: 120 },
  ],
  data: [],
  emptyText: t('noData'),
})

/**
 * 添加机器人
 */
function addRobot() {
  NiceModal.show(RobotSelectModal, {
    onOk: (robot) => {
      gridOptions.data = gridOptions.data.concat(robot)
      refresh()
    },
  })
}

/**
 * 删除机器人
 */
function deleteRobot(rowIndex) {
  gridOptions.data.splice(rowIndex, 1)
  refresh()
}
/**
 * 配置机器人参数
 */
const configRobot = throttle((record) => {
  NiceModal.show(RobotConfigTaskModal, {
    robotId: record.robotId,
    mode: 'CRONTAB',
    params: record.paramJson ? JSON.parse(record.paramJson) : null,
    onOk: (res) => {
      record.paramJson = JSON.stringify(res)
    },
  })
}, 1500, { leading: true, trailing: false })
/**
 * 刷新表格
 */
function refresh() {
  gridRef.value && gridRef.value.loadData(gridOptions.data)
  emit('update:robots', gridOptions.data)
}
/**
 * 表格事件
 */
const gridEvents = {
  rowDragend() {
    gridOptions.data = gridRef.value.getTableData().fullData
    refresh()
  },
}
watch(() => props.robots, (val) => {
  gridOptions.data = val
  refresh()
})
</script>

<template>
  <div class="task-robot-table">
    <div class="table-content">
      <VxeGrid ref="gridRef" round class="robot-table" v-bind="gridOptions" size="mini" v-on="gridEvents">
        <template #index="{ rowIndex }">
          <span>{{ rowIndex + 1 }}</span>
        </template>
        <template #robotVersion="{ row }">
          <span>{{ row.robotVersion || '--' }}</span>
        </template>
        <template #action="{ row, rowIndex }">
          <a-button :disabled="!row.haveParam" type="link" class="ml-4 p-0" @click="configRobot(row)">
            {{ t('configParams') }}
          </a-button>
          <Popconfirm :title="t('deleteConfirmTip')" @confirm="() => deleteRobot(rowIndex)">
            <a-button type="link" class="ml-2 p-0">
              {{ t('delete') }}
            </a-button>
          </Popconfirm>
        </template>
        <template #dragRowTip="{ row }">
          <div>{{ t('moving') }}：{{ row.robotName }}</div>
        </template>
      </VxeGrid>
    </div>
    <div class="text-center mt-2">
      <a-button class="inline-flex items-center justify-center w-full" type="dashed" :icon="h(PlusCircleOutlined)" @click="addRobot">
        {{ t('addRobots') }}
      </a-button>
    </div>
  </div>
</template>

<style scoped>
.task-robot-table {
  height: auto;
}
.bg-fill {
  background-color: #d7d7ff66;
}
:deep(.ant-btn-link) {
  color: var(--color-primary);
}
:deep(.ant-btn-link:disabled) {
  cursor: pointer;
  color: #00000040;
}
</style>
