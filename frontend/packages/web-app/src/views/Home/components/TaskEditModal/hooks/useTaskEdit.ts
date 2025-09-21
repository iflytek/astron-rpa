import type { FormInstance } from 'ant-design-vue'
import { message } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import { useTranslation } from 'i18next-vue'
import { computed, provide, reactive, ref, shallowRef, watch } from 'vue'

import { getTaskInfo, insertTask, isNameCopy, updateTask } from '@/api/task'
import { EMAIL_OPTIONS_MAP } from '@/constants/mail'
import type { Task, TaskTrigger } from '@/types/schedule'
import { TASK_TYPE } from '@/views/Home/config/task'
import type { resOption } from '@/views/Home/types'

export function useTaskEdit(taskId: string, handleRefresh: () => void, handleClose: () => void) {
  const { t } = useTranslation()
  const isEdit = computed(() => !!taskId)
  const formRef = shallowRef<FormInstance>()
  const mailTableRef = shallowRef()
  const timeConfigRef = shallowRef()
  provide('mailTableRef', mailTableRef)
  provide('formRef', formRef)
  const taskInfoForm = reactive<Task>({
    taskId: '', // 任务id
    name: '', // 任务名称
    robotInfoList: [],
    taskJson: null,
    taskType: 'manual',
    exceptional: 'stop',
    taskEnable: true,
    queueEnable: false,
    timeoutEnable: false,
    timeout: 0,
    // 邮件任务
    mail: {
      user_mail: '',
      user_authorization: '',
      mail_flag: '163',
      end_time: '',
      interval_time: 1,
      condition: '',
      sender_text: '',
      receiver_text: '',
      theme_text: '',
      content_text: '',
      attachment: false,
      custom_mail_server: '',
      custom_mail_port: '',
    },
    // 定时任务
    schedule: {
      end_time: '',
      frequency_flag: 'regular',
      minutes: 1,
      hours: 1,
      weeks: [],
      months: 1,
      time_expression: null,
      cron_expression: '',
    },
    // 文件任务
    file: {
      directory: '',
      relative_sub_path: false,
      events: [],
      files_or_type: '',
    },
    // 快捷键任务
    hotkey: {
      shortcuts: [],
      key: '',
    },
  })
  const confirmLoading = ref<boolean>(false)
  const rules: Record<string, Rule[]> = {
    name: [
      { required: true, message: t('taskRuleRequire.taskNameRequired'), trigger: 'change' },
      { max: 20, message: t('taskRuleRequire.taskNameMax'), trigger: 'change' },
      { validator: checkDuplicateTaskName, trigger: 'change' },
    ],
    robotInfoList: [
      { required: true, message: '', trigger: 'change' },
      { validator: validEmptyRobots, trigger: 'change' },
    ],
    // 邮件
    userMail: [{ validator: validMailAccount, trigger: 'change' }],
    intervalTime: [{ validator: validIntervalTime, trigger: 'change' }],
    // 文件
    directory: [{ validator: validDirectory, trigger: 'change' }],
    files_or_type: [{ validator: validFilesOrType, trigger: 'change' }],
    events: [{ validator: validEvents, trigger: 'change' }],
    // 热键
    hotkey: [{ validator: validHotkey, trigger: 'change' }],
    // 时间
    time_expression: [{ validator: validTimeExpression, trigger: 'change' }],
    minutes: [{ validator: validMinutes, trigger: 'change' }],
    hours: [{ validator: validHours, trigger: 'change' }],
    weeks: [{ validator: validWeeks, trigger: 'change' }],
    months: [{ validator: validMonths, trigger: 'change' }],
    cron_expression: [{ validator: validCron, trigger: 'change' }],
    end_time: [{ validator: validEndTime, trigger: 'change' }],
  }

  // 监听robotInfoList变化，校验必填项
  watch(() => taskInfoForm.robotInfoList, () => {
    formRef.value && formRef.value.validate()
  })
  // 监听 directory变化，校验必填项
  watch(
    () => taskInfoForm.file.directory,
    () => formRef.value && formRef.value.validate(),
  )

  async function getTask() {
    getTaskInfo({ taskId }).then((res) => {
      if (res.data) {
        const { enable, exceptional, name, robotInfoVoList, taskId, taskJson, taskType, queueEnable, timeout } = res.data
        taskInfoForm.enable = enable
        taskInfoForm.taskEnable = !!enable
        taskInfoForm.exceptional = exceptional
        taskInfoForm.name = name
        taskInfoForm.robotInfoList = robotInfoVoList
        taskInfoForm.taskId = taskId
        taskInfoForm.taskType = taskType
        taskInfoForm.taskJson = JSON.parse(taskJson)
        taskInfoForm.queueEnable = !!queueEnable
        taskInfoForm.timeout = timeout || 0
        taskInfoForm.timeoutEnable = !!timeout
        // 转换 文件配置里面的 files_or_type 数组转字符串 逗号分割
        if (taskInfoForm.taskType === TASK_TYPE.TASK_FILE && taskInfoForm.taskJson.files_or_type && Array.isArray(taskInfoForm.taskJson.files_or_type)) {
          taskInfoForm.file.files_or_type = taskInfoForm.taskJson.files_or_type.join(',')
          taskInfoForm.taskJson.files_or_type = taskInfoForm.taskJson.files_or_type.join(',')
        }
        // 转换 定时配置里面的 months 数组转数字
        if (taskInfoForm.taskType === TASK_TYPE.TASK_TIME && taskInfoForm.taskJson.months && Array.isArray(taskInfoForm.taskJson.months)) {
          taskInfoForm.schedule.months = taskInfoForm.taskJson.months[0]
          taskInfoForm.taskJson.months = taskInfoForm.taskJson.months[0]
        }
        // 转换end_time_checked
        if (taskInfoForm.taskType === TASK_TYPE.TASK_TIME && taskInfoForm.taskJson.end_time) {
          taskInfoForm.schedule.end_time_checked = true
        }
      }
    })
  }
  // 表格校验中增加对是否存在同名任务的判断
  async function checkDuplicateTaskName(rule, value) {
    if (!value)
      return Promise.resolve()
    if (isEdit.value)
      return Promise.resolve()
    const checkRes = (await isNameCopy({
      // taskId,
      name: value,
    })) as resOption

    if (checkRes?.data) {
      return Promise.reject(new Error(t('taskRuleRequire.taskNameDuplicate')))
    }
    return Promise.resolve()
  }
  async function validIntervalTime() {
    if (!taskInfoForm.mail.interval_time)
      return Promise.reject(new Error(t('taskRuleRequire.intervalTimeRequired')))
    return Promise.resolve()
  }

  async function validMailAccount() {
    if (!taskInfoForm.mail.user_mail)
      return Promise.reject(new Error(t('taskRuleRequire.mailRequired')))
    return Promise.resolve()
  }

  async function validDirectory() {
    if (!taskInfoForm.file.directory)
      return Promise.reject(new Error(t('taskRuleRequire.directoryRequired')))
    return Promise.resolve()
  }

  async function validFilesOrType() {
    if (!taskInfoForm.file.files_or_type) {
      return Promise.reject(new Error(t('taskRuleRequire.filesOrTypeRequired')))
    }
    return Promise.resolve()
  }

  async function validEvents() {
    if (!taskInfoForm.file.events.length)
      return Promise.reject(new Error(t('taskRuleRequire.eventsRequired')))
    return Promise.resolve()
  }

  async function validHotkey() {
    if (!taskInfoForm.hotkey.shortcuts.length)
      return Promise.reject(new Error(t('taskRuleRequire.hotkeyRequired')))
    if (!taskInfoForm.hotkey.key)
      return Promise.reject(new Error(t('taskRuleRequire.hotkeyRequired')))
    return Promise.resolve()
  }

  async function validTimeExpression() {
    const timeExpression = taskInfoForm.schedule.time_expression
    if (!timeExpression)
      return Promise.reject(new Error(t('taskRuleRequire.timeRequired')))
    return Promise.resolve()
  }

  async function validMinutes() {
    const minutes = taskInfoForm.schedule.minutes
    if (!minutes)
      return Promise.reject(new Error(t('taskRuleRequire.minutesRequired')))
    return Promise.resolve()
  }

  async function validHours() {
    const hours = taskInfoForm.schedule.hours
    if (!hours)
      return Promise.reject(new Error(t('taskRuleRequire.hoursRequired')))
    return Promise.resolve()
  }

  async function validWeeks() {
    const weeks = taskInfoForm.schedule.weeks
    if (!weeks.length)
      return Promise.reject(new Error(t('taskRuleRequire.weeksRequired')))
    return Promise.resolve()
  }

  async function validMonths() {
    const weeks = taskInfoForm.schedule.weeks
    if (!weeks.length)
      return Promise.reject(new Error(t('taskRuleRequire.weeksRequired')))
    return Promise.resolve()
  }

  async function validCron() {
    const cronExpression = taskInfoForm.schedule.cron_expression
    if (!cronExpression)
      return Promise.reject(new Error(t('taskRuleRequire.cronRequired')))
    return Promise.resolve()
  }

  async function validEndTime() {
    const endTime = taskInfoForm.schedule.end_time
    const endTimeChecked = taskInfoForm.schedule.end_time_checked
    if (endTimeChecked && !endTime)
      return Promise.reject(new Error(t('taskRuleRequire.endTimeRequired')))
    return Promise.resolve()
  }

  async function validEmptyRobots(_rule: Rule, value: Array<any>) {
    if (value.length === 0) {
      return Promise.reject(new Error(t('taskRuleRequire.robotsRequired')))
    }
    else {
      return Promise.resolve()
    }
  }

  function resetValid() {
    formRef.value.clearValidate()
  }

  // 重置
  function handleReset() {
    formRef.value.resetFields()
  }

  /**
   * 保存计划任务
   */
  function handleSave() {
    const task = taskInfoFn()
    console.log('task: ', task)
    formRef.value
      .validate()
      .then(async () => {
        // 校验邮箱配置
        if (taskInfoForm.taskType === 'mail') {
          const validMail = mailTableRef.value && mailTableRef.value.mailTableValidate()
          if (!validMail) {
            return
          }
        }
        if (taskInfoForm.taskType === 'schedule' && taskInfoForm.schedule.end_time_checked && timeConfigRef.value) {
          const endTimeBeforeFirst = await timeConfigRef.value.checkFirstTime()
          if (!endTimeBeforeFirst) {
            return
          }
        }
        confirmLoading.value = true
        if (isEdit.value) {
          await updateTask(task)
        }
        else {
          await insertTask(task)
        }
        message.success(`${isEdit.value ? t('taskEditSuccess') : t('taskAddSuccess')}`)
        handleRefresh()
        handleClose()
        confirmLoading.value = false
      })
      .catch(() => {
        confirmLoading.value = false
      })
  }
  /**
   * 组装 task
   */
  function taskInfoFn() {
    const {
      taskId, // 任务id
      name, // 任务名称
      robotInfoList,
      taskType,
      exceptional,
      taskEnable,
      queueEnable,
      timeoutEnable,
      timeout,
    } = taskInfoForm

    const taskJson: TaskTrigger = {}

    switch (taskType) {
      case TASK_TYPE.TASK_TIME:
        taskJson.frequency_flag = taskInfoForm.schedule.frequency_flag
        if (taskInfoForm.schedule.frequency_flag === 'regular') {
          taskJson.time_expression = taskInfoForm.schedule.time_expression
        }
        if (taskInfoForm.schedule.frequency_flag === 'advance') {
          taskJson.cron_expression = taskInfoForm.schedule.cron_expression
        }
        if (taskInfoForm.schedule.frequency_flag === 'days') {
          taskJson.minutes = Number(taskInfoForm.schedule.minutes)
          taskJson.hours = Number(taskInfoForm.schedule.hours)
        }
        if (taskInfoForm.schedule.frequency_flag === 'weeks') {
          taskJson.minutes = Number(taskInfoForm.schedule.minutes)
          taskJson.hours = Number(taskInfoForm.schedule.hours)
          taskJson.weeks = taskInfoForm.schedule.weeks.map(item => Number(item))
        }
        if (taskInfoForm.schedule.frequency_flag === 'months') {
          taskJson.minutes = Number(taskInfoForm.schedule.minutes)
          taskJson.hours = Number(taskInfoForm.schedule.hours)
          taskJson.weeks = taskInfoForm.schedule.weeks.map(item => Number(item))
          taskJson.months = [Number(taskInfoForm.schedule.months)]
        }
        if (taskInfoForm.schedule.frequency_flag === 'hours') {
          taskJson.minutes = Number(taskInfoForm.schedule.minutes)
          taskJson.hours = Number(taskInfoForm.schedule.hours)
        }
        if (taskInfoForm.schedule.frequency_flag === 'minutes') {
          taskJson.minutes = Number(taskInfoForm.schedule.minutes)
        }
        if (taskInfoForm.schedule.end_time_checked) {
          taskJson.end_time = taskInfoForm.schedule.end_time
        }
        break
      case TASK_TYPE.TASK_FILE: {
        taskJson.directory = taskInfoForm.file.directory
        taskJson.relative_sub_path = taskInfoForm.file.relative_sub_path
        taskJson.events = taskInfoForm.file.events
        taskJson.files_or_type = stringToArray(taskInfoForm.file.files_or_type)
        break
      }
      case TASK_TYPE.TASK_MAIL:
        taskJson.mail_flag = EMAIL_OPTIONS_MAP[taskInfoForm.mail.mail_flag]
        taskJson.interval_time = taskInfoForm.mail.interval_time
        taskJson.attachment = taskInfoForm.mail.attachment
        taskJson.sender_text = taskInfoForm.mail.sender_text
        taskJson.receiver_text = taskInfoForm.mail.receiver_text
        taskJson.theme_text = taskInfoForm.mail.theme_text
        taskJson.content_text = taskInfoForm.mail.content_text
        taskJson.condition = taskInfoForm.mail.condition
        taskJson.user_mail = taskInfoForm.mail.user_mail
        taskJson.user_authorization = taskInfoForm.mail.user_authorization
        if (taskJson.mail_flag === 'advance') {
          taskJson.custom_mail_server = taskInfoForm.mail.custom_mail_server
          taskJson.custom_mail_port = taskInfoForm.mail.custom_mail_port
        }
        break
      case TASK_TYPE.TASK_HOTKEY:
        taskJson.shortcuts = taskInfoForm.hotkey.shortcuts.filter(item => item)
        taskJson.shortcuts.push(taskInfoForm.hotkey.key)
        taskJson.shortcuts.filter(item => item !== '')
        // 去重
        taskJson.shortcuts = [...new Set(taskJson.shortcuts)]
        break
      default:
        break
    }
    console.log('taskJson: ', taskJson)
    return {
      taskId,
      name,
      robotInfoList,
      taskJson: JSON.stringify(taskJson),
      taskType,
      exceptional,
      enable: taskEnable ? 1 : 0,
      timeout: timeoutEnable ? timeout : 0,
      queueEnable: queueEnable ? 1 : 0,
    }
  }
  /**
   * 字符串转换为数组
   */
  function stringToArray(str: string, delimiter = ',') {
    str = str.replaceAll('，', ',').replaceAll('、', ',')
    const arr = str.split(delimiter)
    return arr.filter(item => item)
  }

  if (isEdit.value) {
    getTask()
  }

  return {
    isEdit,
    formRef,
    taskInfoForm,
    rules,
    confirmLoading,
    handleReset,
    handleSave,
    resetValid,
    timeConfigRef,
  }
}
