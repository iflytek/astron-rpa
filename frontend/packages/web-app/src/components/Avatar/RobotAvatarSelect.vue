<script lang="ts" setup>
import { useTranslation } from 'i18next-vue'
import { difference, sample } from 'lodash-es'
import { computed, ref, watch } from 'vue'

import { COLOR_LIST, ROBOT_DEFAULT_ICON } from '@/constants/avatar'

import Avatar from './Avatar.vue'
import Default from './Default.vue'
import Icon from './Icon.vue'

defineProps<{ robotName: string }>()

const open = ref<boolean>(false)
const { t } = useTranslation()
const iconRef = ref<InstanceType<typeof Icon> | null>(null)

const tabs = computed(() => [
  {
    label: t('common.default'),
    value: 'default',
    component: Default,
  },
  {
    label: t('common.icon'),
    value: 'icon',
    component: Icon,
  },
])

const activeTab = ref<string>(tabs.value[0].value)

const color = defineModel<string>('color', { type: String })
const icon = defineModel<string>('icon', { type: String })
const initialIcon = icon.value
const initialColor = color.value

function showModal() {
  open.value = true
}

function closeModal() {
  open.value = false
}

function handleCancel() {
  icon.value = initialIcon
  color.value = initialColor
  closeModal()
}

function handleOk() {
  closeModal()
}

function handleRandom() {
  if (activeTab.value === 'icon') {
    const avatarList = iconRef.value?.currentAvatarList
    if (avatarList && avatarList.length > 0) {
      const availableIcons = difference(
        avatarList.map(item => item.icon),
        icon.value ? [icon.value] : [],
      )
      if (availableIcons.length > 0) {
        icon.value = sample(availableIcons) || avatarList[0].icon
      }
      else {
        icon.value = avatarList[0].icon
      }
    }
  }
  else {
    color.value = sample(difference(COLOR_LIST, [color.value]))
  }
}

function handleChange(tab: string) {
  if (tab === 'icon') {
    icon.value = initialIcon || ROBOT_DEFAULT_ICON
  }
  else {
    icon.value = ''
  }
}

watch(open, () => {
  if (open.value) {
    activeTab.value = icon.value ? 'icon' : 'default'
  }
})
</script>

<template>
  <Avatar :robot-name="robotName" :icon="icon" :color="color" size="large" @click="showModal" />

  <a-modal
    :open="open"
    destroy-on-close
    centered
    :width="453"
    :title="$t('common.changeAvatar')"
    :keyboard="false"
    :mask-closable="false"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <div class="flex gap-[20px] my-5">
      <div class="flex flex-col gap-3">
        <Avatar :robot-name="robotName" :icon="icon" :color="color" size="xlarge" />
        <a-button class="flex items-center gap-1" @click="handleRandom">
          <rpa-icon name="random" />{{ $t('common.random') }}
        </a-button>
      </div>
      <div class="flex flex-1 flex-col gap-4">
        <div class="w-2/3">
          <a-segmented v-model:value="activeTab" block :options="tabs" @change="handleChange" />
        </div>
        <Default
          v-if="activeTab === 'default'"
          v-model:color="color"
          v-model:icon="icon"
        />
        <Icon
          v-else
          ref="iconRef"
          v-model:color="color"
          v-model:icon="icon"
        />
      </div>
    </div>
  </a-modal>
</template>
