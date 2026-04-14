<script setup lang="ts">
import { refDebounced } from '@vueuse/core'
import hotkeys from 'hotkeys-js'
import { escapeRegExp, isArray } from 'lodash-es'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef, watch } from 'vue'

import { SCOPE } from '@/constants/shortcuts'
import { useProcessStore } from '@/stores/useProcessStore'
import type { VisualEditor } from '@/views/Arrange/canvasManager'
import SearchWidget from '@/views/Arrange/components/search/SearchWidget.vue'
import { atomScrollIntoView, decodeHtml } from '@/views/Arrange/utils/index'
import { renderAtomRemark } from '@/views/Arrange/components/flow/utils/renderAtomRemark'
import { changeSelectAtoms } from '@/views/Arrange/utils/selectItemByClick'

const SEARCH_HOTKEY = 'Ctrl+F'
const ARROW_UP_KEY = 'up'
const ARROW_DOWN_KEY = 'down'

const showSearch = ref(false)
const activeIndex = ref(0)
const searchKeyword = ref('')
const debouncedSearchKeyword = refDebounced(searchKeyword, 300)
const searchWidget = useTemplateRef('searchWidget')
const processStore = useProcessStore()
const activeTab = computed(() => processStore.canvasManager.activeTab as VisualEditor | null)

// 搜索结果显示
const searchResults = computed(() => {
  if (!showSearch.value || !debouncedSearchKeyword.value)
    return []

  const searchRegex = new RegExp(escapeRegExp(debouncedSearchKeyword.value), 'i')
  const dataWithComments = (activeTab.value?.state.data || []).map((item, index) => {
    const comment = renderAtomRemark(item, activeTab.value?.astParser)
    const commentText = isArray(comment)
      ? comment.map(i => typeof i === 'string' ? i : decodeHtml(i.displayValue)).join('')
      : String(comment || '')
    return { id: item.id, title: item.alias, commentText, item, index }
  })

  return dataWithComments.filter(
    it => searchRegex.test(it.title) || searchRegex.test(it.commentText),
  )
})

// 当前激活的搜索结果
const activeSearchAtom = computed(() => {
  return searchResults.value[activeIndex.value]
})

// 展开包含当前搜索结果的折叠组
function expandContainingGroups(atomIndex: number) {
  const tab = activeTab.value
  const atomId = tab?.state.data?.[atomIndex]?.id
  if (!tab || !atomId) {
    return
  }

  let current = tab.astParser.getNode(atomId)?.parent
  while (current && current.type !== 'root') {
    if (current.raw?.id && current.raw?.isOpen === false) {
      tab.toggleFold(current.raw.id)
    }
    current = current.parent
  }
}

// 处理搜索结果切换
function handleSearchResultChange(atomId: string | undefined) {
  if (!atomId) {
    activeIndex.value = 0
    return
  }

  const canvas = document.querySelector<HTMLElement>('.postTask-content-canvas')
  if (canvas) {
    canvas.scrollTop = 0
  }
  changeSelectAtoms(atomId, null, false)
  expandContainingGroups(activeSearchAtom.value.index)
  nextTick(() => atomScrollIntoView(atomId))
}

// 搜索控件操作
function showSearchWidget() {
  showSearch.value = true
  // 绑定上下键快捷键
  hotkeys(ARROW_UP_KEY, SCOPE, handleArrowUp)
  hotkeys(ARROW_DOWN_KEY, SCOPE, handleArrowDown)
  nextTick(() => searchWidget.value?.focus())
}

function closeSearchWidget() {
  showSearch.value = false
  searchKeyword.value = ''
  activeIndex.value = 0
  // 取消绑定上下键快捷键
  hotkeys.unbind(ARROW_UP_KEY, SCOPE)
  hotkeys.unbind(ARROW_DOWN_KEY, SCOPE)
}

function next() {
  if (searchResults.value.length === 0)
    return
  const total = searchResults.value.length
  activeIndex.value = (activeIndex.value + 1) % total
}

function previous() {
  if (searchResults.value.length === 0)
    return
  const total = searchResults.value.length
  activeIndex.value = activeIndex.value === 0 ? total - 1 : activeIndex.value - 1
}

// 上下键处理函数
function handleArrowUp() {
  previous()
}

function handleArrowDown() {
  next()
}

// 监听搜索结果变化
watch(
  () => activeSearchAtom.value?.id,
  handleSearchResultChange,
)

// 快捷键绑定
onMounted(() => {
  hotkeys(SEARCH_HOTKEY, SCOPE, showSearchWidget)
})

onBeforeUnmount(() => {
  hotkeys.unbind(SEARCH_HOTKEY, SCOPE)
  hotkeys.unbind(ARROW_UP_KEY, SCOPE)
  hotkeys.unbind(ARROW_DOWN_KEY, SCOPE)
})
</script>

<template>
  <div class="search">
    <Transition name="search-fade">
      <SearchWidget
        v-if="showSearch"
        ref="searchWidget"
        v-model:value="searchKeyword"
        class="search-widget"
        :active="activeIndex + 1"
        :total="searchResults.length"
        @next="next"
        @previous="previous"
        @close="closeSearchWidget"
      />
    </Transition>
  </div>
</template>

<style scoped lang="scss">
.search {
  width: 100%;
  position: relative;
  z-index: 1;

  .search-widget {
    position: absolute;
    right: 10px;
    top: 20px;
  }
}

// 缓进缓出动画
.search-fade-enter-active,
.search-fade-leave-active {
  transition:
    opacity 0.3s ease-in-out,
    transform 0.3s ease-in-out;
}

.search-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.search-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
