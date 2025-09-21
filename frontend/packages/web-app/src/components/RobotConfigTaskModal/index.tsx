import { NiceModal } from '@rpa/components'
import { Empty, Input, Table } from 'ant-design-vue'
import { isEmpty } from 'lodash-es'
import { defineComponent, ref } from 'vue'

import { getTableScrollY } from '@/utils/common'

import { getConfigParams } from '@/api/atom'
import { saveRobotConfigParamValue } from '@/api/robot'
import GlobalModal from '@/components/GlobalModal/index.vue'
import { useProcessStore } from '@/stores/useProcessStore'

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
      data.value = res || []
      loading.value = false
    }

    const handleOk = async () => {
      emit('ok', data.value)

      if (mode !== 'CRONTAB' && !isEmpty(data.value)) {
        saveRobotConfigParamValue(data.value, mode, props.robotId)
      }

      modal.hide()
    }

    if (mode === 'CRONTAB' && props.params) {
      getConfig().then(() => {
        props.params.forEach((i) => {
          const param = data.value.find(p => p.varName === i.varName)
          if (param) {
            param.varValue = i.varValue
          }
        })
      })
    }
    else {
      getConfig()
    }

    const columns = [
      {
        title: '参数名称',
        dataIndex: 'varName',
        key: 'varName',
        ellipse: true,
      },
      {
        title: '参数类型',
        dataIndex: 'varType',
        key: 'varType',
        ellipse: true,
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
          return <Input v-model={[record.varValue, 'value']} size="small" />
        },
      },
      {
        title: '参数描述',
        dataIndex: 'varDescribe',
        key: 'varDescribe',
        ellipse: true,
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
