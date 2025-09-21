<script lang="ts" setup>
import { HintIcon, Icon } from '@rpa/components'
import type { TreeProps } from 'ant-design-vue'
import { Empty } from 'ant-design-vue'
import type { Ref } from 'vue'
import { computed, h, inject, onMounted, ref, watch } from 'vue'

import { scrollToName } from '@/utils/domUtils'
import { LRUCache } from '@/utils/lruCache'

import ElementMenu from '@/components/ElementItemAction/elementMenu.vue'
import { ELEMENTS_TREE_EXPANDE_KEYS } from '@/constants'
import { useElementsStore } from '@/stores/useElementsStore'
import type { ElementsType } from '@/types/resource.d'
import { useGlobalDataUpdate } from '@/views/Arrange/hook/useGlobalDataUpdate'
import { filterActionData } from '@/views/Arrange/utils/elementsUtils'

import ElementGroupContextmenu from '../ElementGroupContextmenu/Index.vue'
import ElementItemAction from '../ElementItemAction/Index.vue'

const { storageId, disabledContextmenu, itemChosed, searchVal, expandAll, checkUnused, parent } = defineProps({
  storageId: String,
  disabledContextmenu: {
    type: Boolean,
    default: true,
  },
  itemChosed: {
    type: String,
    default: '',
  },
  searchVal: {
    type: String,
    default: '',
  },
  expandAll: {
    type: Boolean,
    default: false,
  },
  checkUnused: {
    type: Boolean,
    default: false,
  },
  parent: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['edit', 'delete', 'selected', 'lookOver', 'rename', 'repick', 'contextmenu', 'actionClick'])

const expandedKeyLRUCache = new LRUCache<string[]>(ELEMENTS_TREE_EXPANDE_KEYS, 10, [])

const useElements = useElementsStore()
const useGlobalData = useGlobalDataUpdate()
const flatElementData = computed(() => useElements.convertTreeToFlat(useElements.elements))
const autoExpandParent = ref(false)
const selectedKeys = ref([])
const expandedKeys = ref([])
const searchText = computed(() => searchVal)
const isExpandAll = computed(() => expandAll)
const searchData = computed(() => {
  if (!searchVal)
    return []// 没有搜索值则不处理
  const searchList = []
  useElements.elements.forEach((item) => {
    // 不区分大小写
    const lowcaseVal = searchVal.toLowerCase()
    const lowcaseName = item.name.toLowerCase().replace(/[\u200B-\u200D\uFEFF]/g, '')
    if (lowcaseName.includes(lowcaseVal)) {
      searchList.push(item)
    }
    if (item.elements && item.elements.length > 0) {
      const inList = searchList.some(searchItem => searchItem.name === item.name)
      const children = item.elements.filter((child) => {
        const lowcaseChildName = child.name.toLowerCase().replace(/[\u200B-\u200D\uFEFF]/g, '')
        return lowcaseChildName.includes(lowcaseVal)
      })
      if (children.length > 0 && !inList) {
        searchList.push({
          ...item,
          elements: children,
        })
      }
    }
  })
  return searchList
})
const unused = computed(() => checkUnused)
const unusedData = ref([])
const fieldNames: TreeProps['fieldNames'] = {
  title: 'name',
  key: 'name',
  children: 'elements',
}

const unUseNum = inject<Ref<number>>('unUseNum', ref(0))
const refresh = inject<Ref<boolean>>('refresh', ref(false))
const activeTab = inject<Ref<string>>('activeTab', ref(''))
const refreshValue = computed(() => refresh?.value)
const groupData = computed(() => {
  const group = useElements.elements.map((item) => {
    return {
      key: item.id,
      name: item.name,
      label: item.name,
      id: item.id,
    }
  })
  return group
})

const menuData = computed(() => {
  if (parent === 'elementChooser') {
    return [
      {
        key: 'more',
        label: '',
        type: 'dropdownMenus',
        icon: h(HintIcon, { name: 'ellipsis', enableHoverBg: true }),
        menus: [
          {
            key: 'delete',
            label: '删除元素',
            icon: h(Icon, { name: 'bottom-pick-menu-del', width: '16px', height: '16px' }),
          },
        ],
      },
    ]
  }
  else {
    return [
      {
        key: 'more',
        label: '',
        type: 'dropdownMenus',
        icon: h(Icon, { name: 'ellipsis' }),
        menus: [
          {
            key: 'quoted',
            label: '查找引用',
            icon: h(Icon, { name: 'bottom-pick-menu-search', width: '16px', height: '16px' }),
          },
          {
            key: 'move',
            label: '移动至',
            icon: h(Icon, { name: 'bottom-pick-menu-move', width: '16px', height: '16px' }),
            children: groupData.value.map((i) => {
              i.label = i.name
              i.key = i.id
              return i
            }),
          },
          {
            key: 'copy',
            label: '创建副本',
            icon: h(Icon, { name: 'bottom-pick-menu-create', width: '16px', height: '16px' }),
          },
          {
            key: 'repick',
            label: '重新拾取',
            icon: h(Icon, { name: 'bottom-pick-menu-repick', width: '16px', height: '16px' }),
          },
          {
            key: 'copy-references',
            label: '复制引用代码',
            icon: h(Icon, { name: 'bottom-pick-menu-copy', width: '16px', height: '16px' }),
          },
          {
            key: 'delete',
            label: '删除元素',
            icon: h(Icon, { name: 'bottom-pick-menu-del', width: '16px', height: '16px' }),
          },
        ],
      },
    ]
  }
})

const configData = computed(() => filterActionData(menuData.value, ['edit', 'quoted', 'move', 'delete', 'copy', 'repick']))

function handleSelect(keys: any, info: any) {
  if (info.node.dataRef.elements)
    return
  emit('selected', info.node.dataRef)
  emit('lookOver', info.node.dataRef)
}

function handleMouseenter(e: MouseEvent, data: ElementsType) {
  e.stopPropagation()
  if (data.elements)
    return
  if (selectedKeys.value.length === 0)
    emit('lookOver', data)
}

function editElement(data: ElementsType) {
  emit('edit', data)
}

function dblClickElement(data: ElementsType) {
  if (data.elements)
    return
  editElement(data)
}

function contextmenu(key: string, data: ElementsType) {
  emit('contextmenu', { key, data })
}
function actionClick(actions: Array<string>, data: ElementsType) {
  emit('actionClick', { keys: actions, data })
}

// 根据元素展开tree分组
function expandedInit(val: string) {
  let expanded: string[] = []

  if (val) {
    useElements.elements.forEach((item) => {
      const lowcaseVal = val.toLowerCase()
      const lowcaseName = item.name.toLowerCase().replace(/[\u200B-\u200D\uFEFF]/g, '')
      if (lowcaseName.includes(lowcaseVal)) {
        expanded.push(item.name)
      }
      if (item.elements && item.elements.length > 0) {
        const children = item.elements.filter((child) => {
          const lowcaseChildName = child.name.toLowerCase().replace(/[\u200B-\u200D\uFEFF]/g, '')
          return lowcaseChildName.includes(lowcaseVal)
        })
        const hasKey = expandedKeys.value.includes(item.name)
        if (children && !hasKey) {
          expanded.push(item.name)
        }
      }
    })

    selectedKeys.value = [val]
  }
  else if (storageId) {
    expanded = expandedKeyLRUCache.get(storageId)
  }

  expandedKeys.value = expanded
}

// 滚动到 name 项
function scrollInto(name: string) {
  const isExist = flatElementData.value.some(item => item.name === name)
  if (!isExist)
    return // 不存在, 默认则不需要滚动
  scrollToName(name)
}
// 得到treeData, 搜索和全部是分开的数据源
function getTreeData() {
  if (searchVal) {
    return searchData.value
  }
  if (checkUnused) {
    return unusedData.value
  }
  return useElements.elements
}
// 打开所有tree
function expandAllTree(isExpand: boolean) {
  if (isExpand) {
    expandedKeys.value = useElements.elements.map(item => item.name)
  }
  else {
    expandedKeys.value = []
  }
}

function refreshUnused() {
  const unusedList = []
  let unusedLength = 0
  useGlobalData.elementUsedInFlow().then((usedIds: string[]) => {
    useElements.elements.forEach((item) => {
      const eles = item.elements?.filter(ele => !usedIds.includes(ele.id))
      if (eles && eles.length > 0) {
        unusedLength += eles.length
        unusedList.push({ ...item, elements: eles })
      }
    })
    unusedData.value = unusedList
    unUseNum.value = unusedLength
  })
}

// 监听 搜索词
watch(searchText, (val) => {
  if (val) {
    autoExpandParent.value = true
    expandedInit(val)
  }
  else {
    autoExpandParent.value = false
    expandedKeys.value = []
    selectedKeys.value = []
  }
})
// 监听展开
watch(isExpandAll, (val) => {
  expandAllTree(val)
})

// 监听未使用
watch(unused, (val) => {
  val && refreshUnused()
})

watch(() => refreshValue.value, () => {
  if (activeTab.value === 'elements') {
    refreshUnused()
  }
})

// 监听 expandedKeys 变化，保存到 localStorage
watch(expandedKeys, (val) => {
  if (storageId) {
    expandedKeyLRUCache.set(storageId, val)
  }
}, { deep: true })

onMounted(() => {
  expandedInit(itemChosed)
  scrollInto(itemChosed)
})
</script>

<template>
  <a-tree
    v-if="useElements.elements.length"
    v-model:expanded-keys="expandedKeys"
    v-model:selected-keys="selectedKeys"
    class="w-full element-tree"
    :tree-data="getTreeData()"
    :field-names="fieldNames"
    :block-node="true"
    :open-animation="null"
    @select="handleSelect"
  >
    <template #title="{ data }">
      <section class="element-item px-1 leading-7 w-full flex items-center" :name="itemChosed ? data.name : ''">
        <div v-if="data.elements" class="element-group w-full">
          <ElementGroupContextmenu class="element-group-attr flex gap-1" pick-type="element" :disabled="disabledContextmenu" @contextmenu="(key) => contextmenu(key, data)">
            <template #content>
              <div class="element-icon flex items-center">
                <img v-if="data.icon" :src="data.icon" alt="">
                <rpa-icon v-else size="16" name="folder" />
              </div>
              <div class="element-title relative bottom-[2px]" @mouseenter="(e) => handleMouseenter(e, data)">
                {{ data.name || data.id }}
              </div>
            </template>
          </ElementGroupContextmenu>
        </div>
        <a-dropdown v-else :trigger="['contextmenu']">
          <template #overlay>
            <ElementMenu :selectd-id="data.groupId" :menus="configData[0].menus" @key-path="(keys) => actionClick(keys, data)" />
          </template>
          <div class="element-attr w-full flex items-center gap-1" @dblclick="() => dblClickElement(data)">
            <div class="element-icon flex items-center">
              <img v-if="data.icon" :src="data.icon" alt="">
              <rpa-icon v-else name="file" size="16" />
            </div>
            <div class="element-title opacity-90 h-7 text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]" @mouseenter="(e) => handleMouseenter(e, data)">
              {{ data.name }}
            </div>
            <div class="edit-btns flex items-center ml-auto">
              <rpa-hint-icon
                name="projedit"
                :title="$t('edit')"
                size="14"
                enable-hover-bg
                class="mr-1 h-min"
                @click.stop="() => editElement(data)"
              />
              <ElementItemAction
                :config-data="configData"
                :active-dropdown-menu-item-id="data.groupId"
                @click-menu="(keys) => actionClick(keys, data)"
              />
            </div>
          </div>
        </a-dropdown>
      </section>
    </template>
  </a-tree>
  <a-empty v-else :image="Empty.PRESENTED_IMAGE_SIMPLE" :description="$t('noData')" />
  <a-empty v-if="searchVal && searchData.length === 0" description="未查找到相关元素" />
</template>

<style lang="scss">
.element-tree {
  background-color: transparent;

  .ant-tree-switcher-icon {
    position: relative;
    top: -3px;
  }

  .ant-tree-node-content-wrapper {
    width: calc(100% - 60px);
    &:hover {
      opacity: 0.9;
      background: rgba(93, 89, 255, 0.35);
    }
  }

  .element-item {
    .element-title {
      width: 100%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .element-icon {
      img {
        width: 14px;
        height: 14px;
        display: block;
      }

      .folder {
        font-size: 13px;
      }
    }

    .element-group-contextmenu {
      flex: 1;
    }
  }

  .element-item .edit-btns {
    display: none;
  }

  .element-item:hover {
    .edit-btns {
      display: flex;
    }
  }

  .element-item .edit-btns {
    position: relative;
    height: 28px;
  }
}
</style>
