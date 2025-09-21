<script lang="ts" setup>
import { FolderOutlined, QuestionCircleOutlined } from '@ant-design/icons-vue'
import { useTranslation } from 'i18next-vue'

import { utilsManager } from '@/platform'
import type { File } from '@/types/schedule'

import { FileEvents } from '../../config/task'

const { taskJson, formState } = defineProps({
  taskJson: {
    type: Object,
  },
  formState: {
    type: Object as () => File,
  },
})

Object.assign(formState, taskJson)

const { t } = useTranslation()

function chooseFolder() {
  utilsManager.showDialog({ file_type: 'folder' }).then((res: string) => {
    formState.directory = res
  })
}
const fileEvents = FileEvents.map((it) => {
  return { label: t(`taskFileEvents.${String(it.value)}`), value: it.value }
})
</script>

<template>
  <a-row>
    <a-col :span="12">
      <a-form-item name="directory">
        <template #label>
          <label for="form_item_directory" class="custom-label" :title="t('watchFolder')">{{ t('watchFolder') }}</label>
        </template>
        <a-input v-model:value="formState.directory" class="text-[12px] h-[32px]" autocomplete="off" :placeholder="t('watchFolderPlaceholder')">
          <template #suffix>
            <FolderOutlined class="cursor-pointer" @click="chooseFolder" />
          </template>
        </a-input>
        <!-- 是否包含子路径 -->
        <a-checkbox v-model:checked="formState.relative_sub_path" class="mt-4">
          {{ t('includeSubfolder') }}
          <a-tooltip :title="t('includeSubfolderTip')">
            <QuestionCircleOutlined style="color: #1677ff; margin-left: 4px" />
          </a-tooltip>
        </a-checkbox>
      </a-form-item>
    </a-col>
    <a-col :span="12">
      <!-- 文件类型 -->
      <a-form-item name="files_or_type" class="ml-4">
        <template #label>
          <label for="form_item_files_or_type" class="custom-label" :title="t('fileType')">{{ t('fileType') }}</label>
          <a-tooltip :title="t('fileTypeTip')">
            <QuestionCircleOutlined style="color: #1677ff; margin-left: 4px" />
          </a-tooltip>
        </template>
        <a-input v-model:value="formState.files_or_type" class="text-[12px] h-[32px]" autocomplete="off" :placeholder="t('fileTypePlaceholder')" />
      </a-form-item>
    </a-col>
  </a-row>

  <!-- 监控事件， 创建，删除，更新，重命名 -->
  <a-form-item name="events">
    <template #label>
      <label for="form_item_events" class="custom-label" :title="t('fileEvents')">{{ t('fileEvents') }}</label>
    </template>
    <a-checkbox-group v-model:value="formState.events" :options="fileEvents" />
  </a-form-item>
</template>

<style lang="scss" scoped>
:deep(.ant-form-item-explain-error) {
  font-size: 12px;
}
:deep(.ant-form-item .ant-form-item-label) {
  text-align: left;
}
:deep(.ant-checkbox-wrapper) {
  margin-right: 14px;
}
.custom-label {
  &::before {
    display: inline-block;
    margin-inline-end: 4px;
    color: #ff4d4f;
    font-size: 14px;
    font-family: SimSun, sans-serif;
    line-height: 1;
    content: '*';
  }
}
</style>
