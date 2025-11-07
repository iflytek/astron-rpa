<script setup lang="ts">
import type { Ref } from 'vue'
import { computed, inject } from 'vue'

import { useFlowStore } from '@/stores/useFlowStore'
import { isConditionalKeys } from '@/views/Arrange/components/atomForm/hooks/useBaseConfig'

interface Props {
  desc?: string
  itemData: RPA.AtomDisplayItem
  id?: string
  canEdit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  desc: '',
  id: '',
  canEdit: true,
})

const isShowFormItem = inject<Ref<boolean>>('showAtomFormItem')
const flowStore = useFlowStore()

// 将菜单项转换为计算属性，提高性能
const menuItems = computed(() => {
  return props.itemData.options?.map(i => ({ key: i.value, label: i.label })) ?? []
})

const isEmpty = computed(() => menuItems.value.length === 0)

function handleClick(val: string) {
  // 更新 itemData 的值（因为 itemData 是响应式对象引用）
  props.itemData.value = val
  // 通过 store 同步更新表单值
  flowStore.setFormItemValue(props.itemData.key, props.itemData.value, props.id)
  // 如果是条件键，切换表单项显示状态
  if (isConditionalKeys(props.itemData.key))
    isShowFormItem.value = !isShowFormItem.value
}
</script>

<template>
  <!-- 下拉选择、单选、切换、复选框 -->
  <a-dropdown :disabled="!props.canEdit || isEmpty">
    <span>{{ isEmpty ? '--' : props.desc }}</span>
    <template #overlay>
      <a-menu
        mode="vertical"
        class="form-type-select-menu"
        :items="menuItems"
        @click="(item) => handleClick(item.key as string)"
      />
    </template>
  </a-dropdown>
</template>

<style lang="scss" scoped>
// 每个菜单项高度约为 32px，5 项共 160px
.form-type-select-menu {
  min-width: 130px;
  max-height: 168px;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>
