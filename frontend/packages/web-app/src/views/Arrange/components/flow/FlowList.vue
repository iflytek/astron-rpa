<script setup lang="ts">
import { useTheme } from '@rpa/components'
import { useElementVisibility, useEventBus, useScroll } from '@vueuse/core'
import { message } from 'ant-design-vue'
import { computed, onBeforeUnmount, useTemplateRef, watch } from 'vue'

import { atomScrollIntoViewKey } from '@/constants/eventBusKey'
import { SMARTCOMPONENT } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { useProcessStore } from '@/stores/useProcessStore'

import ContextMenu from './ContextMunus.vue'
import DraggableVirtualScroller from './DraggableVirtualScroller.vue'
import { draggableAddStyle } from './hooks/useFlow'
import { useRenderListProvide } from './hooks/useRenderList'
import { useRunDebug } from './hooks/useRunDebug'
import { useFlowStateProvide } from './hooks'
import Item from './Item.vue'
import { VisualEditor } from '../../canvasManager'

interface FlowListProps {
  resourceId: string
  manage: VisualEditor
}

const props = defineProps<FlowListProps>()
const { rawList, flowManager } = useFlowStateProvide(props)
const { colorTheme } = useTheme()
const draggableRef = useTemplateRef('draggableRef')
const processStore = useProcessStore()

// TODO: 需要重构一下
const { renderList, adjustIndex, resetRenderList } = useRenderListProvide(rawList)

// TODO: 这个实现有一定的局限性，如果后面原子能力列表改成虚拟滚动，需要换种实现方式
// 监听跳转按钮的可见性
// const jumpIconIsVisible = useElementVisibility(() => document.getElementById(`jump-back__${flowStore.jumpFlowId}`))
// 监听原子能力列表的滚动事件，在滚动结束时如果存在跳转按钮的原子能力不可见，则隐藏跳转按钮
useScroll(flowManager.containerRef, {
  onStop: () => {
    // if (flowStore.jumpFlowId && !jumpIconIsVisible.value) {
    //   flowStore.setJumpFlowId('')
    // }
  },
})

const bus = useEventBus(atomScrollIntoViewKey)
bus.on((idOrIndex) => {
  draggableRef.value.scrollTo(idOrIndex)
})

useRunDebug()

function handleDragChange(e: any) {
  if (e.added) {
    const { element, newIndex } = e.added
    flowManager.add(element.data.key, newIndex)
  }
  else if (e.moved) {
    const { oldIndex, newIndex } = e.moved
    flowManager.move(oldIndex, newIndex)
    resetRenderList() // 重置插入项位置
  }
}

function handleBeforeAdd(e: { element: any, newIndex: number }) {
  if (e.element?.key === 'smart-component') {
    // useRoutePush({
    //   name: SMARTCOMPONENT,
    //   query: {
    //     projectId: processStore.project.id,
    //     projectName: processStore.project.name,
    //     newIndex: Math.min(e.newIndex, flowStore.simpleFlowUIData.length),
    //   },
    // })
    return false
  }
  else {
    return true
  }
}

async function triggerAdd(key: string, preIndex?: number) {
  flowManager.add(key, preIndex)
}
</script>

<template>
  <div
    :ref="flowManager.containerRef"
    class="listwrapper select-none before:bg-[#000000]/[.08] before:dark:bg-[#FFFFFF]/[.08] right-tab-close-area"
  >
    <ContextMenu>
      <DraggableVirtualScroller
        ref="draggableRef"
        v-slot="{ item, index }"
        :items="renderList"
        :min-item-size="40"
        :class="[colorTheme]"
        :before-add="handleBeforeAdd"
        item-key="id"
        filter=".forbid"
        group="postTree"
        @start="draggableAddStyle"
        @move="draggableAddStyle"
        @change="handleDragChange"
      >
        <Item :key="item.id" :item="item" :index="index" @select="triggerAdd" />
      </DraggableVirtualScroller>
    </ContextMenu>
  </div>
</template>

<style lang="scss">
.listwrapper {
  position: relative;
  height: 100%;

  &::before {
    content: '';
    display: block;
    position: absolute;
    left: 81px;
    top: 0;
    width: 1px;
    height: 100%;
    pointer-events: none;
  }

  .virtual-scroll__wrapper {
    min-height: 100%;
    padding-bottom: 100px;
    overflow-x: hidden;
  }

  .virtual-scroll {
    &::-webkit-scrollbar {
      width: 8px;
    }

    &::-webkit-scrollbar-track {
      background-color: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background-color: #f3f3f7;
    }

    &.dark::-webkit-scrollbar-thumb {
      background-color: rgba(#ffffff, 0.08);
      border-radius: 20px;
    }
  }

  .flow-list-item {
    position: relative;
    outline: none;

    &-header {
      display: flex;
      position: relative;
      cursor: pointer;

      .row-left {
        position: relative;
        top: 13px;
        flex: none;
        display: flex;
        align-items: center;
        width: 82px;
        height: 100%;
        padding-left: 20px;
        z-index: 2;

        &:hover {
          .row-breakpoint {
            display: inline-block;
          }

          .row-breakpoint.disabled {
            display: none;
          }
        }

        .row-num {
          width: 20px;
          display: inline-block;
          margin-right: 10px;
        }

        .row-breakpoint {
          display: none;
          width: 10px;
          height: 10px;
          border-radius: 5px;
          background: #ddd;
          border: 1px solid #c3c3c3;

          &.active {
            background: #fdc2c2;
            border: 1px solid #ff796c;
            display: inline-block !important;
          }
        }
      }

      .row-content {
        display: -webkit-box;
        word-break: break-all;
        text-overflow: ellipsis;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 3;
        overflow: hidden;

        margin: 3px 8px;
        padding: 7px 8px;
        line-height: 22px;
        border: 1px solid transparent;
        border-radius: 8px;
        cursor: pointer;

        .desc {
          display: inline;
          padding-left: 8px;
        }

        .flow-list-item-action {
          position: relative;
          top: 3px;
          display: none;
          gap: 12px;
          padding: 0 8px;
          float: right;
        }

        .anticon {
          margin-right: 4px;
        }

        &:hover {
          background: rgba(#726fff, 0.1);

          .flow-list-item-action {
            display: inline-block;
          }
        }
      }

      &.disable {
        .row-content {
          background: rgba(#a5a4ac, 0.1);

          * {
            color: rgba(#000000, 0.1);
          }
        }

        .dark.row-content {
          * {
            color: rgba(#ffffff, 0.1);
          }
        }
      }

      &.debugging {
        .row-content {
          background: rgba(#f39d09, 0.1);
          border-color: #f39d09;
        }
      }

      &.active {
        .row-content {
          background: rgba(#726fff, 0.1);
          border-color: rgba(#726fff, 0.9);
        }
        .flow-list-item-action {
          display: inline-block;
        }
      }
    }

    &.hide-item {
      visibility: hidden;
      height: 0;
    }

    .anticon {
      width: 16px;
      height: 16px;
      font-size: 16px;
    }
  }

  .sortable-ghost {
    --indent: 82px;

    display: flex;
    padding: 0;
    height: 40px;

    * {
      display: none;
    }

    &::before {
      content: '';
      display: block;
      width: var(--indent);
      height: 100%;
      flex: none;
    }

    &::after {
      content: '';
      display: block;
      height: 100%;
      flex: 1;
      border: 1px dashed #2c69ff;
    }
  }

  .sortable-drag {
    .row-left {
      opacity: 0;
    }

    .addAtom {
      opacity: 0;
    }

    .guideline {
      opacity: 0;
    }
  }
}
</style>
