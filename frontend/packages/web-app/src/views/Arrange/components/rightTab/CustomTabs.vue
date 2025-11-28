<script lang="ts" setup>
import { computed, provide, ref, type Ref } from 'vue'

import type { Tab, TabsContext, Position } from './types'

const activeTab = defineModel<PropertyKey>('modelValue')

const props = withDefaults(defineProps<{
  position?: Position
  doubleClickClear?: boolean
}>(), {
  position: 'top',
})

const tabs = ref([]) as Ref<Tab[]>
const positionClass = computed(() => `tabs-${props.position}`)

function selectTab(value: Tab['value']) {
  if (props.doubleClickClear && activeTab.value === value) {
    activeTab.value = ''
  }
  else {
    activeTab.value = value
  }
}

const registerTab: TabsContext['registerTab'] = (tab) => {
  if (!tabs.value.find(item => item.value === tab.value)) {
    tabs.value.push(tab)
  }
}

const updateTab: TabsContext['updateTab'] = (key, tab) => {
  const index = tabs.value.findIndex(item => item.value === key)
  if (index !== -1) {
    tabs.value[index] = { ...tabs.value[index], ...tab }
  }
}

provide<TabsContext>('tabsContext', {
  activeTab,
  position: computed(() => props.position),
  registerTab,
  updateTab,
})
</script>

<template>
  <div :class="positionClass" class="tabs">
    <div class="tabs-header">
      <div
        v-for="(tab, index) in tabs"
        :key="tab.value ?? index"
        v-show="tab.show"
        :class="{ active: activeTab === tab.value }"
        class="tab-bar dark:text-[rgba(255,255,255,0.65)] text-[rgba(0,0,0,0.65)]"
        @click="selectTab(tab.value)"
      >
        <slot name="bar" :tab="tab">
          <span>{{ tab.name }}</span>
        </slot>
      </div>
    </div>
    <div class="flex relative">
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
}

.tabs-top {
  flex-direction: column;

  .tabs-header {
    flex-direction: row;
    gap: var(--tab-bar-gap);

    .tab-bar {
      padding: var(--tab-padding-cross) var(--tab-padding-main);
      cursor: pointer;

      &.active::after {
        left: 0;
        bottom: 0;
        width: 100%;
        height: 2px;
      }
    }
  }
}

.tabs-left {
  flex-direction: row;

  .tabs-header {
    flex-direction: column;
    gap: var(--tab-bar-gap);

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
    }
  }
}

.tabs-right {
  flex-direction: row-reverse;

  .tabs-header {
    flex-direction: column;
    gap: var(--tab-bar-gap);

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
    }
  }
}

.tabs-bottom {
  flex-direction: column-reverse;

  .tabs-header {
    flex-direction: row;
    gap: var(--tab-bar-gap);

    .tab-bar {
      padding: var(--tab-padding-cross) var(--tab-padding-main);
      cursor: pointer;

      &.active::after {
        left: 0;
        top: 0;
        width: 100%;
        height: 2px;
      }
    }
  }
}
</style>
