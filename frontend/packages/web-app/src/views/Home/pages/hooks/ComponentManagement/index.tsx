import { SearchOutlined } from '@ant-design/icons-vue'
import { Icon } from '@rpa/components'
import { Tooltip } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed, h, reactive, ref } from 'vue'

import { getComponentList } from '@/api/project'

import OperMenu from '../../../components/OperMenu.vue'
import StatusCircle from '../../../components/StatusCircle.vue'

import { useOperate } from './useOpetate'

export function useComponentTableOption() {
  const { t } = useTranslation()
  const { baseOpts, moreOpts, handleEdit, handleRename } = useOperate(refreshTable)
  const tableRef = ref(null)

  function refreshTable() {
    tableRef?.value.fetchTableData()
  }

  const columns = computed(() => [
    {
      title: t('components.componentName'),
      ellipsis: true,
      dataIndex: 'name',
      key: 'name',
      customRender: ({ record }) => (
        <div class="flex items-center gap-2 overflow-hidden w-full group">
          <Tooltip title={`ID：${record.componentId}`}>
            <span class="truncate flex-1">{ record.name }</span>
          </Tooltip>
          <Tooltip title={t('rename')} class="hidden group-hover:inline">
            <Icon name="projedit" class="hover:text-primary cursor-pointer" onClick={() => handleRename(record)} />
          </Tooltip>
        </div>
      ),
    },
    {
      title: t('updated'),
      ellipsis: true,
      dataIndex: 'updateTime',
      key: 'updateTime',
    },
    {
      title: t('common.publishStatus'),
      ellipsis: true,
      dataIndex: 'transformStatus',
      key: 'transformStatus',
      customRender: ({ record }) => <StatusCircle type={`${record.transformStatus}`} />,
    },
    {
      title: t('currentVersion'),
      ellipsis: true,
      dataIndex: 'version',
      key: 'version',
      customRender: ({ record }) => Number(record?.version) === 0 ? '--' : `V${record?.version}`,
    },
    {
      title: t('operate'),
      dataIndex: 'oper',
      key: 'oper',
      width: 150,
      customRender: ({ record }) => (
        <OperMenu moreOpts={moreOpts} baseOpts={baseOpts} row={record} />
      ),
    },
  ])

  const tableOption = reactive({
    refresh: false, // 控制表格数据刷新
    getData: params => getComponentList({ ...params, dataSource: 'create', pageNum: params.pageNo }),
    formList: [
      // 表格上方的表单配置
      {
        componentType: 'input',
        bind: 'name',
        placeholder: t('common.enterPlaceholder', {
          name: t('components.componentName'),
        }),
        prefix: h(SearchOutlined),
      },
    ],
    tableProps: {
      columns: columns.value,
      customRow: record => ({
        onDblclick: () => { // 双击行
          handleEdit(record)
        },
      }),
    },
    params: { // 绑定的表单配置的数据
      name: '',
    },
  })

  return { tableOption, tableRef }
}
