import { Icon } from '@rpa/components'
import { message, Tooltip } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { reactive, ref, watch } from 'vue'

import { applicationList, cancelApplication, deleteApplication } from '@/api/market'
import type { ITableResponse, TableOption } from '@/types/normalTable'
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
  const { t } = useTranslation()

  const getApplicationList = async (params): Promise<ITableResponse<any>> => {
    const res = await applicationList(params) as { data: ITableResponse<any> }
    return res.data
  }

  const tableOption = reactive<TableOption>({
    refresh: false, // 控制表格数据刷新
    getData: getApplicationList,
    formList: [
      {
        componentType: 'input',
        bind: 'robotName',
        placeholder: t('market.enterAppName'),
        // prefix: <SearchOutlined />,
      },
      {
        componentType: 'select',
        bind: 'applicationType',
        placeholder: t('market.selectAppType'),
        options: [
          {
            label: t('common.all'),
            value: '',
          },
          {
            label: t('market.releaseApp'),
            value: 'release',
          },
          {
            label: t('market.useApp'),
            value: 'use',
          },
        ],
      },
      {
        componentType: 'select',
        bind: 'status',
        placeholder: t('market.selectAppStatus'),
        options: [
          {
            label: t('common.all'),
            value: '',
          },
          ...applicationStatus.map(item => ({
            ...item,
            label: t(item.label),
          })),
        ],
      },
    ],
    tableProps: {
      columns: [
        {
          title: t('market.appName'),
          dataIndex: 'robotName',
          key: 'robotName',
          ellipsis: true,
          customRender: ({ record }) => {
            return (
              <span class="cursor-pointer inline-flex items-center">
                {record.applicationType === 'release' && record.status === APPROVED && (
                  <Tooltip title={t(SECURITY_LEVEL_TEXT[record.securityLevel])}>
                    <Icon name={`market-${record.securityLevel}`} class="cursor-pointer inline-block mr-[4px]" size="18px" />
                  </Tooltip>
                )}
                <Tooltip title={t('common.idWithColon', { id: record.robotId })}>
                  {record.robotName}
                </Tooltip>
              </span>
            )
          },
        },
        {
          title: t('market.applyTime'),
          dataIndex: 'submitAuditTime',
          key: 'submitAuditTime',
          ellipsis: true,
        },
        {
          title: t('market.applyType'),
          dataIndex: 'applicationType',
          key: 'applicationType',
          ellipsis: true,
          customRender: ({ record }) => {
            return (
              record.applicationType === 'use'
                ? <span class="px-[10px] py-[6px] rounded bg-[#2FCB64]/[.1] text-[#2FCB64]">{t('market.useApp')}</span>
                : <span class="px-[10px] py-[6px] rounded bg-[#F39D09]/[.1] text-[#F39D09]">{t('market.releaseApp')}</span>
            )
          },
        },
        {
          title: t('market.applyStatus'),
          dataIndex: 'status',
          key: 'status',
          ellipsis: true,
          customRender: ({ record }) => {
            return (
              <span class="flex items-center">
                <span class={`inline-block w-[6px] h-[6px] rounded-full mr-[10px] ${record.status === APPROVED ? 'bg-[#2FCB64]' : record.status === REJECTED ? 'bg-[#EC483E]' : 'bg-[#BFBFBF]'}`}></span>
                {t(applicationStatusMap[record.status]) || ''}
              </span>
            )
          },
        },
        {
          title: t('market.auditOpinion'),
          dataIndex: 'auditOpinion',
          key: 'auditOpinion',
          ellipsis: true,
          customRender: ({ record }) => {
            const reason = (record.status === REJECTED) ? (record.auditOpinion || '--') : ''
            return <Tooltip title={reason}>{reason}</Tooltip>
          },
        },
        {
          title: t('common.operate'),
          dataIndex: 'oper',
          key: 'oper',
          width: 120,
          customRender: ({ record }) => {
            return (
              <div class="flex items-center gap-6">
                {record.status === PENDING && (
                  <Tooltip title={t('market.revoke')}>
                    <Icon
                      name="tools-undo"
                      class="cursor-pointer outline-none hover:text-primary"
                      size="16px"
                      onClick={() => handleCancel(record)}
                    />
                  </Tooltip>
                )}
                <Tooltip title={t('common.delete')}>
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

  async function handleCancel(record) {
    if (record.status !== PENDING)
      return
    const confirm = await handleDeleteConfirm(t('market.revokeConfirm'))
    if (!confirm) {
      return
    }
    await cancelApplication({ id: record.id })
    message.success(t('market.revokeSuccess'))
    refreshHomeTable()
  }

  async function handleDelete(record) {
    let tip = t('market.deleteAppConfirm1')
    if (record.status === PENDING)
      tip = t('market.deleteAppConfirm2')
    if (record.status === CANCELED)
      tip = t('market.deleteAppConfirm3')
    const confirm = await handleDeleteConfirm(tip)
    if (!confirm) {
      return
    }
    await deleteApplication({ id: record.id })
    message.success(t('common.deleteSuccess'))
    refreshHomeTable()
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
