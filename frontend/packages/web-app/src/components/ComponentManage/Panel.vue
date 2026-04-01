<script lang="ts" setup>
import { computed, h, ref } from 'vue'
import { Input, message } from 'ant-design-vue'

import { COMPONENT_KEY_PREFIX, updateFlowNodesComponent } from '@/utils/customComponent'
import GlobalModal from '@/components/GlobalModal/index.ts'

import { installComponent, installMarketComponent, removeComponent, removeMarketComponent, updateComponent } from '@/api/robot'
import { deleteApp } from '@/api/market'
import { createComponentAbility } from '@/views/Arrange/utils/generateData'
import { useCommonOperate } from '@/views/Home/pages/hooks/useCommonOperate'

const props = defineProps<{
  data: RPA.ComponentManageItem
  robotId: string
  robotVersion: number
}>()
const emit = defineEmits(['refresh'])

const isInstalled = computed(() => props.data.blocked === 0)
const isLatest = computed(() => props.data.isLatest === 1)
const canOperate = computed(() => props.data.allowOperate === 1) // 是否允许操作（下架）
const loading = ref(false)
const { handleDeleteConfirm } = useCommonOperate()

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

function doInstallMarketComponent(appName: string) {
  return execute(() =>
    installMarketComponent({
      marketId: props.data.marketId!,
      appId: props.data.appId!, // 使用 appId 而不是 componentId
      appName,
      version: props.data.latestVersion || props.data.version,
    }),
  )
}

async function handleInstall() {
  if (props.data.marketId) {
    // 团队市场组件
    try {
      await doInstallMarketComponent(props.data.name)
    }
    catch (err: any) {
      const { code } = err
      // 错误码 600000 表示存在同名组件
      if ([600000, '600000'].includes(code)) {
        const confirmAppName = ref(props.data.name)
        const modal = GlobalModal.warning({
          title: '安装组件',
          content: () => {
            return h('div', [
              h('p', '存在同名自定义组件，请修改名称'),
              h('span', '名称：'),
              h(Input, {
                defaultValue: props.data.name,
                onChange: (e: any) => {
                  confirmAppName.value = e.target.value
                  if (!confirmAppName.value) {
                    message.error('请输入名称')
                  }
                },
                style: 'width: 200px; margin-left: 8px',
              }),
            ])
          },
          async onOk() {
            if (!confirmAppName.value) {
              message.error('请输入名称')
              return false
            }
            try {
              await doInstallMarketComponent(confirmAppName.value)
              modal.destroy()
            }
            catch (err) {
              return false
            }
          },
          maskClosable: true,
          centered: true,
          keyboard: false,
        })
      } else {
        message.error(err.message || err.msg || '安装失败')
      }
    }
  } else {
    // 自建组件
    execute(() =>
      installComponent({
        robotId: props.robotId,
        componentId: props.data.componentId,
      }),
    )
  }
}

// 移除组件
function handleRemove() {
  if (props.data.marketId) {
    // 团队市场组件
    execute(() =>
      removeMarketComponent({
        componentId: props.data.componentId,
      }),
    )
  } else {
    // 自建组件
    execute(() =>
      removeComponent({
        robotId: props.robotId,
        robotVersion: props.robotVersion,
        componentId: props.data.componentId,
      }),
    )
  }
}

// 下架组件
async function handleTakeDown() {
  const confirm = await handleDeleteConfirm(`将要下架：${props.data.name}，下架后将无法恢复，是否仍要下架？`)
  if (!confirm) {
    return
  }
  execute(() =>
    deleteApp({
      appId: props.data.appId!, // 使用 appId 而不是 componentId
      marketId: props.data.marketId!,
      appType: 'component',
    }),
  )
}

function handleUpdate() {
  execute(async () => {
    await updateComponent({
      robotId: props.robotId,
      robotVersion: props.robotVersion,
      componentId: props.data.componentId,
      componentVersion: props.data.latestVersion,
    })
    const node = await createComponentAbility(`${COMPONENT_KEY_PREFIX}.${props.data.componentId}`, props.data.latestVersion, 'update')
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
      <a-tooltip :title="data.name">
        <span
          class="font-medium text-[16px] leading-[22px] max-w-[calc(100%-70px)] text-ellipsis whitespace-nowrap overflow-hidden">
          {{ data.name }}
        </span>
      </a-tooltip>
      <span class="px-2 rounded" :class="[
        data.isLatest === 1
          ? 'bg-[#726FFF]/[.1] text-primary'
          : 'bg-[#000000]/[.06] dark:bg-[#FFFFFF]/[.12]',
      ]">
        v{{ data.version }}
      </span>
    </div>

    <!-- 卡片描述 -->

    <a-tooltip :title="data?.introduction">
      <div class="leading-5 h-10 whitespace-pre-line line-clamp-2 truncate mb-3">
        {{ data?.introduction || '--' }}
      </div>
    </a-tooltip>

    <!-- 卡片操作按钮 -->
    <div class="flex space-x-2">
      <a-button v-if="props.data.marketId && canOperate" class="flex-1" :disabled="loading" @click="handleTakeDown">
        下架
      </a-button>
      <template v-if="!isInstalled">
        <a-button class="flex-1" :disabled="loading" @click="handleInstall">
          安装
        </a-button>
      </template>

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
