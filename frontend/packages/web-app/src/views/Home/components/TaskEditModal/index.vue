<script lang="ts" setup>
import { QuestionCircleOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { Space } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import {
  EXCEPTION_OPTION,
  TASK_FILE,
  TASK_HOTKEY,
  TASK_MAIL,
  TASK_MANUAL,
  TASK_TIME,
  TASK_TYPE_OPTION,
} from '../../config/task'

import FileConfig from './FileConfig.vue'
import { useTaskEdit } from './hooks/useTaskEdit'
import HotkeyConfig from './HotkeyConfig.vue'
import MailConfig from './MailConfig.vue'
import RobotTable from './RobotTable.vue'
import TimeConfig from './TimeConfig.vue'

const props = defineProps({
  taskId: {
    type: String, // 将类型定义为 String
    required: false,
  },
})
const emits = defineEmits(['refresh'])

const modal = NiceModal.useModal()
const { t } = useTranslation()

const {
  isEdit,
  formRef,
  rules,
  taskInfoForm,
  handleSave,
  confirmLoading,
  resetValid,
  timeConfigRef,
} = useTaskEdit(
  props.taskId,
  () => emits('refresh'),
  () => modal.hide(),
)

const taskTypeOptions = TASK_TYPE_OPTION.map((it) => {
  return { label: t(`taskTypeOption.${String(it.value)}`), value: it.value }
})

const exceptionOptions = EXCEPTION_OPTION.map((it) => {
  return { label: t(`taskExeceptOption.${String(it.value)}`), value: it.value }
})
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    class="modal-taskEditModal"
    :width="800"
    :title="`${isEdit ? t('editTask') : t('addTask')}`"
    :mask-closable="false"
  >
    <template #footer>
      <a-row>
        <a-col :span="8" class="text-left">
          <a-checkbox
            v-if="taskInfoForm.taskType !== TASK_MANUAL"
            v-model:checked="taskInfoForm.taskEnable"
          >
            {{ t("enableTask") }}
          </a-checkbox>
        </a-col>
        <a-col :span="8" />
        <a-col :span="8">
          <Space>
            <a-button @click="modal.hide">
              {{ t("cancel") }}
            </a-button>
            <a-button
              type="primary"
              :loading="confirmLoading"
              @click="handleSave"
            >
              {{ t("confirm") }}
            </a-button>
          </Space>
        </a-col>
      </a-row>
    </template>
    <a-form
      ref="formRef"
      class="p-4"
      layout="vertical"
      :model="taskInfoForm"
      :rules="rules"
    >
      <a-row>
        <a-col :span="12" class="p-2">
          <a-form-item :label="t('taskName')" name="name">
            <a-input
              v-model:value="taskInfoForm.name"
              class="text-[12px] h-[32px]"
              autocomplete="off"
              :placeholder="t('taskNamePlaceholder')"
            />
          </a-form-item>
        </a-col>
        <a-col :span="6" class="p-2">
          <a-form-item :label="t('triggerType')" name="taskType" required>
            <a-select
              v-model:value="taskInfoForm.taskType"
              popup-class-name="task-type"
              class="text-[12px]"
              :options="taskTypeOptions"
              @change="resetValid"
            />
          </a-form-item>
        </a-col>
        <a-col :span="6" class="p-2">
          <a-form-item
            name="exceptionHandleWay"
            :label="t('exceptionHandling')"
          >
            <template #tooltip>
              <a-tooltip :title="t('taskExceptionHandlingTip')">
                <QuestionCircleOutlined style="margin-left: 4px" />
              </a-tooltip>
            </template>
            <a-radio-group
              v-model:value="taskInfoForm.exceptional"
              :options="exceptionOptions"
            />
          </a-form-item>
        </a-col>
      </a-row>

      <a-form-item :label="t('robot')" name="robotInfoList" required>
        <template #tooltip>
          <a-tooltip :title="t('robotExecuteOrder')">
            <QuestionCircleOutlined style="margin-left: 4px" />
          </a-tooltip>
        </template>
        <RobotTable
          :robots="taskInfoForm.robotInfoList"
          @update:robots="taskInfoForm.robotInfoList = $event"
        />
      </a-form-item>

      <!-- 不同触发方式的config -->
      <!-- 时间触发 -->
      <TimeConfig
        v-if="taskInfoForm.taskType === TASK_TIME"
        ref="timeConfigRef"
        :form-state="taskInfoForm.schedule"
        :task-json="taskInfoForm.taskJson"
        :enable="taskInfoForm.taskEnable"
      />
      <!-- 文件触发 -->
      <FileConfig
        v-if="taskInfoForm.taskType === TASK_FILE"
        :form-state="taskInfoForm.file"
        :task-json="taskInfoForm.taskJson"
      />
      <!-- 邮件触发 -->
      <MailConfig
        v-if="taskInfoForm.taskType === TASK_MAIL"
        :form-state="taskInfoForm.mail"
        :task-json="taskInfoForm.taskJson"
      />
      <!-- 热键触发 -->
      <HotkeyConfig
        v-if="taskInfoForm.taskType === TASK_HOTKEY"
        :form-state="taskInfoForm.hotkey"
        :task-json="taskInfoForm.taskJson"
      />

      <div class="check-list flex items-center mt-[20px]">
        <!-- 超时结束 -->
        <div class="flex h-10 items-center" name="timeoutEnable">
          <label for="form_item_timeoutEnable" class="custom-label">
            <a-checkbox v-model:checked="taskInfoForm.timeoutEnable">{{
              t("taskTimeout")
            }}</a-checkbox>
            <a-tooltip :title="t('taskExecuteTimeout')" placement="top">
              <QuestionCircleOutlined style="" />
            </a-tooltip>
          </label>
          <div class="flex items-center ml-2">
            <a-input-number
              v-if="taskInfoForm.timeoutEnable"
              v-model:value="taskInfoForm.timeout"
              class="w-[80px] text-[12px]"
              :min="0"
              :max="9999"
            />
            <span v-if="taskInfoForm.timeoutEnable" style="margin-left: 4px">{{
              t("minutes")
            }}</span>
          </div>
        </div>

        <div
          v-if="taskInfoForm.taskType !== TASK_MANUAL"
          class="flex h-10 items-center ml-8"
          name="queueEnable"
        >
          <label for="form_item_queueEnable" class="custom-label">
            <a-checkbox v-model:checked="taskInfoForm.queueEnable">{{
              t("taskQueue")
            }}</a-checkbox>
            <a-tooltip :title="t('taskQueueEnable')" placement="top">
              <QuestionCircleOutlined />
            </a-tooltip>
          </label>
        </div>
      </div>
    </a-form>
  </a-modal>
</template>

<style lang="scss">
.modal-taskEditModal {
  max-height: 500px;
  ::-webkit-scrollbar {
    width: 6px;
  }
  .ant-modal-body {
    max-height: 460px;
    overflow-y: auto;
    padding-bottom: 40px;
    // border-top: 1px solid $color-border;
    // border-bottom: 1px solid $color-border;
  }

  .ant-form-item {
    margin-bottom: 20px;
    .ant-select-selection-item {
      font-size: 12px;
    }
    .ant-btn {
      font-size: 12px;
    }
  }
  // .ant-form-item:last-child {
  //   margin-bottom: 2px;
  // }

  .title::before {
    content: '*';
    color: #f5222d;
    margin-right: 4px;
    font-size: $font-size;
    font-family: SimSun, sans-serif;
  }

  .timeSelect {
    display: flex;
    justify-content: flex-start;
    align-items: center;
  }

  .center {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .ant-transfer .ant-transfer-operation .ant-btn:first-child {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .check-list {
    margin-bottom: 5px;
  }
  .ant-form-item-explain-error {
    font-size: 12px;
  }
  .ant-form-item .ant-form-item-label {
    // text-align: right;
    font-size: 12px;
  }
  .ant-checkbox + span {
    padding-inline-start: 4px;
    padding-inline-end: 4px;
  }

  .check-item-right {
    margin-left: 13px;
    margin-right: 6px;
  }
}

.check-list .ant-form-item .ant-form-item-label > label::after {
  content: '' !important;
  width: 3px;
}
.task-type .ant-select-dropdown .ant-select-item {
  font-size: 12px;
}
</style>
