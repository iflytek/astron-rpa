<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { computed } from 'vue'

import { ProcessModal } from '@/views/Arrange/components/process'
import { AI_BILLING_RULE_URL, WINDOW_NAME } from '@/constants'
import { utilsManager, windowManager } from '@/platform'
import { baseUrl } from '@/utils/env'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'

import AtomConfig from './AtomConfig.vue'
import {
  getLimitLengthTip,
  useFormItemLimitLength,
  useFormItemRequired,
} from './hooks/useFormItemSort'

const { atomFormItem } = defineProps<{
  atomFormItem: RPA.AtomDisplayItem
  disabled?: boolean
  hideRequiredTip?: boolean // 是否隐藏必填提示
}>()

const flowStore = useFlowStore()
const processStore = useProcessStore()

const isCuaInstructionField = computed(() => {
  return flowStore.activeAtom?.key?.startsWith('ComputerUse.') && atomFormItem.key === 'instruction'
})

// 模板按钮仅在「自定义AI操作屏幕」原子能力中显示
const showTemplateButton = computed(() => {
  return isCuaInstructionField.value && flowStore.activeAtom?.key === 'ComputerUse.custom_action_screen'
})

const currentInstruction = computed(() => {
  const value = atomFormItem.value
  if (Array.isArray(value)) {
    return value[0]?.value ?? ''
  }

  return typeof value === 'string' ? value : ''
})

const cuaInstructionTemplates = [
  { key: 'general', label: '通用模板', text: '请根据当前屏幕完成用户目标：{{目标}}。需要先观察页面再执行，必要时先询问我确认。' },
  { key: 'extract', label: '提取屏幕数据', text: '请从当前屏幕提取以下信息：{{字段列表}}。要求逐条列出，并保持原文。' },
  { key: 'fill', label: '填写表单', text: '请根据提供的信息填写表单：{{字段与值}}。填写前先确认字段是否匹配。' },
  { key: 'captcha', label: '处理验证码', text: '如果页面出现验证码，请提示我输入或确认；不要自动猜测。' },
  { key: 'click', label: '单击', text: '请在当前屏幕上单击：{{目标元素}}。如果有多个相似项，先高亮并让我确认。' },
  { key: 'screen_condition', label: '屏幕条件判断', text: '判断当前屏幕是否满足条件：{{条件描述}}。满足则继续执行，不满足则停止或提示。' },
]

function applyInstructionTemplate(value: string) {
  if (!flowStore.activeAtom?.id) {
    return
  }

  const source = atomFormItem.value
  const nextValue = Array.isArray(source) && source.length > 0
    ? source.map((item, index) => (index === 0 ? { ...item, value } : item))
    : [{ type: 'str', value }]

  flowStore.setFormItemValue('instruction', nextValue, flowStore.activeAtom.id)
}

function handleTemplateSelect({ key }: { key: string | number }) {
  const template = cuaInstructionTemplates.find(item => item.key === String(key))
  if (!template) return
  applyInstructionTemplate(template.text)
}

async function openCuaDebugModal() {
  if (!flowStore.activeAtom?.id) {
    return
  }

  const state = encodeURIComponent(JSON.stringify({
    atomId: flowStore.activeAtom.id,
    atomSnapshot: flowStore.activeAtom,
    currentLine: flowStore.simpleFlowUIData.findIndex(item => item.id === flowStore.activeAtom?.id) + 1,
    initialInstruction: currentInstruction.value,
    projectId: processStore.project.id,
    processId: processStore.activeProcessId,
    project: processStore.project,
  }))

  windowManager.closeWindow(WINDOW_NAME.CUA_DEBUG)

  await windowManager.createWindow({
    url: `${baseUrl}/cuadebug.html?ts=${Date.now()}&state=${state}`,
    title: 'CUA Debug',
    label: WINDOW_NAME.CUA_DEBUG,
    alwaysOnTop: false,
    position: 'right_center',
    offset: 40,
    width: 360,
    height: 520,
    resizable: false,
    decorations: false,
    fileDropEnabled: false,
    maximizable: false,
    transparent: false,
  }, () => {
    windowManager.showWindow()
  })

  windowManager.hideWindow()
}

// 是否展示 label
const showLabel = computed(() => {
  return atomFormItem.formType?.type !== 'CHECKBOX'
})
</script>

