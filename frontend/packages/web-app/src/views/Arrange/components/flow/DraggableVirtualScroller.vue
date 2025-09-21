<script setup lang="ts" generic="T">
import { reactiveComputed, syncRefs, useResizeObserver, useScroll } from '@vueuse/core'
import Sortable from 'sortablejs'
import { computed, onMounted, onUnmounted, reactive, ref, useAttrs, useTemplateRef, watch } from 'vue'
import type { Ref } from 'vue'

interface DraggableContext {
  element: T
  index: number
}

interface DraggableElement extends HTMLElement {
  __draggable_context: DraggableContext
}

interface Size {
  size: number
  accumulator: number
}

const props = withDefaults(defineProps<{
  items: T[] // 列表数据
  itemSize?: number // 列表项高度，静态高度需传入
  minItemSize?: number // 列表项最小高度，动态高度需传入
  itemKey: PropertyKey // 唯一键
  buffer?: number // 缓冲数量
}>(), {
  buffer: 20,
})

const emit = defineEmits<{
  (evt: 'change', e: Partial<Record<'added' | 'removed' | 'moved', any>>): void
  (evt: 'move', e: any): void
  (evt: 'end', e: any): void
  (evt: 'add', e: any): void
  (evt: 'remove', e: any): void
}>()

const scroller = useTemplateRef('scroller')
const wrapper = useTemplateRef('wrapper')
const realItems = ref([]) as Ref<T[]>
const itemRefs = ref<DraggableElement[]>([])
syncRefs(() => [...props.items], realItems)

// 起始项索引
const start = ref(0)
// 结束项索引
const end = ref(0)
// 可见项
const visibleItems = computed(() => realItems.value.slice(start.value, end.value))
// 总高度
const totalHeight = ref(0)
// 偏移量
const offset = ref(0)
// 滚动距离
const scrollTop = useScroll(scroller).y

const cacheSizes = reactive<Record<string, number>>({})
const sizes = reactiveComputed(() => {
  if (props.itemSize == null) {
    const _sizes = {
      '-1': { accumulator: 0 },
    }
    const { items, minItemSize } = props
    let accumulator = 0
    let current = minItemSize
    for (let i = 0; i < items.length; i++) {
      current = cacheSizes[i] || minItemSize || 0
      accumulator += current
      _sizes[i] = { accumulator, size: current }
    }
    return _sizes
  }
  else {
    return {}
  }
}) as Record<string, Size>

useResizeObserver(() => itemRefs.value.slice(start.value, end.value), (entries) => {
  entries.forEach((entry) => {
    const el = entry.target as DraggableElement
    const { index } = getContext(el)
    cacheSizes[index] = el.offsetHeight
  })
})

// let rafId
watch([realItems, scrollTop], () => {
  // cancelAnimationFrame(rafId);
  // rafId = requestAnimationFrame(updateVisibleRange)
  updateVisibleRange()
})

function updateVisibleRange() {
  const itemSize = props.itemSize
  const items = props.items
  const buffer = props.buffer
  const count = items.length
  const scroll = {
    start: scroller.value?.scrollTop ?? 0,
    end: (scroller.value?.scrollTop ?? 0) + (scroller.value?.clientHeight ?? 0),
  }

  let startIndex = 0; let endIndex = 0; let totalSize = 0

  if (itemSize == null) { // 动态高度
    let left = 0
    let right = count - 1
    let mid = Math.floor((left + right) / 2)

    while (left !== right) {
      mid = Math.floor((left + right) / 2)
      const h = sizes[mid].accumulator
      if (h <= scroll.start) {
        left = mid + 1
      }
      else {
        right = mid
      }
    }

    startIndex = left
    startIndex < 0 && (startIndex = 0)

    for (
      endIndex = startIndex;
      endIndex < count && sizes[endIndex].accumulator < scroll.end;
      endIndex++
    )
      endIndex++
    endIndex > count && (endIndex = count)

    totalSize = sizes[count - 1].accumulator
  }
  else { // 固定高度
    startIndex = Math.floor(scroll.start / itemSize)
    startIndex < 0 && (startIndex = 0)

    endIndex = Math.ceil(scroll.end / itemSize)
    endIndex > count && (endIndex = count)

    totalSize = count * itemSize
  }

  start.value = Math.max(startIndex - buffer, 0)
  end.value = Math.min(endIndex + buffer, count)
  totalHeight.value = totalSize
  offset.value = itemSize ? start.value * itemSize : sizes[start.value - 1].accumulator
}

function getItemStyle(index: number) {
  if (props.itemSize) {
    return {
      height: `${props.itemSize}px`,
    }
  }
  else {
    return {
      minHeight: `${sizes[index].size ?? props.minItemSize}`,
    }
  }
}

function scrollTo(idOrIndex: string | number) {
  let index = -1
  if (typeof idOrIndex === 'number') {
    index = idOrIndex
  }
  else {
    index = realItems.value.findIndex(item => item[props.itemKey] === idOrIndex)
  }
  scrollToIndex(index)
}

