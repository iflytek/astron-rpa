import { NiceModal } from '@rpa/components'
import { Empty, Table } from 'ant-design-vue'
import { isEmpty } from 'lodash-es'
import { defineComponent, ref } from 'vue'

import { getTableScrollY } from '@/utils/common'

import { getConfigParams } from '@/api/atom'
import { saveRobotConfigParamValue } from '@/api/robot'
import GlobalModal from '@/components/GlobalModal/index.vue'
import { useProcessStore } from '@/stores/useProcessStore'
import VarValueEditor from '@/views/Arrange/components/bottomTools/components/ConfigParameter/VarValueEditor.vue'

const _RobotConfigTaskModal = defineComponent({
  props: {
    robotId: {
      type: String,
      required: true,
    },
    mode: {
      type: String as () => RPA.RunMode,
    },
    params: {
      type: Array as () => RPA.ConfigParamData[],
      default: () => [],
    },
  },
  emits: ['ok'],
  setup(props, { emit }) {
    const modal = NiceModal.useModal()
    const processStore = useProcessStore()

    const mode = props.mode || 'EXECUTOR'
    const data = ref<RPA.ConfigParamData[]>([])
    const loading = ref(false)

    const getConfig = async () => {
      loading.value = true
      const res = await getConfigParams({ robotId: props.robotId, mode })
      const configData = res || []

      if (mode === 'CRONTAB' && props.params && props.params.length > 0) {
        const paramMap = new Map(props.params.map(p => [p.varName, p.varValue]))
        configData.forEach((param) => {
          if (paramMap.has(param.varName)) {
            param.varValue = paramMap.get(param.varName)
          }
        })
      }

      data.value = configData
      loading.value = false
    }

    const handleOk = async () => {
      emit('ok', data.value)

      if (mode !== 'CRONTAB' && !isEmpty(data.value)) {
        saveRobotConfigParamValue(data.value, mode, props.robotId)
      }

      modal.hide()
    }

    getConfig()

    const columns = [
      {
        title: '参数名称',
        dataIndex: 'varName',
        key: 'varName',
        ellipsis: true,
      },
      {
        title: '参数类型',
        dataIndex: 'varType',
        key: 'varType',
        ellipsis: true,
        customRender: ({ record }) => {
          const typeSchema = processStore.globalVarTypeList[record.varType]
          return <span>{typeSchema?.desc}</span>
        },
      },
      {
        title: '参数值',
        dataIndex: 'varValue',
        key: 'varValue',
        width: 200,
        customRender: ({ record }) => {
          return <VarValueEditor varValue={record.varValue} var-type={record.varType} onUpdate:varValue={value => record.varValue = value} class="max-w-[180px]" />
        },
      },
      {
        title: '参数描述',
        dataIndex: 'varDescribe',
        key: 'varDescribe',
        ellipsis: true,
      },
    ]

    const tableMaxSize = window.innerHeight - 300

    return () => (
      <GlobalModal
        {...NiceModal.antdModal(modal)}
        width={600}
        title="参数配置"
        onOk={handleOk}
      >
        <Table
          size="small"
          scroll={{ y: getTableScrollY(tableMaxSize, data.value.length) }}
          loading={loading.value}
          columns={columns}
          dataSource={data.value.filter(param => param.varDirection === 0)}
          pagination={false}
          v-slots={{
            emptyText: () => <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} />,
          }}
        />
      </GlobalModal>
    )
  },
})

export const RobotConfigTaskModal = NiceModal.create(_RobotConfigTaskModal)
