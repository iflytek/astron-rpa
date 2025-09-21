<script lang="ts" setup>
import type { Trigger } from 'ant-design-vue/es/dropdown/props'
import { isFunction } from 'lodash-es'

export interface IMenuItem {
  key: string
  name: string
  disabled?: boolean
  fn?: () => void
}

defineProps({
  trigger: {
    type: String,
    default: 'contextmenu', // click-点击...触发下拉,  contextmenu-右键菜单触发，
  },
  menus: {
    type: Array as () => Array<IMenuItem>,
    default: () => [],
  },
})

const emit = defineEmits(['click'])

function menuItemClick(item: IMenuItem) {
  isFunction(item.fn) && item.fn()
  emit('click', item)
}
</script>

<template>
  <a-dropdown
    :trigger="[trigger] as Trigger[]"
    :destroy-popup-on-hide="true"
    overlay-class-name="subProcessItem-overlay"
  >
    <slot />
    <template #overlay>
      <a-menu>
        <a-menu-item v-for="item in menus" :key="item.key" class="process-contextmenu-item" :disabled="item.disabled" @click="() => menuItemClick(item)">
          <slot name="menu-item" :item="item">
            {{ item.name }}
          </slot>
        </a-menu-item>
      </a-menu>
    </template>
  </a-dropdown>
</template>

<style lang="scss">
.process-contextmenu-item {
  font-size: 12px !important;
}
</style>
