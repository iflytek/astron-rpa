<script lang="ts" setup>
import { Empty } from 'ant-design-vue'
import { onMounted, ref, watch } from 'vue'

import { scrollToName } from '@/utils/domUtils'
import { LRUCache } from '@/utils/lruCache'

import ElementGroupContextmenu from '@/components/ElementGroupContextmenu/Index.vue'
import { IMAGES_TREE_EXPANDE_KEYS } from '@/constants'
import type { ElementGroup } from '@/types/resource.d'
import type { ElementActionType } from '@/types/resource.d.ts'

import { useGroupManager } from '../bottomTools/components/hooks/useGroup.ts'

import CvItem from './CvItem.vue'
import { useCvPick } from './hooks/useCvPick.ts'

const props = defineProps({
  storageId: String,
  treeData: {
    type: Array as () => Array<ElementGroup>,
  },
  collapsed: {
    type: Boolean,
    default: false,
  },
  elementActions: {
    type: Array<ElementActionType>,
  },
  disabledContextmenu: {
    type: Boolean,
    default: false,
  },
  itemChosed: {
    type: String,
    default: '',
  },
  defaultCollapse: {
    type: Boolean,
    default: false,
  },
})

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

// 展开折叠
const openKeys = ref<string[]>([])
const canUpdateOpenKey = ref(true)

function toggleOpen(key: string, flag: boolean) {
  canUpdateOpenKey.value = false
  if (flag) {
    openKeys.value.push(key)
  }
  else {
    openKeys.value = openKeys.value.filter(i => i !== key)
  }
}

watch(
  () => props.treeData,
  (val) => {
    let keys: string[] = []

    if (canUpdateOpenKey.value && !props.defaultCollapse) {
      keys = val.map(i => i.id)
    }
    else if (props.storageId) {
      keys = openKeyLRUCache.get(props.storageId)
    }

    openKeys.value = keys
  },
  { immediate: true },
)

watch(
  () => props.defaultCollapse,
  () => {
    canUpdateOpenKey.value = true
  },
  { immediate: true },
)

// 全部展开/折叠
watch(
  () => props.collapsed,
  (val) => {
    setTimeout(() => {
      openKeys.value = val ? props.treeData.map(i => i.id) : []
    }, 100)
  },
  { immediate: true },
)

// 滚动到 name 项
function scrollInto(id: string) {
  const isExist = props.treeData.find(i => i.elements.some(j => j.id === id))
  if (!isExist)
    return // 不存在, 默认则不需要滚动
  toggleOpen(isExist.id, true)
  scrollToName(id)
}

function autoScroll() {
  if (props.itemChosed && props.treeData.length > 0) {
    scrollInto(props.itemChosed)
  }
}

onMounted(() => autoScroll())

// 监听 expandedKeys 变化，保存到 localStorage
watch(
  openKeys,
  (val) => {
    if (props.storageId) {
      openKeyLRUCache.set(props.storageId, val)
    }
  },
  { deep: true },
)
</script>

<template>
  <div id="cv-group" class="cv-group h-full overflow-y-auto">
    <div class="cv-group-list">
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
    <template v-if="treeData.length === 0">
      <a-empty :image="Empty.PRESENTED_IMAGE_SIMPLE" />
    </template>
  </div>
</template>
