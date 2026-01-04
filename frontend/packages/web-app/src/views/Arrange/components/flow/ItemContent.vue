<script setup lang="ts">
import { DoubleRightOutlined } from '@ant-design/icons-vue'
import { useTheme } from '@rpa/components'
import { useEventBus } from '@vueuse/core'
import { isEmpty, throttle } from 'lodash-es'
import { nextTick, ref } from 'vue'
import type { PropType } from 'vue'

import CustomCheckbox from '@/components/CustomCheckbox.vue'
import { showTriggerInputKey } from '@/constants/eventBusKey'
import { useFlowStore } from '@/stores/useFlowStore'
import { Catch, LOOP_END } from '@/views/Arrange/config/atomKeyMap'
import { FLOW_ACTIVE, FLOW_DISABLE, FLOW_FORBID } from '@/views/Arrange/config/flow'
import { FLOW_DEBUGGING, PAGE_INIT_INDENT, PAGE_LEVEL_INDENT } from '@/views/Arrange/config/flow.ts'

import {
  checkboxChange,
  clickAtom,
  contextmenu,
  dbclickAtom,
  getBreakpointClass,
  toggleBreakPoint,
  toggleFold,
} from './hooks/useFlow'
import { useRenderList } from './hooks/useRenderList'
import ItemAction from './ItemAction.vue'
import ItemDesc from './ItemDesc.vue'
import ItemTitle from './ItemTitle.vue'

const { item, index } = defineProps({
  item: {
    type: Object as PropType<RPA.Atom>,
  },
  index: {
    type: Number,
  },
})

const { colorTheme } = useTheme()
const flowStore = useFlowStore()
const { triggerInsert, canInsert } = useRenderList()

const content = ref() // 节点内容
const addPos = ref<'top' | 'bottom' | ''>('') // 添加按钮位置 top | bottom
const addPosStyle = ref({}) // 添加按钮样式

const mouseMove = throttle((e: MouseEvent) => {
  if (content.value) {
    const domRect = content.value.getBoundingClientRect()
    const pos = (e.clientY > domRect.top + domRect.height / 2) || index === 0 ? 'bottom' : 'top'
    if (canInsert(item, pos)) {
      addPosStyle.value = {
        [pos]: 0,
      }
      addPos.value = pos
    }
    else {
      addPosStyle.value = {}
      addPos.value = ''
    }
  }
}, 100, { leading: true, trailing: false })

function mouseLeave() {
  addPosStyle.value = {}
  addPos.value = ''
}

// 展示输入框
function showTriggerInput() {
  triggerInsert(item, addPos.value)
  addPosStyle.value = {}
  addPos.value = ''
  // 通知输入框聚焦
  const bus = useEventBus(showTriggerInputKey)
  nextTick(() => bus.emit())
}

function rowWidth(item: RPA.Atom) {
  return {
    width: `${item.level * 30 + PAGE_INIT_INDENT + 1 - 10}`,
  }
}

function handleJumpBack(payload: MouseEvent) {
  payload.stopPropagation()
  flowStore.jumpBack()
}
</script>

<template>
  <div
    class="flow-list-item-header"
    :class="{
      [FLOW_DISABLE]: item.disabled,
      [FLOW_ACTIVE]: item.checked,
      [FLOW_FORBID]: LOOP_END.concat([Catch]).includes(item.key),
      [FLOW_DEBUGGING]: item.debugging,
    }"
    @click="clickAtom($event, item)"
    @dblclick="dbclickAtom($event, item)"
    @contextmenu.prevent="contextmenu($event, item)"
  >
    <span class="row-left" :style="rowWidth(item)">
      <span class="row-num">{{ index + 1 }}</span>
      <template v-if="flowStore.multiSelect">
        <CustomCheckbox v-model="item.checked" @click.stop @change="checkboxChange($event, item)" />
      </template>
      <template v-else>
        <DoubleRightOutlined
          v-if="item.id && flowStore.jumpFlowId === item.id"
          :id="`jump-back__${item.id}`"
          class="text-primary inline-flex text-xs"
          :rotate="90"
          @click="handleJumpBack"
        />
        <a-tooltip v-else-if="(!item.disabled) && !isEmpty(item?.nodeError)">
          <template #title>
            <div v-for="(validateText, idx) in item.nodeError">
              {{ idx + 1 }}、{{ validateText }}
            </div>
          </template>
          <rpa-hint-icon name="error" />
        </a-tooltip>
        <span
          v-else
          :class="getBreakpointClass(item)"
          @click.prevent.stop="toggleBreakPoint([item.id], !item.breakpoint)"
        />
      </template>
      <rpa-icon v-if="item.hasFold" class="absolute -right-2" size="16" :name="item.isOpen ? 'un-fold' : 'fold'" @click="toggleFold(item)" />
    </span>
    <div
      ref="content"
      :style="`padding-left: ${(item.level - 1) * PAGE_LEVEL_INDENT}px`"
      class="relative flex-1"
      @mousemove="mouseMove"
      @mouseleave="mouseLeave"
    >
      <div class="addAtom" :class="addPos" :style="addPosStyle">
        <div class="addAtom-btn" @click.stop="showTriggerInput">
          <rpa-hint-icon name="python-package-plus" size="14" class="addAtom-btn-icon" />
        </div>
        <div class="addAtom-line bg-primary" />
      </div>
      <div class="row-content" :class="[colorTheme]">
        <ItemTitle :item="item" />
        <ItemDesc :item="item" />
        <ItemAction :item="item" />
      </div>
      <template v-for="level in item.level">
        <div
          v-if="level > 1"
          class="guideline absolute top-0 w-[2px] h-full bg-primary"
          :style="`left: ${(level - 1) * PAGE_LEVEL_INDENT}px`"
        />
      </template>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.addAtom {
  display: none;
  position: absolute;
  left: -12px;
  width: calc(100% + 12px);
  pointer-events: none;

  &.bottom,
  &.top {
    display: block;
  }

  &-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    background: $color-primary;
    border-radius: 10px;
    color: #ffffff;
    cursor: pointer;
    pointer-events: auto;
    z-index: 1;

    &:hover {
      & + .addAtom-line {
        display: block;
      }
    }
  }

  &-line {
    display: none;
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 100%;
    height: 2px;
    z-index: 0;
  }
}
</style>
