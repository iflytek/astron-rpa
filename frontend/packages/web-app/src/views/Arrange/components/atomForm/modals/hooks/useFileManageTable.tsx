import { SearchOutlined } from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import { useTranslation } from 'i18next-vue'
import { reactive, ref } from 'vue'

import { getRemoteFiles } from '@/api/atom'
import type { TableOption } from '@/types/normalTable'

export default function useFileManageTable() {
  const selectFileId = ref('')
  const { t } = useTranslation()

  const handleClick = (record) => {
    selectFileId.value = record.fileId
  }
  const tableOption = reactive<TableOption>({
    refresh: false, // 控制表格数据刷新
    getData: getRemoteFiles,
    formList: [ // 表格上方的表单配置
      {
        componentType: 'input',
        bind: 'fileName',
        placeholder: t('market.enterFileName'),
        prefix: <SearchOutlined />,
      },
    ],
    tableProps: { // 表格配置，即antd中的Table组件的属性
      columns: [
        {
          title: t('market.fileName'),
          dataIndex: 'fileName',
          key: 'fileName',
          fixed: 'left',
          ellipsis: true,
        },
        {
          title: t('common.createTime'),
          dataIndex: 'createTime',
          key: 'createTime',
          sortable: true,
          ellipsis: true,
          customRender: ({ record }) => dayjs(record.createTime).format('YYYY-MM-DD HH:mm:ss'),
        },
        {
          title: t('common.updateTime'),
          dataIndex: 'updateTime',
          key: 'updateTime',
          sortable: true,
          ellipsis: true,
          customRender: ({ record }) => dayjs(record.updateTime).format('YYYY-MM-DD HH:mm:ss'),
        },
        {
          title: t('market.owner'),
          dataIndex: 'creatorName',
          key: 'creatorName',
          ellipsis: true,
        },
        {
          title: t('common.account'),
          dataIndex: 'phone',
          key: 'phone',
          ellipsis: true,
        },
        {
          title: t('market.department'),
          dataIndex: 'deptName',
          key: 'deptName',
          ellipsis: true,
        },
        {
          title: t('market.tags'),
          dataIndex: 'tags',
          key: 'tags',
          ellipsis: true,
          customRender: ({ record }) => {
            return record.tagsNames?.length > 0 ? record.tagsNames.join(', ') : '--'
          },
        },
      ],
      rowKey: 'fileId',
      size: 'middle',
      customRow: (record) => {
        return {
          class: `cursor-pointer ${record.fileId === selectFileId.value ? 'selectRow' : ''}`,
          onClick: () => { // 双击行
            handleClick(record)
          },
        }
      },
    },
    params: { // 绑定的表单配置的数据
      fileName: '',
    },
  })

  return {
    selectFileId,
    tableOption,
  }
}
