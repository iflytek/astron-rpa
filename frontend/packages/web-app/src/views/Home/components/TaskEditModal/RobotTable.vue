<script setup>
import { PlusCircleOutlined } from '@ant-design/icons-vue'
import { NiceModal, useTheme } from '@rpa/components'
import { Popconfirm } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { throttle } from 'lodash-es'
import { reactive, ref, watch } from 'vue'

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
const { colorTheme } = useTheme()

/**
 * 表格配置
 */
const gridOptions = reactive({
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
    { field: 'none', title: '', width: 48, dragSort: true },
    { field: 'index', title: t('sort'), width: 60, slots: { default: 'index' } },
    { field: 'robotName', title: t('robot') },
    { field: 'robotVersion', title: t('packageVersion'), slots: { default: 'robotVersion' } },
    { field: 'action', title: t('operate'), width: 120, slots: { default: 'action' } },
  ],
  data: [],
  emptyText: t('noData'),
})

/**
 * 添加应用
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
 * 删除应用
 */
function deleteRobot(rowIndex) {
  gridOptions.data.splice(rowIndex, 1)
  refresh()
}
/**
 * 配置应用参数
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
  <div class="task-robot-table" :class="colorTheme">
    <VxeGrid ref="gridRef" round v-bind="gridOptions" size="mini" v-on="gridEvents">
      <template #index="{ rowIndex }">
        <span>{{ rowIndex + 1 }}</span>
      </template>
      <template #robotVersion="{ row }">
        <span>{{ row.robotVersion || '--' }}</span>
      </template>
      <template #action="{ row, rowIndex }">
        <a v-bind="row.haveParam ? undefined : { disabled: true }" @click="row.haveParam && configRobot(row)">
          {{ t('configParams') }}
        </a>
        <Popconfirm :title="t('deleteConfirmTip')" @confirm="() => deleteRobot(rowIndex)">
          <a class="ml-2">
            {{ t('delete') }}
          </a>
        </Popconfirm>
      </template>
      <template #dragRowTip="{ row }">
        <div>{{ t('moving') }}：{{ row.robotName }}</div>
      </template>
    </VxeGrid>
    <div class="text-center mt-2">
      <div
        class="flex items-center justify-center gap-2 text-xs h-8 cursor-pointer border-dashed border-x border-y rounded-lg border-[#00000040] dark:border-[#FFFFFF40] hover:text-primary hover:border-primary"
        @click="addRobot"
      >
        <PlusCircleOutlined />
        <span class="leading-[12px]">{{ t('addRobots') }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.task-robot-table {
  height: auto;

  --vxe-ui-table-header-background-color: rgba(255, 255, 255, 0.08);
  --vxe-ui-layout-background-color: transparent;
}
.task-robot-table.dark {
  --vxe-ui-table-header-background-color: rgba(0, 0, 0, 0.08);
}

:deep(.ant-btn-link) {
  color: var(--color-primary);
}

:deep(.ant-btn-link:disabled) {
  cursor: pointer;
  color: #00000040;
}
</style>
