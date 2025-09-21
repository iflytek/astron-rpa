<script lang="ts" setup>
import { useAsyncState } from '@vueuse/core'
import { computed, ref } from 'vue'

import { COMPONENT_KEY_PREFIX, updateFlowNodesComponent } from '@/utils/customComponent'

import { getComponentDetail, removeComponent, updateComponent } from '@/api/robot'
import { createComponentAbility } from '@/views/Arrange/utils/generateData'

const props = defineProps<{ robotId: string, componentId: string }>()
const emit = defineEmits(['refresh'])

const { state, executeImmediate } = useAsyncState(() => getComponentDetail(props), null)

const open = ref(false)
const loading = ref(false)
const isLatest = computed(() => state.value?.isLatest === 1)

function close() {
  open.value = false
}

async function execute<T>(func: () => Promise<T>) {
  loading.value = true

  try {
    const res = await func()
    emit('refresh', res)
    executeImmediate()
    close()
  }
  finally {
    loading.value = false
  }
}

function handleRemove() {
  execute(() =>
    removeComponent({
      robotId: props.robotId,
      componentId: props.componentId,
    }),
  )
}

function handleUpdate() {
  execute(async () => {
    await updateComponent({
      robotId: props.robotId,
      componentId: props.componentId,
      componentVersion: state.value.latestVersion,
    })
    const node = await createComponentAbility(`${COMPONENT_KEY_PREFIX}.${props.componentId}`, state.value.latestVersion)
    await updateFlowNodesComponent(props.componentId, node)
  })
}
</script>

<template>
  <a-popover
    v-model:open="open"
    trigger="click"
    placement="rightTop"
    :arrow="false"
  >
    <template #content>
      <div class="py-2 px-3 w-[296px]">
        <div class="flex justify-between items-center font-medium text-[16px]">
          <span>{{ $t("components.customComponentManage") }}</span>
          <rpa-hint-icon
            enable-hover-bg
            name="close"
            size="16"
            class="!p-0.5"
            icon-class="opacity-[.25]"
            @click="close"
          />
        </div>

        <div class="flex flex-wrap text-[12px] mt-4">
          <div class="flex-1 flex flex-col gap-1">
            <span class="text-text-tertiary dark:text-[#FFFFFF]/[.65]">
              {{ $t("components.componentName") }}
            </span>
            <span>{{ state?.name }}</span>
          </div>
          <div class="flex-1 flex flex-col gap-1">
            <span class="text-text-tertiary dark:text-[#FFFFFF]/[.65]">
              {{ $t("currentVersion") }}
            </span>
            <span>v{{ state?.version }}</span>
          </div>
        </div>

        <div class="mt-4 flex flex-col gap-1 text-[12px]">
          <span class="text-text-tertiary dark:text-[#FFFFFF]/[.65]">
            {{ $t("components.componentDescription") }}
          </span>

          <div class="leading-5 whitespace-pre-line line-clamp-2 truncate">
            {{ state?.introduction || '当前组件暂无简介' }}
          </div>
        </div>

        <div class="mt-4 flex justify-end gap-2">
          <a-button :disabled="loading" @click="handleRemove">
            {{ $t('common.remove') }}
          </a-button>

          <a-button v-if="!isLatest" type="primary" :disabled="loading" @click="handleUpdate">
            {{ $t('common.update') }}：v{{ state?.latestVersion }}
          </a-button>
          <a-button v-else disabled>
            {{ $t('common.latestVersion') }}
          </a-button>
        </div>
      </div>
    </template>

    <slot />
  </a-popover>
</template>
