<script setup lang="ts">
defineOptions({
  name: 'MenuItem',
})

defineProps({
  route: {
    type: Object,
    default: () => { },
  },
})

const emits = defineEmits(['getCurrentMenuKey'])

// 获取菜单key
function handleMenuClick(key: string) {
  emits('getCurrentMenuKey', key)
}
</script>

<template>
  <a-sub-menu
    v-if="route.children && route.children.length > 0"
    :key="route.name"
    :title="$t(route.name)"
    :expand-icon="() => null"
  >
    <MenuItem
      v-for="child in route.children" :key="child.name" :route="child" @get-current-menu-key="handleMenuClick"
    />
  </a-sub-menu>
  <a-menu-item
    v-else
    :key="route.name as string"
    class="!px-y !px-4 !mx-0 !my-2 !w-full"
    @click="() => handleMenuClick(route.name)"
  >
    <template v-if="route.meta.iconPark" #icon>
      <rpa-icon size="16px" :name="route.meta.iconPark" />
    </template>
    {{ $t(route.name) }}
  </a-menu-item>
</template>
