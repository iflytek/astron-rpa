import { SearchOutlined, SyncOutlined } from '@ant-design/icons-vue'
import { Icon } from '@rpa/components'
import { Tooltip } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { h, reactive, ref, watch } from 'vue'

import type { AnyObj } from '@/types/common'
import { ROBOT_SOURCE_LOCAL, ROBOT_SOURCE_TEXT } from '@/views/Home/config'
import { handleRun } from '@/views/Home/pages/hooks/useCommonOperate.tsx'
import { useUserStore } from '@/stores/useUserStore'

import OperMenu from '../../../components/OperMenu.vue'

import useRobotOperation from './useRobotOperation'

export default function useRobotTableOption() {
  const homeTableRef = ref(null)
  function refreshHomeTable() {
    if (homeTableRef.value) {
      homeTableRef.value?.fetchTableData()
    }
  }
  const { t } = useTranslation()
  const { getTableData, handleToConfig, openRobotDetailModal, openMcpConfigModal, handleDeleteRobot, handleRobotUpdate, expiredTip } = useRobotOperation(homeTableRef, refreshHomeTable)
  const userStore = useUserStore()

  const baseOpts = [
    {
      key: 'run',
      text: 'run',
      clickFn: (record) => { !expiredTip(record) && handleRun({ ...record, exec_position: 'EXECUTOR' }) },
      icon: h(<Icon name="play-circle-stroke" size="16px" />),
    },
    {
      key: 'config',
      text: 'configParameters',
      clickFn: handleToConfig,
      icon: h(<Icon name="config-params" size="16px" />),
    },
  ]

  const localMoreOpts = [
    {
      key: 'virtualRun',
      text: 'virtualDesktopRunning',
      icon: h(<Icon name="virtual-desktop" size="16px" />),
      disableFn: (row: AnyObj) => row.usePermission === 0,
      clickFn: (record) => { !expiredTip(record) && handleRun({ ...record, exec_position: 'EXECUTOR', open_virtual_desk: true }) },
    },
    {
      key: 'check',
      text: 'appDetails',
      icon: h(<Icon name="robot" size="16px" />),
      clickFn: openRobotDetailModal,
    },
    {
      key: 'mcpconfig',
      text: 'mcpconfig',
      icon: h(<Icon name="robot" size="16px" />),
      clickFn: openMcpConfigModal,
    },
  ]
  const marketMoreOpts = [
    {
      key: 'virtualRun',
      text: 'virtualDesktopRunning',
      icon: h(<Icon name="virtual-desktop" size="16px" />),
      disableFn: (row: AnyObj) => row.usePermission === 0,
      clickFn: (record) => { !expiredTip(record) && handleRun({ ...record, exec_position: 'EXECUTOR', open_virtual_desk: true }) },
    },
    {
      key: 'check',
      text: 'appDetails',
      icon: h(<Icon name="robot" size="16px" />),
      clickFn: openRobotDetailModal,
    },
    {
      key: 'delete',
      text: 'delete',
      icon: h(<Icon name="market-del" size="16px" />),
      clickFn: handleDeleteRobot,
    },
  ]

  const tableOption = reactive({
    refresh: false, // 控制表格数据刷新
    getData: getTableData,
    formList: [ // 表格上方的表单配置
      {
        componentType: 'input',
        bind: 'name',
        placeholder: 'enterName',
        prefix: <SearchOutlined />,
      },
    ],
    // 这块注释不要删，后期要上
    // buttonList: [ // 表格上方的按钮配置
    //   // {
    //   //   label: '导入应用',
    //   //   clickFn: importRobot,
    //   //   type: 'primary',
    //   //   hidden: false,
    //   // },
    //   {
    //     label: '批量操作',
    //     plain: true,
    //     type: 'primary',
    //     btnType: 'dropdown',
    //     // hidden: !btnPermission(['unmanned', 'elc_center_resource_terminal_unmanned_list_edit']),
    //     options: [{
    //       key: 'taskCreate',
    //       label: '创建任务',
    //       clickFn: () => {
    //         console.log('创建任务')
    //       },
    //     }],
    //   },
    // ],
    tableProps: { // 表格配置，即antd中的Table组件的属性
      columns: [
        {
          title: t('robotName'),
          key: 'robotName',
          dataIndex: 'robotName',
          // width: 300,
          ellipsis: true,
          customRender: ({ record }) => (
            <div>
              <span class="inline-flex items-center w-full overflow-hidden">
                <Tooltip title={`ID：${record.robotId}`}>
                  <span class="truncate">{ record.robotName }</span>
                </Tooltip>
                {record.updateStatus === 1 && <SyncOutlined onClick={() => { handleRobotUpdate(record) }} />}
                {record.expiryDateStr && (
                  <span class="inline-block text-[12px] text-[#EC483E] bg-[#EC483E1A] rounded-[4px] px-[4px] py-[1px] ml-[5px] font-normal">
                    {record.expiryDateStr}
                  </span>
                )}
              </span>
            </div>
          ),
        },
        {
          title: t('updated'),
          key: 'updateTime',
          dataIndex: 'updateTime',
          width: 150,
          sorter: true,
          ellipsis: true,
        },
        {
          title: t('common.enabled'),
          dataIndex: 'version',
          key: 'version',
          ellipsis: true,
          customRender: ({ record }) => {
            return Number(record.version) === 0 ? '--' : `V${record.version}`
          },
        },
        {
          title: t('source'),
          dataIndex: 'sourceName',
          key: 'sourceName',
          ellipsis: true,
          customRender: ({ record }) => {
            return (<span class="h-[24px] px-[6px] py-[2px] leading-6 bg-[rgba(215,215,255,0.4)] dark:bg-[rgba(56,55,100,0.60)] text-[rgba(132,130,254,0.9)] rounded-[4px] flex-inline items-center justify-center">{ ROBOT_SOURCE_TEXT[record.sourceName] }</span>)
          },
        },
        {
          title: t('operate'),
          key: 'oper',
          dataIndex: 'oper',
          width: 200,
          customRender: ({ record }) => {
            const { sourceName } = record
            const moreOpts = sourceName === ROBOT_SOURCE_LOCAL ? localMoreOpts : marketMoreOpts
            return <OperMenu moreOpts={moreOpts} baseOpts={baseOpts} row={record} />
          },
        },
      ],
      size: 'middle',
      rowKey: 'resourceId',
      customRow: (record) => {
        return {
          class: record.usePermission === 0 ? 'opacity-50' : '',
          onDblclick: () => {
            expiredTip(record)
          },
        }
      },
      // 这块注释不要删，后期要上
      // rowSelection: {
      //   onChange: onSelectChange,
      // },
    },
    params: { // 绑定的表单配置的数据
      name: '',
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
    tableOption,
  }
}
