<script setup lang="ts">
import { SearchOutlined } from '@ant-design/icons-vue'
import hotkeys from 'hotkeys-js'
import { debounce, escapeRegExp, isArray, isEmpty, isNumber } from 'lodash-es'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { SCOPE } from '@/constants/shortcuts'
import { useFlowStore } from '@/stores/useFlowStore'
import { toggleFold } from '@/views/Arrange/components/flow/hooks/useFlow'
import SearchWidget from '@/views/Arrange/components/search/SearchWidget.vue'
import { backContainNodeIdx } from '@/views/Arrange/utils/flowUtils'
import { atomScrollIntoView, decodeHtml } from '@/views/Arrange/utils/index'
import { renderAtomRemark } from '@/views/Arrange/utils/renderAtomRemark'
import { changeSelectAtoms } from '@/views/Arrange/utils/selectItemByClick'

const searchHotkey = 'Ctrl+F'

const showSearch = ref(false)
const searchWidget = ref(null)

function showSearchWidget() {
  showSearch.value = true
  nextTick(() => {
    searchWidget.value.focus()
  })
}
function closeSearchWidget() {
  showSearch.value = false
}

const activeSearchIndex = ref(0)
const searchKeyword = ref('')

const search = debounce((val) => {
  searchKeyword.value = val
}, 300)

const searchResults = computed(() => {
  if (!showSearch.value || isEmpty(searchKeyword.value))
    return []
  const datas = useFlowStore().simpleFlowUIData.map((item, index) => {
    const comment = renderAtomRemark(item)
    const commentText = isArray(comment)
      ? comment.map(i => i.variable ? decodeHtml(i.sr[2]) : i).join('')
      : comment
    return { id: item.id, title: item.alias, commentText, item, index }
  })

  const reg = new RegExp(escapeRegExp(searchKeyword.value), 'i')
  return datas
    .filter(it => reg.test(it.title) || reg.test(it.commentText))
})

function next() {
  activeSearchIndex.value
    = activeSearchIndex.value + 1 === searchResults.value.length
      ? 0
      : activeSearchIndex.value + 1
}
function previous() {
  activeSearchIndex.value
    = activeSearchIndex.value === 0
      ? searchResults.value.length - 1
      : activeSearchIndex.value - 1
}

const activeSearchAtom = computed(() => {
  return isNumber(activeSearchIndex.value)
    ? searchResults.value[activeSearchIndex.value]
    : undefined
})

watch(
  () => activeSearchAtom.value?.id,
  (val) => {
    if (!val) {
      activeSearchIndex.value = 0
      return
    }
    const flowStore = useFlowStore()
    document.querySelector(`.postTask-content-canvas`).scrollTop = 0
    changeSelectAtoms(val, null, false)
    const groupArr = Object.keys(flowStore.nodeContactMap)
    groupArr.forEach((i) => {
      const findIdx = flowStore.simpleFlowUIData.findIndex(node => node.id === i)
      const endIdx = backContainNodeIdx(i)
      if (findIdx <= activeSearchAtom.value.index && endIdx >= activeSearchAtom.value.index)
        toggleFold(flowStore.simpleFlowUIData[findIdx])
    })
    nextTick(() => {
      atomScrollIntoView(val)
    })
  },
)

onMounted(() => {
  hotkeys(searchHotkey, SCOPE, showSearchWidget)
})

onBeforeUnmount(() => {
  hotkeys.unbind(searchHotkey, SCOPE)
})
</script>

<template>
  <div class="search fixed">
    <a-tooltip placement="bottom" :title="$t('search')" overlay-class-name="editorTools-overlay">
      <div class="search-btn cursor-pointer" @click="showSearchWidget">
        <SearchOutlined class="editorTools-font" />
      </div>
    </a-tooltip>
    <SearchWidget
      v-if="showSearch" ref="searchWidget" :value="searchKeyword" :active="activeSearchIndex + 1"
      :total="searchResults.length" @input="search" @next="next" @previous="previous" @close="closeSearchWidget"
    />
  </div>
</template>

<style scoped lang="scss">
.search {
  z-index: 1;
}
</style>
