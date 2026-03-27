<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import MarkdownIt from 'markdown-it'

const props = defineProps<{
  content: string
  tone?: 'user' | 'assistant'
}>()

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  typographer: true,
})

// 自定义链接渲染，在新标签页打开
const defaultRender = md.renderer.rules.link_open || function (tokens, idx, options, _env, self) {
  return self.renderToken(tokens, idx, options)
}

md.renderer.rules.link_open = function (tokens, idx, options, env, self) {
  const aIndex = tokens[idx].attrIndex('target')
  if (aIndex < 0) {
    tokens[idx].attrPush(['target', '_blank'])
    tokens[idx].attrPush(['rel', 'noopener noreferrer'])
  }
  return defaultRender(tokens, idx, options, env, self)
}

const renderedHtml = computed(() => {
  const normalized = props.content.trim()
  if (!normalized) return ''
  return md.render(normalized)
})

const containerRef = ref<HTMLDivElement>()

onMounted(() => {
  // 为代码块添加复制按钮
  if (!containerRef.value) return

  const codeBlocks = containerRef.value.querySelectorAll('pre code')
  codeBlocks.forEach((block) => {
    const pre = block.parentElement
    if (!pre || pre.querySelector('.code-copy-btn')) return

    const button = document.createElement('button')
    button.className = 'code-copy-btn'
    button.textContent = '复制'
    button.onclick = async () => {
      const code = block.textContent || ''
      try {
        await navigator.clipboard.writeText(code)
        button.textContent = '已复制'
        setTimeout(() => {
          button.textContent = '复制'
        }, 1400)
      } catch {
        button.textContent = '复制失败'
        setTimeout(() => {
          button.textContent = '复制'
        }, 1400)
      }
    }

    const wrapper = document.createElement('div')
    wrapper.className = 'code-block-wrapper'
    pre.parentNode?.insertBefore(wrapper, pre)
    wrapper.appendChild(pre)
    wrapper.insertBefore(button, pre)
  })
})
</script>

<template>
  <div
    ref="containerRef"
    class="markdown-message"
    :class="tone ? `is-${tone}` : ''"
    v-html="renderedHtml"
  />
</template>

<style scoped>
.markdown-message {
  font-size: 13px;
  line-height: 1.6;
  color: #343A52;
}

.markdown-message.is-user {
  color: #343A52;
}

.markdown-message.is-assistant {
  color: #2F374A;
}

/* 段落 */
.markdown-message :deep(p) {
  margin: 0 0 0.75em 0;
}

.markdown-message :deep(p:last-child) {
  margin-bottom: 0;
}

/* 标题 */
.markdown-message :deep(h1),
.markdown-message :deep(h2),
.markdown-message :deep(h3),
.markdown-message :deep(h4),
.markdown-message :deep(h5),
.markdown-message :deep(h6) {
  margin: 1em 0 0.5em 0;
  font-weight: 600;
  line-height: 1.3;
}

.markdown-message :deep(h1) { font-size: 1.5em; }
.markdown-message :deep(h2) { font-size: 1.3em; }
.markdown-message :deep(h3) { font-size: 1.15em; }

/* 列表 */
.markdown-message :deep(ul),
.markdown-message :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.markdown-message :deep(li) {
  margin: 0.25em 0;
}

/* 行内代码 */
.markdown-message :deep(code) {
  background: rgba(0, 0, 0, 0.06);
  padding: 0.15em 0.4em;
  border-radius: 4px;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  font-size: 0.9em;
}

/* 代码块 */
.markdown-message :deep(.code-block-wrapper) {
  position: relative;
  margin: 0.75em 0;
}

.markdown-message :deep(.code-copy-btn) {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 10px;
  font-size: 11px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  cursor: pointer;
  color: #5a5a5a;
  transition: all 0.15s;
  z-index: 1;
}

.markdown-message :deep(.code-copy-btn:hover) {
  background: white;
  border-color: rgba(0, 0, 0, 0.15);
}

.markdown-message :deep(pre) {
  background: #f6f8fa;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0;
}

.markdown-message :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 0.85em;
  line-height: 1.5;
  display: block;
}

/* 引用 */
.markdown-message :deep(blockquote) {
  margin: 0.75em 0;
  padding-left: 1em;
  border-left: 3px solid rgba(0, 0, 0, 0.15);
  color: rgba(0, 0, 0, 0.65);
}

/* 链接 */
.markdown-message :deep(a) {
  color: #726FFF;
  text-decoration: none;
}

.markdown-message :deep(a:hover) {
  text-decoration: underline;
}

/* 表格 */
.markdown-message :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.75em 0;
  font-size: 0.95em;
}

.markdown-message :deep(th),
.markdown-message :deep(td) {
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 6px 10px;
  text-align: left;
}

.markdown-message :deep(th) {
  background: rgba(0, 0, 0, 0.03);
  font-weight: 600;
}

/* 分隔线 */
.markdown-message :deep(hr) {
  border: none;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  margin: 1.5em 0;
}

/* 图片 */
.markdown-message :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  margin: 0.5em 0;
}
</style>
