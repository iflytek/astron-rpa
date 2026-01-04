<script lang="ts" setup>
import { computed, ref } from 'vue'

import { NEW_ROBOT_AVATAR_LIST } from '@/constants/avatar'
import type { AvatarItem } from '@/constants/avatar'

import AvatarPicker from './AvatarPicker.vue'

const icon = defineModel('icon', { type: String, required: true })

const avatarTypeOptions = computed(() => {
  return NEW_ROBOT_AVATAR_LIST.map(item => ({
    value: item.type,
    label: item.typeName,
  }))
})

const selectedAvatarType = ref<string>(NEW_ROBOT_AVATAR_LIST[0]?.type || '')

const currentAvatarList = computed<AvatarItem[]>(() => {
  const typeData = NEW_ROBOT_AVATAR_LIST.find(item => item.type === selectedAvatarType.value)
  if (typeData) {
    return typeData.list.map(iconName => ({ icon: iconName }))
  }

  return []
})

function handleTypeChange() {
  const currentList = currentAvatarList.value
  const iconExists = currentList.some(item => item.icon === icon.value)

  if (!iconExists && currentList.length > 0) {
    icon.value = currentList[0].icon
  }
}

defineExpose({
  currentAvatarList,
})
</script>

<template>
  <a-form layout="vertical" class="flex-1">
    <a-form-item label="" class="flex items-center gap-4">
      <span class="text-[12px] text-text-secondary mr-4">分类</span>
      <a-select
        v-model:value="selectedAvatarType"
        :options="avatarTypeOptions"
        class="!w-[150px] !text-[12px]"
        @change="handleTypeChange"
      />
    </a-form-item>
    <a-form-item :label="$t('common.avatarIcon')" class="max-h-[120px] overflow-y-auto">
      <AvatarPicker v-model:value="icon" :list="currentAvatarList" />
    </a-form-item>
  </a-form>
</template>
