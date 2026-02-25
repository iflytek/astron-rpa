<script lang="ts" setup>
import type { Trigger } from 'ant-design-vue/es/dropdown/props'
import { isFunction } from 'lodash-es'

export interface IMenuItem {
  key: string
  name: string
  disabled?: boolean
  fn?: () => void
}

interface DropdownMenuProps {
  trigger?: Trigger
  menus: IMenuItem[]
}

const props = withDefaults(defineProps<DropdownMenuProps>(), {
  trigger: 'contextmenu',
  menus: () => [],
})

const emit = defineEmits(['click'])

function menuItemClick(item: IMenuItem) {
  isFunction(item.fn) && item.fn()
  emit('click', item)
}
</script>

<template>
  <a-dropdown
    :trigger="[props.trigger]"
    :destroy-popup-on-hide="true"
    overlay-class-name="subProcessItem-overlay"
  >
    <slot />
    <template #overlay>
      <a-menu>
        <a-menu-item v-for="item in props.menus" :key="item.key" class="process-contextmenu-item" :disabled="item.disabled" @click="() => menuItemClick(item)">
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
