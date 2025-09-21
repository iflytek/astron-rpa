import { Icon } from '@rpa/components'
import { message, Tooltip } from 'ant-design-vue'
import { reactive, ref, watch } from 'vue'

import { applicationList, cancelApplication, deleteApplication } from '@/api/market'
import { applicationStatus, applicationStatusMap, APPROVED, CANCELED, PENDING, REJECTED, SECURITY_LEVEL_TEXT } from '@/views/Home/components/TeamMarket/config/market.ts'
import { useCommonOperate } from '@/views/Home/pages/hooks/useCommonOperate.tsx'

export function useApplicationTable() {
  const tableRef = ref(null)
  function refreshHomeTable() {
    if (tableRef.value) {
      tableRef.value?.fetchTableData()
    }
  }
  const { handleDeleteConfirm } = useCommonOperate()

  const getApplicationList = (params) => {
    return new Promise((resolve) => {
      applicationList(params).then((res: any) => {
        res.data && resolve(res.data)
      })
    })
  }

  const tableOption = reactive({
    refresh: false, // 控制表格数据刷新
    getData: getApplicationList,
    formList: [
      {
        componentType: 'input',
        bind: 'robotName',
        placeholder: '请输入机器人名称',
        // prefix: <SearchOutlined />,
      },
      {
        componentType: 'select',
        bind: 'applicationType',
        placeholder: '请选择申请类型',
        options: [
          {
            label: '全部',
            value: '',
          },
          {
            label: '上架申请',
            value: 'release',
          },
          {
            label: '使用申请',
            value: 'use',
          },
        ],
      },
      {
        componentType: 'select',
        bind: 'status',
        placeholder: '请选择申请状态',
        options: [
          {
            label: '全部',
            value: '',
          },
          ...applicationStatus,
        ],
      },
    ],
    tableProps: {
      columns: [
        {
          title: '机器人名称',
          dataIndex: 'robotName',
          key: 'robotName',
          ellipsis: true,
          customRender: ({ record }) => {
            return (
              <span class="cursor-pointer inline-flex items-center">
                {record.applicationType === 'release' && record.status === APPROVED && (
                  <Tooltip title={SECURITY_LEVEL_TEXT[record.securityLevel]}>
                    <Icon name={`market-${record.securityLevel}`} class="cursor-pointer inline-block mr-[4px]" size="18px" />
                  </Tooltip>
                )}
                <Tooltip title={`ID：${record.robotId}`}>
                  {record.robotName}
                </Tooltip>
              </span>
            )
          },
        },
        {
          title: '申请时间',
          dataIndex: 'submitAuditTime',
          key: 'submitAuditTime',
          ellipsis: true,
        },
        {
          title: '申请类型',
          dataIndex: 'applicationType',
          key: 'applicationType',
          ellipsis: true,
          customRender: ({ record }) => {
            return (
              record.applicationType === 'use'
                ? <span class="px-[10px] py-[6px] rounded bg-[#2FCB64]/[.1] text-[#2FCB64]">使用申请</span>
                : <span class="px-[10px] py-[6px] rounded bg-[#F39D09]/[.1] text-[#F39D09]">上架申请</span>
            )
          },
        },
        {
          title: '申请状态',
          dataIndex: 'status',
          key: 'status',
          ellipsis: true,
          customRender: ({ record }) => {
            return (
              <span class="flex items-center">
                <span class={`inline-block w-[6px] h-[6px] rounded-full mr-[10px] ${record.status === APPROVED ? 'bg-[#2FCB64]' : record.status === REJECTED ? 'bg-[#EC483E]' : 'bg-[#BFBFBF]'}`}></span>
                {applicationStatusMap[record.status] || ''}
              </span>
            )
          },
        },
        {
          title: '审核意见',
          dataIndex: 'auditOpinion',
          key: 'auditOpinion',
          ellipsis: true,
          customRender: ({ record }) => {
            const reason = (record.status === REJECTED) ? (record.auditOpinion || '--') : ''
            return <Tooltip title={reason}>{reason}</Tooltip>
          },
        },
        {
          title: '操作',
          dataIndex: 'oper',
          key: 'oper',
          width: 120,
          customRender: ({ record }) => {
            return (
              <div class="flex items-center gap-6">
                {record.status === PENDING && (
                  <Tooltip title="撤销">
                    <Icon
                      name="tools-undo"
                      class="cursor-pointer outline-none hover:text-primary"
                      size="16px"
                      onClick={() => handleCancel(record)}
                    />
                  </Tooltip>
                )}
                <Tooltip title="删除">
                  <Icon
                    name="market-del"
                    class="cursor-pointer outline-none hover:text-primary"
                    size="16px"
                    onClick={() => handleDelete(record)}
                  />
                </Tooltip>
              </div>
            )
          },
        },
      ],
      rowKey: 'id',
    },
    params: {
      robotName: '',
      applicationType: undefined,
      status: undefined,
    },
    size: 'middle',
  })

  function handleCancel(record) {
    if (record.status !== PENDING)
      return
    handleDeleteConfirm(`撤销后该申请流程将会被终止，管理员无法审核，请确认继续撤销？`, () => {
      cancelApplication({ id: record.id }).then(() => {
        message.success('撤销成功')
        refreshHomeTable()
      })
    })
  }

  function handleDelete(record) {
    let tip = '删除后该申请流程结果不会受到影响，请确认继续删除？'
    if (record.status === PENDING)
      tip = '删除后该申请流程也会被终止，管理员无法审核，请确认继续删除？'
    if (record.status === CANCELED)
      tip = '删除后不可恢复，请确认继续删除？'
    handleDeleteConfirm(tip, () => {
      deleteApplication({ id: record.id }).then(() => {
        message.success('删除成功')
        refreshHomeTable()
      })
    })
  }

  watch(() => tableOption.params, () => {
    refreshHomeTable()
  }, {
    immediate: true,
    deep: true,
  })

  return {
    tableRef,
    tableOption,
  }
}
