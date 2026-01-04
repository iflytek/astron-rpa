<script setup lang="ts">
import { NiceModal, useTheme } from '@rpa/components'
import { useElementSize, watchDebounced } from '@vueuse/core'
import type { TreeProps } from 'ant-design-vue'
import { Empty, message, Skeleton } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { cloneDeep, throttle } from 'lodash-es'
import { computed, onBeforeMount, ref, shallowRef, useTemplateRef } from 'vue'
import draggable from 'vuedraggable'

import { getParentNodes } from '@/utils/common'
import { COMPONENT_KEY_PREFIX, isComponentKey } from '@/utils/customComponent'

import { addFavorite, removeFavorite } from '@/api/atom'
import { ComponentManageModal } from '@/components/ComponentManage'
import { useProcessStore } from '@/stores/useProcessStore'
import { addAtomData, draggableAddStyle } from '@/views/Arrange/components/flow/hooks/useFlow'
import type { ATOMTABKEYS } from '@/views/Arrange/config/atom'

import AtomMenu from './AtomMenu.vue'
import AtomTree from './AtomTree.vue'
import CompDetail from './CompDetail.vue'
import UseAtomItem from './useAtomItem.vue'
import type { AtomTreeNode } from './utils'
import { addUniqueIdsToTree, searchTreeAndKeepStructure } from './utils'

const props = defineProps<{
  collapse: boolean
  isPopover?: boolean
}>()

const emit = defineEmits<{
  (evt: 'collapse-left', e: boolean): void
  (evt: 'change-trigger', e: 'hover' | 'click'): void
}>()

const { colorTheme } = useTheme()
const processStore = useProcessStore()
const panel = useTemplateRef('panel')
const panelHeight = useElementSize(panel).height
const popoverTrigger = ref<'hover' | 'click'>('hover')
const { t } = useTranslation()

const isShowTree = computed(() => !props.collapse)
let preExpandedKeys: (string | number)[] = []
const expandedKeys = ref<(string | number)[]>([])
const searchAtom = ref<string>('')
const treeData = shallowRef<AtomTreeNode[]>([])

const collapsed = ref(false) // 展开所有节点
const menuKey = ref<ATOMTABKEYS>('BASE_ATOM')

const fullTreeData = computed<AtomTreeNode[]>(() => {
  let list: RPA.AtomTreeNode[] = []

  switch (menuKey.value) {
    case 'BASE_ATOM': {
      const favorite: RPA.AtomTreeNode = {
        key: 'favorite',
        title: t('myFavorites'),
        icon: 'atom-favorite',
        iconColor: '#F39D09',
        atomics: processStore.favorite.state,
      }
      list = [favorite, ...processStore.atomicTreeData]
      break
    }
    case 'EXT_ATOM': {
      const customComps = {
        key: 'customComponent',
        title: t('components.customComponent'),
        atomics: processStore.componentTree.state.map(item => ({
          key: `${COMPONENT_KEY_PREFIX}.${item.componentId}`,
          title: item.name,
          icon: item.icon,
          componentId: item.componentId,
          dot: item.isLatest === 0,
        })),
      }
      const businessComps = {
        key: 'businessComponent',
        title: t('businessComponent'),
        atomics: processStore.extendTree.state,
      }
      list = processStore.isComponent ? [businessComps] : [customComps, businessComps]
      break
    }
  }

  // 由于 list 中会存在重复的 key，因此需要给每个节点添加一个唯一的 id，通过路径的 key 来生成
  return list.map(node => addUniqueIdsToTree(node))
})

watchDebounced([searchAtom, fullTreeData], ([searchKey, treeList], [oldSearchKey]) => {
  let list: AtomTreeNode[] = cloneDeep(treeList)

  /**
   * 为了能在搜索时保留展开的节点状态，需要记录一下之前的展开节点状态，
   * 搜索结束时，将之前的展开节点状态赋值给 expandedKeys
   */
  // 开始搜索时
  if (!oldSearchKey && searchKey) {
    preExpandedKeys = expandedKeys.value
  }

  // 搜索结束时
  if (oldSearchKey && !searchKey) {
    expandedKeys.value = preExpandedKeys
  }

  if (searchKey) {
    [list, expandedKeys.value] = searchTreeAndKeepStructure(list, searchKey)
  }

  treeData.value = list
}, { debounce: 200, immediate: true })