<template>
  <div class="form-container">
    <div v-if="isCuaInstructionField" class="cua-debug-tip">
      <rpa-icon name="info" size="16" class="cua-debug-tip-icon" />
      <div class="cua-debug-hint-content">
        <span class="cua-debug-hint">AI可能误判，运行将消耗增值服务积分，优先消耗赠送额度。</span>
        <a
          class="cua-more-btn"
          href="javascript:void(0)"
          @click.prevent="utilsManager.openInBrowser(AI_BILLING_RULE_URL)"
        >
          查看更多
        </a>
      </div>
    </div>
    <label
      v-if="showLabel"
      class="form-container-label flex items-center gap-1 text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]"
    >
      <span v-if="atomFormItem.required" class="text-error">*</span>
      <span
        v-if="atomFormItem.title"
        class="text-xs leading-[22px] text-[#000000]/[.65] dark:text-[#FFFFFF]/[.65]"
      >
        {{ atomFormItem.title }}
      </span>
      <span v-if="atomFormItem.subTitle" class="text-[10px] leading-4">
        {{ atomFormItem.subTitle }}
      </span>
      <a-tooltip v-if="atomFormItem.tip" :title="atomFormItem.tip">
        <rpa-hint-icon name="atom-form-tip" width="16px" height="16px" />
      </a-tooltip>
      <span
        v-if="atomFormItem.title === $t('common.selectPythonModule')"
        class="text-xs text-primary ml-auto cursor-pointer"
        @click="NiceModal.show(ProcessModal, { type: 'module' })"
      >
        {{ $t('common.createPythonScript') }}
      </span>
    </label>
    <div class="form-config-wrap mt-2">
      <AtomConfig :form-item="atomFormItem" />
      <div v-if="isCuaInstructionField" class="cua-debug-trigger-row">
        <article
          v-if="useFormItemRequired(atomFormItem)"
          class="form-container-context-required cua-required-inline"
        >
          {{ $t('common.fieldIsRequired', { field: atomFormItem.title }) }}
        </article>
        <div class="cua-debug-actions">
          <a-dropdown v-if="showTemplateButton" :trigger="['hover']">
            <template #overlay>
              <a-menu @click="handleTemplateSelect">
                <a-menu-item v-for="item in cuaInstructionTemplates" :key="item.key">
                  {{ item.label }}
                </a-menu-item>
              </a-menu>
            </template>
            <a-button size="small" class="cua-template-trigger">
              <template #icon>
                <rpa-icon name="component-manage" size="12" />
              </template>
              模板
            </a-button>
          </a-dropdown>
        <a-tooltip title="在浮窗中调试">
          <a-button
            size="small"
            class="cua-debug-trigger"
            @click="openCuaDebugModal"
          >
            <template #icon>
              <rpa-icon name="bottom-pick-menu-create" size="14" />
            </template>
          </a-button>
        </a-tooltip>
        </div>
      </div>
    </div>
    <article
      v-if="atomFormItem.customizeTip"
      class="form-container-context-required"
    >
      {{ atomFormItem.customizeTip }}
    </article>
    <article
      v-if="!useFormItemLimitLength(atomFormItem)"
      class="form-container-context-required"
    >
      {{ atomFormItem.title }}{{ $t('common.length') }}{{ getLimitLengthTip(atomFormItem.limitLength) || $t('common.exceedLimit') }}
    </article>
  </div>
</template>

<style lang="scss" scoped>
.form-container {
  & + & {
    margin-top: 12px;
  }

  .cua-debug-trigger-row {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 8px;
  }

  .cua-debug-tip {
    display: flex;
    align-items: flex-start;
    gap: 8px;
  }

  .cua-debug-tip-icon {
    color: #eb6e49;
    flex-shrink: 0;
  }

  .cua-debug-hint-content {
    flex: 1;
    min-width: 0;
  }

  .cua-debug-hint {
    display: inline;
    flex: 1;
    min-width: 0;
    color: #eb6e49;
  }

  .cua-more-btn {
    float: right;
    flex-shrink: 0;
    padding: 0 10px;
    font-size: 12px;
    line-height: 1.4;
    height: 18px;
    display: inline-flex;
    align-items: center;
    color: #fff;
    background: #eb6e49;
    border-radius: 999px;
    text-decoration: none;
    white-space: nowrap;
    transition: opacity 0.2s;

    &:hover {
      opacity: 0.9;
    }
  }

  .cua-debug-actions {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-left: auto;
  }

  .cua-required-inline {
    margin: 0;
    margin-right: auto;
  }

  .cua-template-trigger {
    height: 28px;
    padding: 0 10px;
    font-size: 12px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08);
  }

  .cua-debug-trigger {
    width: 30px;
    height: 28px;
    padding: 0;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08);
  }

  .form-container-context-required {
    color: $color-error;
    margin: 4px 0px;
    text-align: left;
  }
}

:deep(.atom-options_item) {
  margin: 0 !important;
  padding: 4px 0 !important;
}
</style>
