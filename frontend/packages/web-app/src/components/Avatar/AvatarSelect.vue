<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import { ref } from 'vue'

import { COMPONENT_AVATAR_LIST } from '@/constants/avatar'

import Avatar from './Avatar.vue'
import AvatarPicker from './AvatarPicker.vue'

const value = defineModel('value', { type: String, required: true })

const { t } = useTranslation()
const open = ref<boolean>(false)

function showModal() {
  open.value = true
}

function handleOk() {
  open.value = false
}
</script>

<template>
  <Avatar :icon="value" class="cursor-pointer" @click="showModal" />

  <a-modal
    v-model:open="open"
    :title="t('components.changeAvatar')"
    :width="453"
    @ok="handleOk"
  >
    <div class="flex gap-5">
      <Avatar size="xlarge" :icon="value" />
      <a-form layout="vertical" class="flex-1">
        <a-form-item :label="t('components.avatarIcon')">
          <AvatarPicker v-model:value="value" :list="COMPONENT_AVATAR_LIST" />
        </a-form-item>
      </a-form>
    </div>
  </a-modal>
</template>
