<script lang="ts" setup>
import { computed, provide, ref } from 'vue'
import type { Ref } from 'vue'

type Position = 'top' | 'left' | 'right' | 'bottom'

interface Tab {
  name: string
  value: PropertyKey
  size?: string | number
}

interface TabsContext {
  activeTab: Ref<Tab['value']>
  position: Ref<Position>
  registerTab: (tab: Tab) => void
}

const props = withDefaults(defineProps<{
  modelValue: string
  position?: Position
  doubleClickClear?: boolean
  beforeSelectChange?: (tab: Tab['value']) => boolean | void // 返回值为false则取消更改
}>(), {
  position: 'top',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: PropertyKey): void
}>()

const tabs = ref([]) as Ref<Tab[]>
const activeTab = computed(() => props.modelValue)
const positionClass = computed(() => `tabs-${props.position}`)

const activeStyle = computed(() => {
  // const isVertical = ['top', 'bottom'].includes(props.position || '')
  // const mainDimension = isVertical ? 'height' : 'width'
  // const activeSize = tabs.value.find(item => item.value === activeTab.value)?.size ?? 0
  // const validSize = Number.isNaN(Number(activeSize)) ? activeSize : `${Number(activeSize)}px`

  return {
    // [mainDimension]: validSize,
    // transition: 'all 0.3s ease',
  }
})

function selectTab(value: Tab['value']) {
  if (props.beforeSelectChange && props.beforeSelectChange(value) === false) {
    return
  }
  if (props.doubleClickClear && activeTab.value === value) {
    emit('update:modelValue', '')
  }
  else {
    emit('update:modelValue', value)
  }
}

function registerTab(tab: Tab) {
  if (tabs.value.find(item => item.value === tab.value))
    return
  tabs.value.push(tab)
}

provide<TabsContext>('tabsContext', {
  activeTab,
  position: computed(() => props.position),
  registerTab,
})
</script>

<template>
  <div :class="positionClass" class="tabs">
    <div class="tabs-header">
      <div
        v-for="(tab, index) in tabs" :key="tab.value ?? index" :class="{ active: activeTab === tab.value }"
        class="tab-bar dark:text-[rgba(255,255,255,0.65)] text-[rgba(0,0,0,0.65)]" @click="selectTab(tab.value)"
      >
        <slot name="bar" :tab="tab">
          <span>{{ tab.name }}</span>
        </slot>
      </div>
    </div>
    <div :style="activeStyle" class="tabs-content">
      <slot />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.tabs {
  --tab-padding-main: 8px;
  --tab-padding-cross: 12px;
  --text-color: #000000;
  --active-color: var(--color-primary);
  --active-text-color: var(--active-color);
  --tab-bar-gap: 16px;

  display: flex;
  font-size: 14px;

  .tabs-header {
    display: flex;

    .tab-bar {
      position: relative;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
      user-select: none;

      &:hover {
        color: #9e99ff;
      }

      &.active {
        font-weight: 600;
        color: rgba(0, 0, 0, 0.85);

        .dark & {
          color: rgba(255, 255, 255, 0.85);
        }

        &::after {
          content: '';
          display: block;
          position: absolute;
          background: var(--active-color);
        }
      }
    }
  }

  .tabs-content {
    display: flex;
    position: relative;
  }
}

.tabs-top {
  flex-direction: column;

  .tabs-header {
    flex-direction: row;

    .tab-bar {
      padding: var(--tab-padding-cross) var(--tab-padding-main);
      cursor: pointer;

      &.active::after {
        left: 0;
        bottom: 0;
        width: 100%;
        height: 2px;
      }

      &:not(:first-child) {
        margin-left: var(--tab-bar-gap);
      }
    }
  }
}

.tabs-left {
  flex-direction: row;

  .tabs-header {
    flex-direction: column;

    .tab-bar {
      padding: 20px 10px;
      cursor: pointer;
      span {
        writing-mode: vertical-rl;
      }

      &.active::after {
        right: 0;
        top: 0;
        width: 2px;
        height: 100%;
      }

      &:not(:first-child) {
        margin-top: var(--tab-bar-gap);
      }
    }
  }
}

.tabs-right {
  flex-direction: row-reverse;

  .tabs-header {
    flex-direction: column;

    .tab-bar {
      padding: var(--tab-padding-main) var(--tab-padding-cross);
      cursor: pointer;

      span {
        writing-mode: vertical-rl;
      }

      &.active::after {
        left: 0;
        top: 0;
        width: 2px;
        height: 100%;
      }

      &:not(:first-child) {
        margin-top: var(--tab-bar-gap);
      }
    }
  }
}

.tabs-bottom {
  flex-direction: column-reverse;

  .tabs-header {
    flex-direction: row;

    .tab-bar {
      padding: var(--tab-padding-cross) var(--tab-padding-main);
      cursor: pointer;

      &.active::after {
        left: 0;
        top: 0;
        width: 100%;
        height: 2px;
      }

      &:not(:first-child) {
        margin-left: var(--tab-bar-gap);
      }
    }
  }
}
</style>