const loading = computed(() => {
  switch (menuKey.value) {
    case 'BASE_ATOM':
      return processStore.atomMeta.isLoading
    case 'EXT_ATOM':
      return processStore.extendTree.isLoading
  }

  return false
})

function toggleCollapsed() {
  collapsed.value = !collapsed.value

  if (collapsed.value) {
    expandedKeys.value = getParentNodes(treeData.value)
  }
  else {
    expandedKeys.value = []
  }
}

const onExpand: TreeProps['onExpand'] = (_, { expanded, node }) => {
  if (expanded) {
    console.log('node: ', node)
    // useProjectDocStore().gainLastNodeAbility(node.key as unknown as string)
  }
}

const selectedClick: TreeProps['onSelect'] = (_, { node }) => {
  const { eventKey } = node

  if (expandedKeys.value.includes(eventKey)) {
    expandedKeys.value = expandedKeys.value.filter(key => key !== eventKey)
  }
  else {
    expandedKeys.value = [...expandedKeys.value, eventKey]
  }
}

function getLikeId(atom: AtomTreeNode) {
  return processStore.favorite.state.find(item => item.key === atom.key)?.likeId
}

// 添加收藏
const addfavorite = throttle(async (item: TreeProps['treeData'][number]) => {
  const { key } = item.data
  await addFavorite({ atomKey: key })
  message.success(t('common.collectSuccess'))
  // 刷新列表
  processStore.favorite.execute()
}, 1500, { leading: true, trailing: false })

// 取消收藏
async function removefavorite(likeId) {
  await removeFavorite({ likeId })
  message.success(t('common.cancelCollectSuccess'))
  // 刷新列表
  processStore.favorite.execute()
}

// 打开组件管理弹窗
function openComponentManageModal() {
  NiceModal.show(ComponentManageModal, { robotId: processStore.project.id })
}

// 刷新自定义组件
function refreshComponentTree() {
  processStore.componentTree.execute()
}

onBeforeMount(() => {
  processStore.atomMeta.execute()
  processStore.favorite.execute()
  processStore.extendTree.execute()
  processStore.componentTree.execute()
})
</script>

