<script lang="ts" setup>
import { difference, sample } from 'lodash-es'
import { computed, ref, watch } from 'vue'

import { COLOR_LIST, ROBOT_AVATAR_LIST, ROBOT_DEFAULT_ICON } from '@/constants/avatar'

import Avatar from './Avatar.vue'
import Default from './Default.vue'
import Icon from './Icon.vue'

defineProps<{ robotName: string }>()

const open = ref<boolean>(false)

const tabs = [
  {
    label: '默认',
    value: 'default',
    component: Default,
  },
  {
    label: '图标',
    value: 'icon',
    component: Icon,
  },
]

const activeTab = ref<string>(tabs[0].value)
const activeComp = computed(() => tabs.find(tab => tab.value === activeTab.value).component)

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
  color.value = sample(difference(COLOR_LIST, [color.value]))
  if (activeTab.value === 'icon') {
    icon.value = sample(difference(ROBOT_AVATAR_LIST.map(item => item.icon), [icon.value]))
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
    title="修改头像"
    :keyboard="false"
    :mask-closable="false"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <div class="flex gap-[20px] my-5">
      <div class="flex flex-col gap-3">
        <Avatar :robot-name="robotName" :icon="icon" :color="color" size="xlarge" />
        <a-button class="flex items-center gap-1" @click="handleRandom">
          <rpa-icon name="random" />随机
        </a-button>
      </div>
      <div class="flex flex-1 flex-col gap-4">
        <div class="w-2/3">
          <a-segmented v-model:value="activeTab" block :options="tabs" @change="handleChange" />
        </div>
        <component :is="activeComp" v-model:color="color" v-model:icon="icon" />
      </div>
    </div>
  </a-modal>
</template>
