<script setup lang="ts">
import { QuestionCircleFilled, QuestionCircleOutlined } from '@ant-design/icons-vue'
import { DatePicker, message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { useTranslation } from 'i18next-vue'
import { throttle } from 'lodash-es'
import { computed, inject, ref } from 'vue'

import { getEverydayExecuteTime, getEveryHoursExecuteTime, getEveryMinutesExecuteTime, getEveryMonthsExecuteTime, getEveryWeeksExecuteTime } from '@/utils/dayjsUtils'

import { taskFutureTimeNoCreate } from '@/api/task'
import { utilsManager } from '@/platform'
import type { Schedule } from '@/types/schedule'

import SelectWeek from './SelectWeek.vue'

const { taskJson, formState, enable } = defineProps({
  taskJson: {
    type: Object,
  },
  formState: {
    type: Object as () => Schedule,
  },
  enable: {
    type: Boolean,
    default: false,
  },
})

Object.assign(formState, taskJson)
const outFormRef = inject('formRef', ref(null))
const tempExecuteTime = computed(() => taskExecuteList.value[0] || '')
const taskExecuteList = ref([])
const { t } = useTranslation()

const frequencyOptions = [
  { label: t('taskTimeGroup.regular'), value: 'regular' },
  { label: t('taskTimeGroup.minutes'), value: 'minutes' },
  { label: t('taskTimeGroup.hours'), value: 'hours' },
  { label: t('taskTimeGroup.days'), value: 'days' },
  { label: t('taskTimeGroup.weeks'), value: 'weeks' },
  { label: t('taskTimeGroup.months'), value: 'months' },
  { label: t('taskTimeGroup.advance'), value: 'advance' },
]

function handleScheduleTypeChange() {
  handExecuteTimeChange()
}
// 本地计算，减少接口调用，提升响应性能
function handExecuteTimeChange() {
  taskExecuteList.value = []
  console.log('formState.frequency_flag: ', formState.frequency_flag)
  switch (formState.frequency_flag) {
    case 'regular':
      if (formState.time_expression && dayjs(formState.time_expression).isBefore(dayjs())) {
        taskExecuteList.value = []
      }
      else {
        taskExecuteList.value = [formState.time_expression]
      }
      break
    case 'advance':
      break
    case 'days':
      // 在每天的 formState.hours:formState.minutes 执行一次
      taskExecuteList.value = [
        getEverydayExecuteTime(formState.hours, formState.minutes, 0),
      ]
      break
    case 'hours':
      taskExecuteList.value = [
        getEveryHoursExecuteTime(formState.hours, formState.minutes, 0),
      ]
      break
    case 'minutes':
      taskExecuteList.value = [
        getEveryMinutesExecuteTime(formState.minutes, 0),
      ]
      break
    case 'weeks':
      // 在每周的 formState.weeks:formState.hours:formState.minutes 执行一次, weeks 是个数组
      taskExecuteList.value = [
        getEveryWeeksExecuteTime(formState.weeks, formState.hours, formState.minutes, 0),
      ]
      break
    case 'months':
      // 在每 months 的 weeks, formState.hours:formState.minutes 执行一次, months 是个整数，weeks 是个数组
      taskExecuteList.value = [
        getEveryMonthsExecuteTime(formState.months, formState.weeks, formState.hours, formState.minutes, 0),
      ]
  }
}

async function checkFirstTime() {
  const first = await getFirstRunTime()
  if (first && dayjs(formState.end_time).isBefore(first)) {
    message.warning('结束时间在首次运行之前')
    return false
  }
  else {
    return true
  }
}

async function onTimeEndChange() {
  const checked = formState.end_time_checked
  if (checked) {
    formState.end_time = formState.end_time ? formState.end_time : dayjs().add(1, 'day').format('YYYY-MM-DD HH:mm:ss')
    const isEffect = await checkFirstTime()
    if (!isEffect) {
      formState.end_time_checked = false
    }
  }
  else {
    formState.end_time = ''
  }
}

async function getFirstRunTime() {
  const nextTimes = await getNextExecuteTimes()
  if (nextTimes && Array.isArray(nextTimes) && nextTimes.length > 0) {
    const first = nextTimes[0]
    return first
  }
  else {
    return null
  }
}

function viewCorn() {
  utilsManager.openInBrowser('https://www.iflyrpa.com/help/article/850')
}

function getNextExecuteTimes() {
  return new Promise((resolve, reject) => {
    const { frequency_flag, time_expression, minutes, hours, weeks, months, cron_expression } = formState
    let fields = []
    let config
    switch (frequency_flag) {
      case 'regular':
        config = {
          frequency_flag,
          time_expression,
        }
        fields = ['time_expression']
        break
      case 'advance':
        config = {
          frequency_flag,
          cron_expression,
        }
        fields = ['cron_expression']
        break
      case 'days':
        config = {
          frequency_flag,
          hours,
          minutes,
        }
        fields = ['hours', 'minutes']
        break
      case 'hours':
        config = {
          frequency_flag,
          hours,
          minutes,
        }
        fields = ['hours', 'minutes']
        break
      case 'minutes':
        config = {
          frequency_flag,
          minutes,
        }
        fields = ['minutes']
        break
      case 'weeks':
        config = {
          frequency_flag,
          weeks,
          hours,
          minutes,
        }
        fields = ['weeks', 'hours', 'minutes']
        break
      case 'months':
        config = {
          frequency_flag,
          weeks,
          hours,
          minutes,
          months: [months],
        }
        fields = ['weeks', 'hours', 'minutes', 'months']
        break
      default:
    }
    outFormRef.value && outFormRef.value.validateFields(fields).then(() => {
      taskFutureTimeNoCreate({
        times: 5,
        ...config,
      }).then((res) => {
        const nextTimes = res.data?.next_exec_times || [] as Array<string>
        resolve(nextTimes)
      }, reject)
    })
  })
}

const openSheculedTaskList = throttle(async () => {
  const nextTimes = await getNextExecuteTimes()
  if (nextTimes && Array.isArray(nextTimes)) {
    taskExecuteList.value = nextTimes
  }
}, 1500, { leading: true, trailing: false })

defineExpose({
  checkFirstTime,
})
</script>

<template>
  <a-form-item name="frequency_flag">
    <template #label>
      <label for="form_item_frequency_flag" class="custom-label" :title="t('taskTimeSet')">{{ t('taskTimeSet') }}</label>
    </template>
    <a-radio-group v-model:value="formState.frequency_flag" :options="frequencyOptions" @change="handleScheduleTypeChange" />
  </a-form-item>

  <a-form-item v-if="formState.frequency_flag === 'regular'" class="form-item-no-label text-xs" label="" name="time_expression">
    <div class="text-[12px] flex items-center">
      {{ t('taskTimeConfig.atPrefix') }}
      <DatePicker v-model:value="formState.time_expression" show-time class="time-picker" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DD HH:mm:ss" @change="handExecuteTimeChange" />
      {{ t('taskTimeConfig.executeOnce') }}
    </div>
  </a-form-item>

  <a-form-item v-if="formState.frequency_flag === 'minutes'" class="form-item-no-label" label="" name="minutes">
    <div class="flex items-center text-[12px]">
      <span class="mr-2">{{ t('taskTimeConfig.every') }}</span>
      <a-input-number v-model:value="formState.minutes" class="number-input" :min="1" :max="59" @change="handExecuteTimeChange" />
      <span class="ml-2 text-gray-500 mr-2">{{ t('taskTimeConfig.minuteUnit') }}</span>
      <span>{{ t('taskTimeConfig.executeOnce') }}</span>
    </div>
  </a-form-item>

  <a-form-item v-if="formState.frequency_flag === 'hours'" class="form-item-no-label" label="" name="hours">
    <div class="flex items-center text-[12px]">
      <span class="mr-2">{{ t('taskTimeConfig.every') }}</span>
      <a-input-number v-model:value="formState.hours" class="number-input" :min="1" :max="24" @change="handExecuteTimeChange" />
      <span class="ml-2 text-gray-500 mr-2">{{ t('taskTimeConfig.hours') }}</span>
      <a-input-number v-model:value="formState.minutes" class="number-input" :min="0" :max="59" @change="handExecuteTimeChange" />
      <span class="ml-2 text-gray-500 mr-2">{{ t('taskTimeConfig.minuteUnit') }}</span>
      <span>{{ t('taskTimeConfig.executeOnce') }}</span>
    </div>
  </a-form-item>

  <a-form-item v-if="formState.frequency_flag === 'days'" class="form-item-no-label" label="" name="days">
    <div class="flex items-center text-[12px]">
      <span class="mr-2">{{ t('taskTimeConfig.daysPrefix') }}</span>
      <a-input-number v-model:value="formState.hours" class="number-input" :min="0" :max="23" @change="handExecuteTimeChange" />
      <span class="ml-2 text-gray-500 mr-2">{{ t('taskTimeConfig.hourUnit') }}</span>
      <a-input-number v-model:value="formState.minutes" class="number-input" :min="0" :max="59" @change="handExecuteTimeChange" />
      <span class="ml-2 text-gray-500 mr-2">{{ t('taskTimeConfig.minuteUnit') }}</span>
      <span>{{ t('taskTimeConfig.executeOnce') }}</span>
    </div>
  </a-form-item>

  <a-form-item v-if="formState.frequency_flag === 'weeks'" class="form-item-no-label" label="" name="weeks">
    <div class="flex items-center flex-wrap text-[12px]">
      <span class="mr-2">{{ t('taskTimeConfig.weeksPrefix') }}</span>
      <SelectWeek class="mr-2" :value="formState.weeks" @update:value="formState.weeks = $event; handExecuteTimeChange();" />
      <a-input-number v-model:value="formState.hours" class="number-input" :min="0" :max="23" @change="handExecuteTimeChange" />
      <span class="ml-2 text-gray-500 mr-2">{{ t('taskTimeConfig.hourUnit') }}</span>
      <a-input-number v-model:value="formState.minutes" class="number-input" :min="0" :max="59" @change="handExecuteTimeChange" />
      <span class="ml-2 text-gray-500 mr-2">{{ t('taskTimeConfig.minuteUnit') }}</span>
      <span class="">{{ t('taskTimeConfig.executeOnce') }}</span>
    </div>
  </a-form-item>

  <a-form-item v-if="formState.frequency_flag === 'months'" class="form-item-no-label" label="" name="months">
    <div class="flex items-center flex-wrap text-[12px]">
      <span class="mr-2">{{ t('taskTimeConfig.atPrefix') }}</span>
      <a-input-number v-model:value="formState.months as number" class="number-input " :min="1" :max="12" @change="handExecuteTimeChange" />
      <span class="ml-2 text-gray-500 mr-2">{{ t('taskTimeConfig.monthUnit') }}</span>
      <span>{{ t('taskTimeConfig.monthsWeekPrefix') }}</span>
      <SelectWeek class="ml-2 mr-2" :value="formState.weeks" @update:value="formState.weeks = $event; handExecuteTimeChange();" />
      <a-input-number v-model:value="formState.hours" class="number-input" :min="0" :max="23" @change="handExecuteTimeChange" />
      <span class="ml-2 text-gray-500 mr-2">{{ t('taskTimeConfig.hourUnit') }}</span>
      <a-input-number v-model:value="formState.minutes" class="number-input" :min="0" :max="59" @change="handExecuteTimeChange" />
      <span class="ml-2 text-gray-500 mr-2">{{ t('taskTimeConfig.minuteUnit') }}</span>
      <span>{{ t('taskTimeConfig.executeOnce') }}</span>
    </div>
  </a-form-item>

  <a-form-item v-if="formState.frequency_flag === 'advance'" name="cron_expression">
    <div class="flex items-center flex-wrap text-[12px]">
      <label for="form_item_cron_expression" class="custom-label mr-2">
        {{ t('taskTimeConfig.cronLabel') }}
        <a-tooltip :title="t('taskTimeConfig.cronTip')" placement="top">
          <QuestionCircleOutlined style="color: #1677ff; margin-left: 4px" />
        </a-tooltip>
      </label>
      <a-input v-model:value="formState.cron_expression" autocomplete="off" class="text-input" />
      <span class="advance-link ml-2" @click="viewCorn">{{ t('taskTimeConfig.cronView') }}</span>
    </div>
  </a-form-item>

  <div v-if="enable" class="check-for-next flex items-center bg-[#efefff] dark:bg-[#33326c]">
    <div class="w-[140px]">
      {{ tempExecuteTime || t('taskTimeConfig.noPlanTime') }}
    </div>
    <a-popover trigger="click" placement="right" overlay-class-name="time-popover">
      <template #title>
        <QuestionCircleFilled class="text-primary" />
        <span class="text-[12px] ml-2">{{ t('aboutExecuteTime') }}</span>
      </template>
      <template #content>
        <div class="flex flex-col text-[12px] time-popover-content">
          <p v-for="(time, index) in taskExecuteList" :key="index">
            {{ index + 1 }}. {{ time }}
          </p>
          <p v-if="taskExecuteList.length === 0">
            {{ t('taskTimeConfig.noPlanTime') }}
          </p>
        </div>
      </template>
      <a-button class="p-0 text-[12px]" :disabled="!enable" type="link" @click="openSheculedTaskList">
        {{ t('detail') }}
      </a-button>
    </a-popover>
  </div>

  <div name="end_time" class="mt-[20px]">
    <a-checkbox v-model:checked="formState.end_time_checked" @change="onTimeEndChange">
      {{ t('taskTimeConfig.timedCloseTask') }}
    </a-checkbox>
    <a-tooltip :title="t('taskTimeConfig.timedCloseTip')">
      <QuestionCircleOutlined />
    </a-tooltip>
    <a-date-picker
      v-model:value="formState.end_time"
      class="time-picker"
      :disabled-date="current => current < dayjs().startOf('day')"
      :show-time="{ format: 'HH:mm:ss' }"
      value-format="YYYY-MM-DD HH:mm:ss"
      type="date"
    />
  </div>
</template>

<style lang="scss" scoped>
.time-picker {
  width: 200px;
  margin: 0 8px;
}

.number-input {
  width: 60px;
  font-size: 12px;
}

.weekday-picker {
  width: 260px;
}

.text-input {
  width: 200px;
}

.advance-link {
  color: #1677ff;
  cursor: pointer;
}

.advance-link:hover {
  color: #4894ff;
}

:deep(.ant-form-item-explain-error) {
  font-size: 12px;
}
:deep(.ant-form-item .ant-form-item-control-input-content) {
  font-size: 12px;
}
:deep(.ant-picker .ant-picker-input > input) {
  font-size: 12px;
}
:deep(.ant-radio-wrapper) {
  margin-right: 14px;
}

.check-for-next {
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 12px;
}

.custom-label {
  &::before {
    display: inline-block;
    margin-inline-end: 4px;
    color: #ff4d4f;
    font-size: 14px;
    line-height: 1;
    content: '*';
  }
}
:global(.time-popover .ant-popover-content .ant-popover-inner) {
  position: relative;
  overflow: hidden;
}
:global(.time-popover .ant-popover-content .ant-popover-inner::after) {
  content: '';
  position: absolute;
  top: 0px;
  height: 4px;
  width: 100%;
  background: var(--color-primary);
  left: 0%;
}
</style>
