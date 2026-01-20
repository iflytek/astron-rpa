<script lang="ts" setup>
import { message } from 'ant-design-vue'
import { throttle } from 'lodash-es'
import { computed, defineAsyncComponent, provide, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { codeToMeta } from '@/api/component'
import { getRootBaseURL } from '@/api/http/env'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunlogStore } from '@/stores/useRunlogStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { debug } from '@/views/Arrange/components/flow/hooks/useFlow'

import AtomForm from '../components/AtomForm.vue'
import { modeOptions } from '../config/constants'
import { usePackageCheck, useSmartComp } from '../hooks'
import { generateComponentForm } from '../utils'
import { useDark } from '@vueuse/core'

const isDark = useDark()
const processStore = useProcessStore()
const flowStore = useFlowStore()
const smartComp = useSmartComp()
const runningStore = useRunningStore()
const runlogStore = useRunlogStore()
const route = useRoute()

// 依赖检查（使用共享的上下文）
const {
  lackPackages,
  installAllPackages,
} = usePackageCheck()

// 获取智能组件插入位置索引
const newIndex = computed(() => {
  const index = route.query?.newIndex
  return index ? Number(index) : undefined
})

provide('smartCompNewIndex', newIndex)

const mode = ref<('visual' | 'code')>('visual') // 可视化/代码模式
const baseUrl = `${getRootBaseURL()}/scheduler`
const CodeEditor = defineAsyncComponent(() => import('@rpa/components').then(m => m.CodeEditor))

const previousCode = ref('')
const currentCode = ref('')

// 判断是否有修改
const isModified = computed(() => {
  return currentCode.value !== previousCode.value
})

// 当编辑的组件或版本切换时，重置 previousCode 和 currentCode
watch(
  () => [smartComp.editingSmartComp.value, smartComp.currentVersionIndex.value],
  () => {
    const code = smartComp.editingSmartComp.value?.smartCode || ''
    previousCode.value = code
    currentCode.value = code
  },
  { immediate: true },
)

function handleCodeUpdate(value: string) {
  currentCode.value = value
}

const buttonConfig = computed(() => {
  if (runningStore.running === 'run' || runningStore.running === 'debug') {
    return {
      icon: 'tools-stop',
      text: '停止',
      clickHandler: handleStop,
    }
  }
  else {
    return {
      icon: 'tools-run',
      text: '运行',
      clickHandler: handleRun,
    }
  }
})

const handleRun = throttle(async () => {
  try {
    // 如果有缺失依赖，自动安装
    if (lackPackages.value.length > 0) {
      try {
        await installAllPackages()
      }
      catch (error) {
        console.error('安装依赖失败:', error)
        return
      }
    }

    await smartComp.saveSmartComp()
    const componentId = flowStore.simpleFlowUIData.find(item => item.key === smartComp.editingSmartComp.value?.key)?.id
    debug([componentId])
  }
  catch (error) {
    console.error('运行失败:', error)
  }
}, 1500, { leading: true, trailing: false })

const handleStop = throttle(() => {
  try {
    if (runningStore.getRunProjectId()) {
      runningStore.stop(runningStore.getRunProjectId())
    }
  }
  catch (error) {
    console.error(error)
  }
}, 1500, { leading: true, trailing: false })

const handleSave = throttle(async () => {
  try {
    if (!smartComp.editingSmartComp.value) {
      return
    }

    const code = currentCode.value

    // 调用 codeToMeta 获取代码元数据
    const compMeta = await codeToMeta({ code }) || {}

    const updatedComp = {
      ...generateComponentForm(compMeta, smartComp.editingSmartComp.value.outputList),
      key: smartComp.editingSmartComp.value.key,
      alias: smartComp.editingSmartComp.value?.alias || compMeta.title,
      version: smartComp.editingSmartComp.value.version,
      smartType: smartComp.editingSmartComp.value.smartType,
      smartCode: code,
      detail: smartComp.editingSmartComp.value.detail,
    }
    smartComp.setEditingSmartComp(updatedComp)

    // 更新 previousCode 为当前保存的代码
    previousCode.value = code

    runlogStore.clearLogs()
    message.success('保存成功')
  }
  catch (error) {
    console.error('保存失败:', error)
    message.error('保存失败')
  }
}, 1500, { leading: true, trailing: false })

const handleReset = throttle(() => {
  // 还原代码到 previousCode
  currentCode.value = previousCode.value
}, 1500, { leading: true, trailing: false })
</script>

<template>
  <div class="flex-1 flex flex-col bg-[#FFFFFF] dark:bg-[#FFFFFF]/[.08] rounded-lg overflow-hidden">
    <div class="flex justify-between px-4 py-[10px]">
      <a-segmented v-model:value="mode" :options="modeOptions as any">
        <template #label="{ payload }">
          <rpa-hint-icon :name="payload.icon" :title="payload.title" class="relative top-[2px]" />
        </template>
      </a-segmented>
      <div class="flex items-center gap-2">
        <template v-if="isModified">
          <rpa-hint-icon
            name="tools-redo"
            enable-hover-bg
            @click="handleReset"
          >
            <template #suffix>
              <span class="ml-1">重置</span>
            </template>
          </rpa-hint-icon>
          <rpa-hint-icon
            name="tools-save"
            enable-hover-bg
            @click="handleSave"
          >
            <template #suffix>
              <span class="ml-1">保存</span>
            </template>
          </rpa-hint-icon>
        </template>
        <rpa-hint-icon
          :name="buttonConfig.icon"
          :disabled="isModified"
          enable-hover-bg
          @click="buttonConfig.clickHandler"
        >
          <template #suffix>
            <span class="ml-1">{{ buttonConfig.text }}</span>
          </template>
        </rpa-hint-icon>
      </div>
    </div>
    <a-divider class="!my-0" />
    <div
      v-if="mode === 'visual'"
      class="flex-1 py-3 px-4 border-dashed border-[#000000]/[.16] dark:border-[#FFFFFF]/[.16] rounded overflow-hidden"
    >
      <AtomForm :atom="smartComp.editingSmartComp.value as any" />
    </div>
    <CodeEditor
      v-else
      :project-id="processStore.project.id"
      :base-url="baseUrl"
      :value="currentCode"
      :is-dark="isDark"
      style="height: calc(100% - 52px); padding-bottom: 16px"
      @update:value="handleCodeUpdate"
    />
  </div>
</template>
