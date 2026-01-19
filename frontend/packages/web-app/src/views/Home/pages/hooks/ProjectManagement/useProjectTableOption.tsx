import { SearchOutlined } from '@ant-design/icons-vue'
import { storeToRefs } from 'pinia'
import { reactive, ref, watch } from 'vue'

import { getDesignList } from '@/api/project'
import type { VIEW_OTHER } from '@/constants/resource'
import { VIEW_OWN } from '@/constants/resource'
import { useAppConfigStore } from '@/stores/useAppConfig'
import { useUserStore } from '@/stores/useUserStore'

import { useProjectOperate } from './useProjectOperate'

type DataSource = typeof VIEW_OWN | typeof VIEW_OTHER

export default function useProjectTableOption(dataSource: DataSource = VIEW_OWN) {
  const homeTableRef = ref(null)
  const consultRef = ref(null)

  const { createColumns, currHoverId, handleEdit } = useProjectOperate(homeTableRef, consultRef)
  const appStore = useAppConfigStore()
  const userStore = useUserStore()
  const { appInfo } = storeToRefs(appStore)

  function refreshHomeTable() {
    if (homeTableRef.value) {
      homeTableRef.value?.fetchTableData()
    }
  }

  const tableOption = reactive({
    refresh: false, // 控制表格数据刷新
    getData: getDesignList,
    formList: [ // 表格上方的表单配置
      {
        componentType: 'input',
        bind: 'name',
        placeholder: 'enterName',
        prefix: <SearchOutlined />,
      },
    ],
    tableProps: { // 表格配置，即antd中的Table组件的属性
      columns: createColumns,
      onResizeColumn: (w, col) => {
        createColumns.value.find(item => item.key === col.key).width = w
      },
      rowKey: 'robotId',
      size: 'middle',
      customRow: record => ({
        onDblclick: () => { // 双击行
          handleEdit(record)
        },
        onMouseenter: () => { // 鼠标移动到行
          currHoverId.value = record.robotId // 当前选中行标识
        },
        onMouseleave: () => { // 鼠标离开行
          currHoverId.value = ''
        },
      }),
    },
    params: { // 绑定的表单配置的数据
      name: '',
      dataSource,
    },
  })

  // 切换租户后列表刷新
  watch(() => userStore.currentTenant?.id, (val) => {
    if (val) {
      refreshHomeTable()
    }
  })

  return {
    homeTableRef,
    consultRef,
    tableOption,
    authType: appInfo.value.appAuthType,
  }
}
