<script setup lang="ts">
import { onMounted, provide, ref, watch } from 'vue'

import AtomFormItem from '@/views/Arrange/components/atomForm/AtomFormItem.vue'
import type { VariableTypes } from '@/views/Arrange/types/atomForm'
import { PARAMETER_VAR_TYPE } from '@/views/Arrange/config/atom'
import { useProcessStore } from '@/stores/useProcessStore'
import { convertCommentToInputVariableValue, convertInputVariableValueToComment } from '@/utils/customComponent'
import { getComponentDetail } from '@/api/project'

import DescriptionTooltip from './DescriptionTooltip.vue'

// 限制变量类型为配置参数
provide<VariableTypes>('variableType', PARAMETER_VAR_TYPE)

const processStore = useProcessStore()

const initialValue = processStore.componentComment
  ? convertCommentToInputVariableValue(processStore.componentComment)
  : []

const descriptionForm = ref({
  formType: { type: 'INPUT_VARIABLE' },
  key: 'comment',
  name: 'comment',
  required: false,
  tip: '编辑区便捷描述',
  title: '编辑区便捷描述',
  types: 'Str',
  value: initialValue,
})

async function loadComponentComment() {
  const { project } = processStore
  if (!project?.id || processStore.componentComment) {
    return
  }

  try {
    const info = await getComponentDetail({ componentId: project.id })
    const comment = info?.comment || ''
    if (comment) {
      // 更新 store 和表单
      processStore.componentComment = comment
      const valueArray = convertCommentToInputVariableValue(comment)
      descriptionForm.value.value = valueArray
    }
  } catch (error) {
    console.error('加载组件 comment 失败:', error)
  }
}

// 监听表单变化，同步到 store
watch(() => descriptionForm.value.value, (newValue) => {
  const comment = convertInputVariableValueToComment(newValue as Array<{ type: string; value: string }>)
  processStore.componentComment = comment
}, { deep: true })

onMounted(() => {
  loadComponentComment()
})
</script>

<template>
  <section class="mx-4 mb-5">
    <AtomFormItem
      :atom-form-item="descriptionForm"
      class="text-[12px]"
    >
      <template #tooltip-title>
        <DescriptionTooltip :description-value="descriptionForm.value as Array<{ type: string; value: string }>" />
      </template>
    </AtomFormItem>
  </section>
</template>