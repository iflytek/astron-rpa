import useRequest from '@vue-hooks-plus/use-request'
import { DatePicker, Form, Select, Spin } from 'ant-design-vue'
import dayjs from 'dayjs'
import { defineComponent, reactive } from 'vue'

import { getRobotRecordOverview } from '@/api/robot'
import NDataCards from '@/components/NDataCards/index.vue'
import type { DataCardItem } from '@/components/NDataCards/index.vue'
import RecordTable from '@/views/Home/components/RecordTable/index.vue'

import { useBasicStore } from './basicStore'

const labelClasses = 'text-[12px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)] font-normal pb-[8px]'

export default defineComponent({
  name: 'RecordContent',
  props: {
    robotId: {
      type: String,
      required: true,
    },
    version: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    const { data: basicInfo } = useBasicStore()
    const formState = reactive({
      deadline: dayjs(),
      version: props.version,
    })

    const { data, loading } = useRequest<DataCardItem[]>(
      () =>
        getRobotRecordOverview({
          robotId: props.robotId,
          version: formState.version,
          deadline: formState.deadline.format('YYYY-MM-DD'),
        }),
      {
        initialData: [],
        refreshDeps: true,
      },
    )

    const disabledDate = (current: dayjs.Dayjs) => {
      return current && current > dayjs()
    }

    return () => (
      <Spin spinning={loading.value}>
        <div class="text-base font-semibold mb-[12px]">执行概况</div>
        <Form layout="vertical" model={formState} colon={false} class="flex items-center justify-start !h-[74px] pt-[12px]">
          <Form.Item name="deadline" class="w-[50%] mr-[8px]">
            <div v-slot="label" class={labelClasses}>截止日期</div>
            <DatePicker v-model={[formState.deadline, 'value']} disabledDate={disabledDate} allowClear={false} class="w-full" />
          </Form.Item>
          <Form.Item name="version" class="w-[50%] ml-[8px]">
            <div v-slot="label" class={labelClasses}>选择版本</div>
            <Select v-model={[formState.version, 'value']}>
              {basicInfo.value.versionInfoList.map(item => (
                <Select.Option
                  v-for="item in basicInfo.versionInfoList"
                  key={item.versionNum}
                  value={item.versionNum}
                >
                  {`版本${item.versionNum}`}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
        <NDataCards list={data.value} />
        <div class="text-base font-semibold mt-[20px] mb-[6px]">执行记录</div>
        <RecordTable class="!h-[340px]" robotId={props.robotId} />
      </Spin>
    )
  },
})