function scrollToIndex(index: number, duration: number = 300) {
  if (index < 0 || index >= realItems.value.length) {
    throw new Error(
      `[ScrollTo Error] 目标索引${index}越界（有效范围：0~${realItems.value.length - 1}）`,
    )
  }

  const from = scrollTop.value
  const to = props.itemSize ? index * props.itemSize : sizes[index - 1].accumulator
  smoothScrollTo(from, to, duration).then(() => {
    if (props.itemSize)
      return

    // 动态高度需检测目标项累计高度是否发生变化
    const newTo = sizes[index - 1].accumulator
    const diff = Math.abs(newTo - to)
    if (diff) {
      scrollToIndex(index, diff / newTo * duration)
    }
    else {
      const stopWatch = watch(() => sizes[index - 1].accumulator, (newTo) => {
        const diff = Math.abs(newTo - to)
        if (diff) {
          scrollToIndex(index, diff / newTo * duration)
        }
      })
      setTimeout(stopWatch, 100)
    }
  })
}

function smoothScrollTo(from: number, to: number, duration: number) {
  const change = to - from
  let startTime = null

  return new Promise((resolve) => {
    function animateScroll(currentTime) {
      if (!startTime)
        startTime = currentTime
      const elapsed = currentTime - startTime!
      const progress = Math.min(elapsed / duration, 1)
      scrollTop.value = from + change * progress
      if (progress < 1) {
        requestAnimationFrame(animateScroll)
      }
      else {
        resolve(true)
      }
    }
    requestAnimationFrame(animateScroll)
  })
}

function initSortable() {
  const options = createSortableOptions({
    ...useAttrs(),
    onAdd: (e) => {
      removeElement(e.item)
      const { element } = getContext(e.item)
      const newIndex = e.newIndex + start.value
      realItems.value.splice(newIndex, 0, element)
      emit('change', { added: { element, newIndex } })
    },
    onRemove: (e) => {
      insertElementAt(e.item, e.oldIndex)
      const { items, itemKey } = props
      const { element } = getContext(e.item)
      const oldIndex = items.findIndex(item => item[itemKey] === element[itemKey])
      realItems.value.splice(oldIndex, 1)
      emit('change', { removed: { element, oldIndex } })
    },
    onMove: (e) => {
      if (e.from === e.to) {
        const oldIndex = getContext(e.dragged).index
        const newIndex = getContext(e.related).index
        realItems.value.splice(newIndex, 0, realItems.value.splice(oldIndex, 1)[0])
      }
    },
    onEnd: (e) => {
      if (e.from === e.to) {
        const { items, itemKey } = props
        const { element } = getContext(e.item)
        const oldIndex = items.findIndex(item => item[itemKey] === element[itemKey])
        const newIndex = realItems.value.findIndex(item => item[itemKey] === element[itemKey])
        if (oldIndex !== newIndex) {
          emit('change', { moved: { element, oldIndex, newIndex } })
        }
      }
    },
  })
  return new Sortable(wrapper.value, options)
}

function createSortableOptions(options) {
  const events = ['Add', 'Remove', 'Move', 'End'] as const
  events.forEach((event) => {
    const eventHandle = options[`on${event}`]
    options[`on${event}`] = (e) => {
      eventHandle(e)
      emit(event.toLowerCase() as any, e)
    }
  })
  return options
}

function setItemRef(el, context: DraggableContext) {
  if (el) {
    itemRefs.value[context.index] = el
    addContext(el, context)
  }
}

function addContext(domElement, context: DraggableContext) {
  domElement && (domElement.__draggable_context = context)
}

function getContext(domElement: DraggableElement) {
  return domElement.__draggable_context
}

function removeElement(domElement: DraggableElement) {
  domElement.parentElement?.removeChild(domElement)
}

function insertElementAt(domElement: DraggableElement, position: number) {
  const parentElement = domElement.parentElement
  const anchorElement
    = position === 0
      ? parentElement?.children[0]
      : parentElement?.children[position - 1].nextSibling
  parentElement?.insertBefore(domElement, anchorElement ?? null)
}

let sortableInstance: any = null
onMounted(() => {
  updateVisibleRange()
  sortableInstance = initSortable()
})

onUnmounted(() => {
  sortableInstance?.destroy()
  sortableInstance = null
})

defineExpose({
  scrollTo,
})
</script>

<template>
  <div ref="scroller" class="virtual-scroll">
    <div ref="wrapper" class="virtual-scroll__wrapper" :style="{ transform: `translateY(${offset}px)` }">
      <div
        v-for="(item, index) in visibleItems"
        :key="item[itemKey]"
        :ref="(el) => setItemRef(el, { element: item, index: start + index })"
        class="virtual-scroll__item"
        :style="getItemStyle(start + index)"
      >
        <slot :item="item" :index="start + index" />
      </div>
    </div>
    <div class="virtual-scroll__placeholder" :style="{ height: `${totalHeight}px` }" />
  </div>
</template>

<style scoped>
.virtual-scroll {
  position: relative;
  width: 100%;
  height: 100%;
  overflow-y: auto;
  overflow-anchor: none;
}

.virtual-scroll__wrapper {
  will-change: transform;
}

.virtual-scroll__placeholder {
  position: absolute;
  top: 0;
  width: 100%;
  pointer-events: none;
}
</style>
