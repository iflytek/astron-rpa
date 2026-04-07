<script setup lang="ts">
import { computed } from 'vue'

import { useProcessSelectOptions } from '../hooks'

interface Props {
  desc?: string | number
  itemData: RPA.AtomDisplayItem
  id?: string
  canEdit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  desc: '',
  id: '',
  canEdit: true,
})

// 将菜单项转换为计算属性，提高性能
const menuItems = computed(() => {
  const options = useProcessSelectOptions(props.itemData)
  return options?.map(i => ({ key: i.value, label: i.label })) ?? []
})

const isEmpty = computed(() => menuItems.value.length === 0)

// TODO: 更新表单值
function handleClick(val: string) {
  // 更新 itemData 的值（因为 itemData 是响应式对象引用）
  props.itemData.value = val
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
