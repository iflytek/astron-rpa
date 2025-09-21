<script lang="ts" setup>
import { useTranslation } from 'i18next-vue'

import { Hotkeys } from '../../config/task'

interface Hotkey {
  shortcuts: string[]
  key: string
}

const { taskJson, formState } = defineProps({
  taskJson: {
    type: Object,
  },
  formState: {
    type: Object as () => Hotkey,
  },
})
const { t } = useTranslation()
Object.assign(formState, taskJson)
const hotkeys = Hotkeys()
// formState.shortcuts 删除最后一个键值
formState.key = formState.shortcuts[formState.shortcuts.length - 1] || ''
formState.shortcuts = formState.shortcuts.filter(item => item !== formState.key)
</script>

<template>
  <a-form-item name="hotkey">
    <template #label>
      <label for="form_item_hotkey" class="custom-label">
        {{ t('hotkeySelect') }}
      </label>
    </template>
    <!-- ctrl + Shift + Alt + Win checkbox -->
    <a-checkbox-group v-model:value="formState.shortcuts" class="text-[12px]">
      <a-checkbox value="ctrl">
        Ctrl +
      </a-checkbox>
      <a-checkbox value="shift">
        Shift +
      </a-checkbox>
      <a-checkbox value="alt">
        Alt +
      </a-checkbox>
      <a-checkbox value="win">
        Win +
      </a-checkbox>
    </a-checkbox-group>
    <span class="text-[12px]">{{ t('keyboardValue') }}</span>
    <!-- select 按键F1-F12、0-9、A-Z -->
    <a-select v-model:value="formState.key" class="text-[12px] ml-4" style="width: 120px" :placeholder="t('pleaseChoose')">
      <a-select-option v-for="item in hotkeys" :key="item.value" class="text-[12px]" :value="item.value">
        {{ item.value }}
      </a-select-option>
    </a-select>
  </a-form-item>
</template>

<style lang="scss" scoped>
:deep(.ant-form-item-explain-error) {
  font-size: 12px;
}
:deep(.ant-form-item .ant-form-item-label) {
  text-align: left;
}
:deep(.ant-select-selection-placeholder) {
  font-size: 12px;
}
:deep(.ant-checkbox-wrapper) {
  margin-right: 14px;
}
.custom-label {
  &::before {
    display: inline-block;
    margin-inline-end: 4px;
    color: #ff4d4f;
    font-size: 12px;
    font-family: SimSun, sans-serif;
    line-height: 1;
    content: '*';
  }
}
</style>
