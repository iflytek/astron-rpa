import { SearchOutlined } from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import { reactive, ref } from 'vue'

import { getRemoteFiles } from '@/api/atom'

export default function useFileManageTable() {
  const selectFileId = ref('')

  const handleClick = (record) => {
    selectFileId.value = record.fileId
  }
  const tableOption = reactive({
    refresh: false, // 控制表格数据刷新
    getData: getRemoteFiles,
    formList: [ // 表格上方的表单配置
      {
        componentType: 'input',
        bind: 'fileName',
        placeholder: '请输入文件名称',
        prefix: <SearchOutlined />,
      },
    ],
    tableProps: { // 表格配置，即antd中的Table组件的属性
      columns: [
        {
          title: '文件名称',
          dataIndex: 'fileName',
          key: 'fileName',
          fixed: 'left',
          ellipsis: true,
        },
        {
          title: '创建时间',
          dataIndex: 'createTime',
          key: 'createTime',
          sortable: true,
          ellipsis: true,
          customRender: ({ record }) => dayjs(record.createTime).format('YYYY-MM-DD HH:mm:ss'),
        },
        {
          title: '更新时间',
          dataIndex: 'updateTime',
          key: 'updateTime',
          sortable: true,
          ellipsis: true,
          customRender: ({ record }) => dayjs(record.updateTime).format('YYYY-MM-DD HH:mm:ss'),
        },
        {
          title: '所有者',
          dataIndex: 'creatorName',
          key: 'creatorName',
          ellipsis: true,
        },
        {
          title: '账号',
          dataIndex: 'phone',
          key: 'phone',
          ellipsis: true,
        },
        {
          title: '所属部门',
          dataIndex: 'deptName',
          key: 'deptName',
          ellipsis: true,
        },
        {
          title: '标签',
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
