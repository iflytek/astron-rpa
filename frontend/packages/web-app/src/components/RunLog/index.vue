<script lang="tsx" setup>
import { useTheme } from '@rpa/components'
import { message, Tooltip } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { debounce, isNil, last, noop } from 'lodash-es'
import type { Ref } from 'vue'
import { computed, inject, onMounted, onUnmounted, ref, shallowRef, watch } from 'vue'
import type {
  VxeGridEventProps,
  VxeGridInstance,
  VxeGridProps,
} from 'vxe-table'

import VxeGrid from '@/plugins/VxeTable'

import { clipboardManager, windowManager } from '@/platform'
import { useRunlogStore } from '@/stores/useRunlogStore'
import { useRunningStore } from '@/stores/useRunningStore'

const props = defineProps<{ size?: 'default' | 'small' }>()
const emit = defineEmits(['rowClick'])
const { colorTheme } = useTheme()
const height = inject<Ref<number>>('logTableHeight', ref(320)) // 若没有注入，默认值为320
const runlogStore = useRunlogStore()
const { t } = useTranslation()
const xGrid = ref<VxeGridInstance<RPA.LogItem>>()
const isMinimized = ref(false) // 是否最小化
const dataList = shallowRef<RPA.LogItem[]>([])

let unWindowResizeListen = noop

onMounted(async () => {
  const resizeDebounce = debounce(async () => {
    isMinimized.value = await windowManager.isMinimized()
  }, 200)
  unWindowResizeListen = await windowManager.onWindowResize(resizeDebounce)
})

onUnmounted(() => unWindowResizeListen())

const columns = computed<VxeGridProps<RPA.LogItem>['columns']>(() => {
  const isSmall = props.size === 'small'

  return [
    {
      title: t('errorType'),
      field: 'logLevelText',
      width: isSmall ? 50 : 80,
    },
    {
      title: t('timestamp'),
      field: 'timestamp',
      width: isSmall ? 130 : 160,
    },
    {
      title: t('processName'),
      field: 'processName',
      width: isSmall ? 60 : 80,
      align: 'right',
      formatter: ({ cellValue }) => (isNil(cellValue) ? '--' : cellValue),
    },
    {
      title: t('rows'),
      field: 'lineNum',
      width: isSmall ? 50 : 80,
      align: 'right',
      formatter: ({ cellValue }) => (isNil(cellValue) ? '--' : cellValue),
    },
    {
      title: t('content'),
      field: 'content',
      showOverflow: 'ellipsis',
      slots: { default: 'content_default' },
    },
  ]
})

const onMenuClick: VxeGridEventProps<RPA.LogItem>['onMenuClick'] = ({
  menu,
  row,
  column,
}) => {
  const $grid = xGrid.value

  if ($grid && menu.code === 'copy' && row && column) {
    const text = row[column.field]
    clipboardManager.writeClipboardText(text)
    message.info(t('contentCopied'))
  }
}

async function scrollTobottom() {
  const $grid = xGrid.value
  if (!$grid)
    return

  await $grid.clearScroll()

  $grid.scrollToRow(last(dataList.value), 'id')
}

function refreshDataList() {
  // 判断 dataList 和 runlogStore.logList 是否相等
  // 1. 先判断长度是否相等
  // 2. 再判断每一项是否相等
  if (
    dataList.value.length !== runlogStore.logList.length
    || dataList.value.find((item, index) => item.id !== runlogStore.logList[index].id)
  ) {
    dataList.value = runlogStore.logList
    setTimeout(() => scrollTobottom(), 100)
  }
}

// 监听表格数据变化实时滚动到底
watch(
  () => runlogStore.logList.length,
  () => {
    // 如果窗口最小化，则不更新数据
    if (!isMinimized.value) {
      refreshDataList()
    }
  },
  { immediate: true },
)

watch(
  () => isMinimized.value,
  (val) => {
    // 如果窗口恢复，则更新数据
    if (!val) {
      refreshDataList()
    }
  },
)

// 每次工程运行前将dataList清空，解决日志数据不更新问题
watch(() => useRunningStore().running, (val) => {
  if (val !== 'free') {
    dataList.value = []
  }
})

const onCellClick: VxeGridEventProps['onCellClick'] = (data) => {
  const { row } = data
  emit('rowClick', row)
}

const setRowClassName: VxeGridProps['rowClassName'] = ({ row }) => {
  const levelClassMap = {
    error: 'row-error',
    warning: 'row-warning',
  }

  return levelClassMap[row.logLevel] || ''
}
</script>

<template>
  <div class="runlog-content_table" :class="[colorTheme]">
    <VxeGrid
      id="id"
      ref="xGrid"
      size="mini"
      :height="height"
      border="none"
      :show-overflow="true"
      :keep-source="false"
      :columns="columns"
      :data="dataList"
      :row-class-name="setRowClassName"
      :scroll-y="{ enabled: true }"
      :row-config="{ isHover: true }"
      :menu-config="{
        body: {
          options: [[{ code: 'copy', name: $t('复制') }]],
        },
        visibleMethod: ({ options, column }) => {
          const isVisible = column?.field === 'content';

          const copyOption = options
            .flat(1)
            .find((item) => item.code === 'copy');
          if (copyOption) {
            copyOption.visible = isVisible;
          }

          return true;
        },
      }"
      :tooltip-config="{ showAll: false }"
      @menu-click="onMenuClick"
      @cell-click="onCellClick"
    >
      <template #content_default="{ row }">
        <Tooltip
          :title="row.content"
          :mouse-enter-delay="1"
          :overlay-inner-style="{
            width: row.content.length >= 100 ? '600px' : 'auto',
            maxHeight: '150px',
            overflow: 'hidden',
            overflowY: 'auto',
          }"
          placement="topLeft"
        >
          {{ row.content }}
        </Tooltip>
      </template>
    </VxeGrid>
  </div>
</template>

<style lang="scss">
.runlog-content_table {
  height: 100%;

  --vxe-ui-table-row-height-mini: 32px;
  --vxe-ui-table-column-padding-mini: 5px 0;
  --vxe-ui-font-color: rgba(0, 0, 0, 0.85);
  --vxe-ui-table-header-font-color: rgba(0, 0, 0, 0.45);
  --vxe-ui-table-header-font-weight: 400;

  &.dark {
    --vxe-ui-font-color: rgba(255, 255, 255, 0.85);
    --vxe-ui-table-header-font-color: rgba(255, 255, 255, 0.45);
  }

  .row-error {
    color: $color-error;
  }
  .row-warning {
    color: $color-warning;
  }

  .custom-content-render {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    user-select: text;
  }
}
</style>
