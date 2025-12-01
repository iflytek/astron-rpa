<script setup lang="ts">
import hotkeys from 'hotkeys-js'
import { escapeRegExp, isArray } from 'lodash-es'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch, useTemplateRef } from 'vue'
import { refDebounced } from '@vueuse/core'

import { SCOPE } from '@/constants/shortcuts'
import { useFlowStore } from '@/stores/useFlowStore'
import { toggleFold } from '@/views/Arrange/components/flow/hooks/useFlow'
import SearchWidget from '@/views/Arrange/components/search/SearchWidget.vue'
import { backContainNodeIdx } from '@/views/Arrange/utils/flowUtils'
import { atomScrollIntoView, decodeHtml } from '@/views/Arrange/utils/index'
import { renderAtomRemark } from '@/views/Arrange/utils/renderAtomRemark'
import { changeSelectAtoms } from '@/views/Arrange/utils/selectItemByClick'

const SEARCH_HOTKEY = 'Ctrl+F'
const ARROW_UP_KEY = 'up'
const ARROW_DOWN_KEY = 'down'

const showSearch = ref(false)
const activeIndex = ref(0)
const searchKeyword = ref('')
const debouncedSearchKeyword = refDebounced(searchKeyword, 300)
const searchWidget = useTemplateRef('searchWidget')
const flowStore = useFlowStore()

// 搜索结果显示
const searchResults = computed(() => {
  if (!showSearch.value || !debouncedSearchKeyword.value) return []

  const searchRegex = new RegExp(escapeRegExp(debouncedSearchKeyword.value), 'i')
  const dataWithComments = flowStore.simpleFlowUIData.map((item, index) => {
    const comment = renderAtomRemark(item)
    const commentText = isArray(comment)
      ? comment.map(i => (i.variable ? decodeHtml(i.sr[2]) : i)).join('')
      : comment
    return { id: item.id, title: item.alias, commentText, item, index }
  })

  return dataWithComments.filter(
    it => searchRegex.test(it.title) || searchRegex.test(it.commentText)
  )
})

// 当前激活的搜索结果
const activeSearchAtom = computed(() => {
  return searchResults.value[activeIndex.value]
})

// 展开包含当前搜索结果的折叠组
function expandContainingGroups(atomIndex: number) {
  const groupKeys = Object.keys(flowStore.nodeContactMap)
  groupKeys.forEach((groupId) => {
    const groupStartIdx = flowStore.simpleFlowUIData.findIndex(node => node.id === groupId)
    const groupEndIdx = backContainNodeIdx(groupId)
    
    if (groupStartIdx > -1 && groupStartIdx <= atomIndex && groupEndIdx >= atomIndex) {
      toggleFold(flowStore.simpleFlowUIData[groupStartIdx])
    }
  })
}

// 处理搜索结果切换
function handleSearchResultChange(atomId: string | undefined) {
  if (!atomId) {
    activeIndex.value = 0
    return
  }

  const canvas = document.querySelector<HTMLElement>('.postTask-content-canvas');
  if (canvas) {
    canvas.scrollTop = 0;
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
  if (searchResults.value.length === 0) return
  const total = searchResults.value.length
  activeIndex.value = (activeIndex.value + 1) % total
}

function previous() {
  if (searchResults.value.length === 0) return
  const total = searchResults.value.length
  activeIndex.value = activeIndex.value === 0 ? total - 1 : activeIndex.value - 1
}

// 上下键处理函数
function handleArrowUp() {
  console.log('handleArrowUp')
  previous()
}

function handleArrowDown() {
  next()
}

// 监听搜索结果变化
watch(
  () => activeSearchAtom.value?.id,
  handleSearchResultChange
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
        class="search-widget"
        v-model:value="searchKeyword"
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
  transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
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
