<script lang="ts" setup>
import { computed, ref } from 'vue'

import { COMPONENT_KEY_PREFIX, updateFlowNodesComponent } from '@/utils/customComponent'

import { installComponent, removeComponent, updateComponent } from '@/api/robot'
import { createComponentAbility } from '@/views/Arrange/utils/generateData'

const props = defineProps<{ data: RPA.ComponentManageItem, robotId: string }>()
const emit = defineEmits(['refresh'])

const isInstalled = computed(() => props.data.blocked === 0)
const isLatest = computed(() => props.data.isLatest === 1)
const loading = ref(false)

async function execute<T>(func: () => Promise<T>) {
  loading.value = true

  try {
    const res = await func()
    emit('refresh', res)
  }
  finally {
    loading.value = false
  }
}

function handleInstall() {
  execute(() =>
    installComponent({
      robotId: props.robotId,
      componentId: props.data.componentId,
    }),
  )
}

function handleRemove() {
  execute(() =>
    removeComponent({
      robotId: props.robotId,
      componentId: props.data.componentId,
    }),
  )
}

function handleUpdate() {
  execute(async () => {
    await updateComponent({
      robotId: props.robotId,
      componentId: props.data.componentId,
      componentVersion: props.data.latestVersion,
    })
    const node = await createComponentAbility(`${COMPONENT_KEY_PREFIX}.${props.data.componentId}`, props.data.latestVersion)
    await updateFlowNodesComponent(props.data.componentId, node)
  })
}
</script>

<template>
  <!-- 组件卡片 -->
  <div class="border border-border rounded-[12px] p-[18px]">
    <!-- 卡片头部 -->
    <div class="flex items-center gap-[6px] mb-[6px]">
      <rpa-icon :name="data.icon" size="20" />
      <span class="font-medium text-[16px] leading-[22px]">
        {{ data.name }}
      </span>
      <span
        class="px-2 rounded"
        :class="[
          data.isLatest === 1
            ? 'bg-[#726FFF]/[.1] text-primary'
            : 'bg-[#000000]/[.06] dark:bg-[#FFFFFF]/[.12]',
        ]"
      >
        v{{ data.version }}
      </span>
    </div>

    <!-- 卡片描述 -->

    <div class="leading-5 h-10 whitespace-pre-line line-clamp-2 truncate mb-3">
      {{ data?.introduction || '--' }}
    </div>

    <!-- 卡片操作按钮 -->
    <div class="flex space-x-2">
      <a-button v-if="!isInstalled" class="flex-1" :disabled="loading" @click="handleInstall">
        安装
      </a-button>

      <template v-else>
        <a-button class="flex-1" :disabled="loading" @click="handleRemove">
          移除
        </a-button>

        <a-button v-if="isLatest" class="flex-[2]" disabled>
          最新版本
        </a-button>
        <a-button v-else type="primary" class="flex-[2]" :disabled="loading" @click="handleUpdate">
          更新：{{ data.latestVersion }}
        </a-button>
      </template>
    </div>
  </div>
</template>
