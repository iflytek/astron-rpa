<script lang="ts" setup>
import { Empty } from 'ant-design-vue'
import { ref, watch } from 'vue'

import { LRUCache } from '@/utils/lruCache'

import ElementGroupContextmenu from '@/components/ElementGroupContextmenu/Index.vue'
import { IMAGES_TREE_EXPANDE_KEYS } from '@/constants'
import type { ElementGroup } from '@/types/resource.d'
import type { ElementActionType } from '@/types/resource.d.ts'

import { useGroupManager } from '../bottomTools/components/hooks/useGroup.ts'

import CvItem from './CvItem.vue'
import { useCvPick } from './hooks/useCvPick.ts'

const props = defineProps<{
  treeData: ElementGroup[]
  collapsed: boolean
  storageId?: string
  elementActions?: ElementActionType[]
  disabledContextmenu?: boolean
  itemChosed?: string
  emptyText?: string
}>()

const emits = defineEmits(['click', 'actionClick'])

const openKeyLRUCache = new LRUCache<string[]>(
  IMAGES_TREE_EXPANDE_KEYS,
  10,
  [],
)

const useGroup = useGroupManager()

// 右键菜单点击
function contextmenu(key: string, item: ElementGroup) {
  switch (key) {
    case 'rename':
      useGroup.renameGroup(item, 'cv')
      break
    case 'delete':
      useGroup.delGroup(item, 'cv')
      break
    case 'cvPick':
      useCvPick().pick({ groupId: item.id, entry: 'group' })
      break
    default:
      break
  }
}

// 点击cvitem
function itemClick(item: any) {
  emits('click', item)
}

function getOpenKeys(): string[] {
  if (!props.collapsed) {
    return props.treeData.map(i => i.id)
  }
  else if (props.storageId) {
    return openKeyLRUCache.get(props.storageId)
  }
  return []
}

// 展开折叠
const openKeys = ref<string[]>(getOpenKeys())

function toggleOpen(key: string, flag: boolean) {
  if (flag) {
    updateOpenKeys([...openKeys.value, key])
  }
  else {
    updateOpenKeys(openKeys.value.filter(i => i !== key))
  }
}

function updateOpenKeys(keys: string[]) {
  openKeys.value = keys
  if (props.storageId) {
    openKeyLRUCache.set(props.storageId, keys)
  }
}

// 全部展开/折叠
watch(
  () => [props.collapsed, props.treeData],
  () => {
    const keys = getOpenKeys()
    updateOpenKeys(keys)
  }
)
</script>

<template>
  <div id="cv-group" class="cv-group h-full overflow-y-auto">
    <div class="cv-group-list" v-if="treeData.length > 0">
      <div
        v-for="item in treeData"
        class="cv-group-item"
        :class="{ 'cv-group-item-active': openKeys.includes(item.id) }"
      >
        <ElementGroupContextmenu
          pick-type="cv"
          :disabled="disabledContextmenu"
          :group-id="item.id"
          @contextmenu="(key) => contextmenu(key, item)"
        >
          <template #content>
            <div
              class="flex items-center cursor-pointer h-6 mb-[6px]"
              @click="toggleOpen(item.id, !openKeys.includes(item.id))"
            >
              <rpa-icon
                name="caret-down-small"
                size="16"
                :class="{ '-rotate-90': !openKeys.includes(item.id) }"
              />
              <rpa-icon name="folder" size="16" class="mr-1 ml-2" />
              <span class="select-none text-xs">{{ item.name }}</span>
            </div>
          </template>
        </ElementGroupContextmenu>
        <div
          v-if="openKeys.includes(item.id)"
          class="cv-list flex align-center flex-wrap"
        >
          <CvItem
            v-for="i in item.elements"
            :key="i.id"
            :element-actions="elementActions"
            :item-data="i"
            :group-id="item.id"
            :item-chosed="itemChosed"
            @click="itemClick"
            @action-click="emits('actionClick')"
          />
        </div>
      </div>
    </div>
    
    <a-empty v-else :image="Empty.PRESENTED_IMAGE_SIMPLE" :description="props.emptyText" />
  </div>
</template>