<template>
  <section ref="panel" class="atom-tree relative bg-[#FFFFFF] dark:bg-[#FFFFFF]/[.04] rounded-md">
    <section class="atom-tree-header" :class="{ '!px-2': !isShowTree }">
      <a-input
        v-show="isShowTree"
        v-model:value="searchAtom"
        :placeholder="$t('common.enter')"
        allow-clear
        class="flex-1 leading-6 py-1"
        @compositionstart="emit('change-trigger', 'click')"
        @compositionend="emit('change-trigger', 'hover')"
      >
        <template #prefix>
          <rpa-icon name="search" />
        </template>
      </a-input>
      <!-- 展开/折叠树节点 -->
      <rpa-hint-icon
        v-show="isShowTree"
        name="tree-expand"
        :title="collapsed ? $t('common.foldTree') : $t('common.expandTree')"
        :class="[isPopover ? 'ml-[6px]' : 'mx-[6px]']"
        enable-hover-bg
        @click="() => toggleCollapsed()"
      />
      <template v-if="!isPopover">
        <!-- 展开左侧面板 -->
        <a-popover :trigger="popoverTrigger" placement="bottomLeft" overlay-class-name="custom-popover-overlay">
          <template #content>
            <AtomTree
              :collapse="false"
              :style="{ height: `${panelHeight - 35}px` }"
              class="w-[240px]"
              is-popover
              @change-trigger="(trigger) => popoverTrigger = trigger"
            />
          </template>
          <rpa-hint-icon
            v-show="!isShowTree"
            name="navigate-expand"
            :title="$t('common.expand')"
            enable-hover-bg
            @click="emit('collapse-left', !collapse)"
          />
        </a-popover>
        <!-- 收起左侧面板 -->
        <rpa-hint-icon
          v-show="isShowTree"
          name="navigate-collapse"
          :title="$t('common.collapse')"
          enable-hover-bg
          @click="emit('collapse-left', !collapse)"
        />
      </template>
    </section>
    <AtomMenu v-show="isShowTree" v-model:value="menuKey" />
    <a-button
      v-show="!processStore.isComponent && isShowTree && menuKey === 'EXT_ATOM'"
      class="mx-3 h-[32px] flex justify-center items-center gap-2"
      @click="openComponentManageModal"
    >
      <rpa-icon name="component-manage" size="16" />
      <span>{{ $t('moduleManagement') }}</span>
    </a-button>
    <div v-show="isShowTree" class="atom-tree-container">
      <Skeleton v-if="loading" :paragraph="{ rows: 8 }" active class="mx-2" />
      <a-tree
        v-else-if="treeData.length > 0"
        v-model:expanded-keys="expandedKeys"
        :class="[colorTheme]"
        class="forbid flex-1 !overflow-x-hidden"
        block-node
        :tree-data="treeData"
        :field-names="{ children: 'atomics', key: 'uniqueId' }"
        @select="selectedClick"
        @expand="onExpand"
      >
        <template #title="item">
          <UseAtomItem
            v-if="item.atomics?.length > 0 || item.key === 'favorite' || item.key === 'customComponent'"
            :title="item.title"
            :icon="item.icon"
            :icon-color="item.iconColor"
            :dot="item.dot"
            :search-atom="searchAtom"
          />
          <draggable
            v-else
            :item-key="item.key"
            :list="[item]"
            :group="{ name: 'postTree', pull: 'clone', put: false }"
            :sort="false"
            filter=".forbid"
            tag="span"
            class="treeTitle"
            fallback-class="flow-list-item"
            @move="draggableAddStyle"
          >
            <template #item="">
              <div
                class="tree-node flex items-center px-2 hover:bg-[#5D59FF]/[.35] rounded"
                @dblclick="() => addAtomData(item.key)"
              >
                <UseAtomItem
                  :title="item.title"
                  :icon="item.icon"
                  :icon-color="item.iconColor"
                  :dot="item.dot"
                  :search-atom="searchAtom"
                />
                <div class="tree-node-action">
                  <CompDetail
                    v-if="isComponentKey(item.key)"
                    :robot-id="processStore.project.id"
                    :component-id="item.componentId"
                    @refresh="refreshComponentTree"
                  >
                    <rpa-hint-icon
                      name="component-manage"
                      :title="$t('moduleManagement')"
                      enable-hover-bg
                      class="!p-[2px]"
                    />
                  </CompDetail>
                  <template v-if="menuKey === 'BASE_ATOM'">
                    <rpa-hint-icon
                      v-if="getLikeId(item)"
                      name="atom-favorite"
                      :title="$t('common.cancelCollect')"
                      enable-hover-bg
                      class="!p-[2px] text-[#F39D09]"
                      @click="() => removefavorite(getLikeId(item))"
                    />
                    <rpa-hint-icon
                      v-else
                      name="atom-favorite-outline"
                      :title="$t('common.collect')"
                      enable-hover-bg
                      class="!p-[2px]"
                      @click="() => addfavorite(item)"
                    />
                  </template>
                </div>
              </div>
            </template>
          </draggable>
        </template>
      </a-tree>
      <div v-else class="flex w-full h-full items-center justify-center">
        <a-empty :image="Empty.PRESENTED_IMAGE_SIMPLE" />
      </div>
    </div>
  </section>
</template>

<style lang="scss" scoped>
@import './atomTree.scss';

.tree-node {
  .tree-node-action {
    display: none;
  }

  &:hover {
    .tree-node-action {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 4px;
    }
  }
}

:deep(.ant-tree-node-content-wrapper) {
  overflow: hidden;
}

:deep(.ant-tree) {
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
</style>

<style>
.custom-popover-overlay {
  padding-top: 0 !important;

  .ant-popover-inner {
    padding: 0;
  }

  .ant-popover-arrow {
    display: none;
  }
}
</style>
