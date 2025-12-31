<script setup lang="ts">
import { Icon } from '@rpa/components'
import StarterKit from '@tiptap/starter-kit'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import { storeToRefs } from 'pinia'
import { computed, h, nextTick, ref, watch } from 'vue'

import { useAppConfigStore } from '@/stores/useAppConfig'

import type { DocNode } from '../../types'

import { DescriptionNode, ElementNode } from './extensions/CustomNodes'

const props = defineProps<{
  loading?: boolean
  disabled?: boolean
  optimizeLoading?: boolean
}>()

const emit = defineEmits<{
  (evt: 'change', e)
  (evt: 'submit', e)
  (evt: 'optimize', e)
}>()

const model = defineModel('value')
const editorContentRef = ref<InstanceType<typeof EditorContent>>()
const { colorTheme } = storeToRefs(useAppConfigStore())

function isValidDocNode(text: string): boolean {
  try {
    const parsed = JSON.parse(text)
    return parsed && parsed.type === 'doc' && Array.isArray(parsed.content)
  }
  catch {
    return false
  }
}

// 检测是否有未完成的 elementNode（elementId 为空）
function checkHasIncompleteElementNode(editorInstance: any) {
  if (!editorInstance) {
    return false
  }

  const doc = editorInstance.getJSON()
  let hasIncomplete = false

  // 递归遍历文档节点
  function traverseNode(node: any) {
    if (node.type === 'elementNode') {
      if (!node.attrs?.elementId) {
        hasIncomplete = true
        return
      }
    }

    if (node.content && Array.isArray(node.content)) {
      for (const child of node.content) {
        traverseNode(child)
        if (hasIncomplete) {
          return
        }
      }
    }
  }

  traverseNode(doc)
  return hasIncomplete
}

const editor = useEditor({
  content: model.value,
  extensions: [StarterKit, ElementNode, DescriptionNode],
  coreExtensionOptions: {
    clipboardTextSerializer: {
      blockSeparator: '\n',
    },
  },
  // autofocus: true,
  onUpdate: () => {
    // HTML
    // model.value = editor.value.getHTML()

    // JSON
    model.value = editor.value.getJSON()

    emit('change', { target: { value: model.value } })

    // 如果光标位置不在视口内，则滚动到光标位置
    nextTick(() => {
      scrollToCursorIfNeeded()
    })
  },
  editorProps: {
    handleKeyDown: (view, event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()

        if (!isSubmitDisabled.value) {
          handleSubmit()
        }

        return true
      }
      return false
    },
    handlePaste: (view, event) => {
      const clipboardData = event.clipboardData
      if (!clipboardData) {
        return false
      }

      const text = clipboardData.getData('text/plain')
      if (!text) {
        return false
      }

      // 检测是否是有效的 JSON docNode
      if (isValidDocNode(text)) {
        try {
          const docNode = JSON.parse(text) as DocNode
          model.value = docNode
          // 阻止默认粘贴行为
          event.preventDefault()
          return true
        }
        catch (error) {
          console.log(error)
          return false
        }
      }

      return false
    },
  },
})

watch(model, (value) => {
  // HTML
  // const isSame = editor.value.getHTML() === value

  // JSON
  const isSame = JSON.stringify(editor.value.getJSON()) === JSON.stringify(value)

  if (isSame) {
    return
  }

  editor.value.commands.setContent(value)
})

const isEmpty = computed(() => {
  if (!editor.value) {
    return true
  }
  return !editor.value.getText().trim()
})

const hasIncompleteElementNode = computed(() => {
  return checkHasIncompleteElementNode(editor.value)
})

const submitTooltip = computed(() => {
  if (hasIncompleteElementNode.value) {
    return '请先完成元素拾取'
  }
  return '发送'
})

const isSubmitDisabled = computed(() => {
  return props.disabled || props.loading || isEmpty.value || hasIncompleteElementNode.value
})

function focus() {
  editor.value.commands.focus('end')
}

function blur() {
  editor.value.commands.blur()
}

function createElementNode() {
  (editor.value.commands as any).insertElementNode()
}

function setContent(content: any) {
  if (!editor.value) {
    return
  }

  editor.value.commands.setContent(content)
  model.value = editor.value.getJSON()
}

// 如果光标位置不在视口内，则滚动到光标位置
function scrollToCursorIfNeeded() {
  if (!editor.value || !editorContentRef.value?.$el) {
    return
  }

  const scrollContainer = editorContentRef.value.$el as HTMLElement
  const { selection } = editor.value.view.state
  const coords = editor.value.view.coordsAtPos(selection.$anchor.pos)
  const containerRect = scrollContainer.getBoundingClientRect()

  // 检查光标是否在视口内
  const isVisible = coords.top >= containerRect.top && coords.top <= containerRect.bottom

  if (!isVisible) {
    requestAnimationFrame(() => {
      // 计算滚动位置：光标相对于容器的位置 + 当前滚动位置
      const relativeTop = coords.top - containerRect.top + scrollContainer.scrollTop
      scrollContainer.scrollTop = relativeTop - containerRect.height / 2 // 滚动到中间位置
    })
  }
}

function handleSubmit() {
  if (isSubmitDisabled.value) {
    return
  }
  emit('submit', model.value)
  model.value = ''
}

function handleOptimizeQuestion() {
  if (props.optimizeLoading || props.disabled || isEmpty.value) {
    return
  }
  emit('optimize', model.value)
}

defineExpose({
  editor,
  focus,
  blur,
  setContent,
})
</script>

<template>
  <div class="editor-container border border-[#000000]/[.1] dark:border-[#FFFFFF]/[.16] rounded-xl" :class="[colorTheme]">
    <EditorContent ref="editorContentRef" :editor="editor" class="flex-1 min-h-[44px] max-h-[132px] overflow-auto" />
    <div class="flex justify-between">
      <section class="flex items-center gap-2">
        <a-button
          class="flex items-center gap-1 px-2 rounded-lg"
          size="middle"
          :icon="h(Icon, { name: 'bottom-menu-ele-manage', size: '16' })"
          @click="createElementNode"
        >
          元素拾取
        </a-button>
        <a-button
          class="flex items-center gap-1 px-2 rounded-lg"
          size="middle"
          :icon="h(Icon, { name: 'ai-edit', size: '16' })"
          :loading="optimizeLoading"
          :disabled="optimizeLoading || disabled || isEmpty"
          @click="handleOptimizeQuestion"
        >
          优化提问
        </a-button>
      </section>

      <section class="flex items-center">
        <a-tooltip :title="submitTooltip">
          <rpa-hint-icon
            name="round-arrow-up"
            size="32"
            class="transition-colors"
            :class="isSubmitDisabled ? 'text-[#F3F3F7] dark:text-[#FFFFFF]/[.08]' : 'text-primary'"
            :disabled="isSubmitDisabled"
            @click="handleSubmit"
          />
        </a-tooltip>
      </section>
    </div>

    <!-- 优化提问蒙版 -->
    <div v-if="optimizeLoading" class="editor-mask" />
  </div>
</template>

<style lang="scss" scoped>
.editor-container {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 16px;
  box-shadow:
    0 1px 2px 0 rgba(0, 0, 0, 0.03),
    0 1px 6px -1px rgba(0, 0, 0, 0.02),
    0 2px 4px 0 rgba(0, 0, 0, 0.02);
}

.editor-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  z-index: 10;
  cursor: not-allowed;
  pointer-events: all;
}

.dark .editor-mask {
  background-color: rgba(0, 0, 0, 0.4);
}
</style>
