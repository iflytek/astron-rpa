<script setup lang="ts">
import { computed } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'
import type { VisualEditor } from '@/views/Arrange/canvasManager'

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
const processStore = useProcessStore()
const activeTab = computed(() => processStore.canvasManager.activeTab as VisualEditor | null)

const menuItems = computed(() => {
  const options = useProcessSelectOptions(props.itemData)
  return options?.map(i => ({ key: i.value, label: i.label })) ?? []
})

const isEmpty = computed(() => menuItems.value.length === 0)

function handleClick(val: string) {
  props.itemData.value = val

  if (props.id && props.itemData.sourceValue) {
    activeTab.value?.updateFormItemValue(
      props.id,
      props.itemData.sourceValue,
      val,
    )
  }
}
</script>

<template>
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
.form-type-select-menu {
  min-width: 130px;
  max-height: 168px;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>
