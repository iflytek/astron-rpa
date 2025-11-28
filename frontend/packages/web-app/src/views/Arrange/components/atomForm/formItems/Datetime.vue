<script setup lang="ts">
import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const handleChange = (date: string) => {
  emits('update', props.item.key, date)
}
</script>

<template>
  <a-date-picker
    show-time
    value-format="YYYY-MM-DD HH:mm:ss"
    format="YYYY-MM-DD HH:mm:ss"
    :bordered="false"
    :input-read-only="true"
    placeholder=""
    class="datetime-picker"
    @update:value="handleChange"
  >
    <template #suffixIcon>
      <rpa-hint-icon title="选择日期时间" size="16" name="set-time" class="text-black dark:text-white opacity-45" />
    </template>
  </a-date-picker>
</template>

<style lang="scss" scoped>
.datetime-picker {
  width: 16px;
  height: 16px;
  padding: 0;

  :deep(.ant-picker-input) {
    > input {
      display: none;
    }

    .ant-picker-suffix {
      pointer-events: inherit;
      margin-left: 0;
      color: inherit;
      cursor: pointer;
    }
  }
}
</style>