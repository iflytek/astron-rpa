<!-- @format -->
<script setup lang="ts">
import { QuestionCircleOutlined } from '@ant-design/icons-vue'
import { provide } from 'vue'

import type { VariableTypes } from '@/views/Arrange/types/atomForm'

import AtomConfig from '../atomForm/AtomConfig.vue'

defineProps({
  customData: {
    type: Array<RPA.AtomDisplayItem>,
    default: () => [],
  },
})

provide<VariableTypes>('variableType', 'globalVariables')
</script>

<template>
  <a-form :model="customData" layout="vertical" class="custom-table-form">
    <a-form-item v-for="item in customData" :key="item.uniqueKey">
      <!-- 变量选择器 -->
      <template #label>
        <span>{{ item.name }}</span>
        <a-tooltip :title="$t(`customElement.${item.name}`)">
          <QuestionCircleOutlined style="margin-left: 4px" />
        </a-tooltip>
      </template>
      <AtomConfig :form-item="item" />
    </a-form-item>
  </a-form>
</template>

<style lang="scss" scoped>
.custom-table-form {
  :deep(.ant-form-item-label) {
    padding-top: 4px;
  }

  :deep(.ant-form-item) {
    margin-bottom: 8px;
  }
  :deep(.form-item-container .editor-container) {
    margin: 2px 0px;
    padding: 4px;
  }
  :deep(.editor) {
    max-height: 88px;
    overflow-y: auto;
  }
}
</style>
