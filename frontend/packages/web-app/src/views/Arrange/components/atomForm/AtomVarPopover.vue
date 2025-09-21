<script setup lang="ts">
import type { TreeProps } from 'ant-design-vue'
import { Empty, Popover } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { filter, find } from 'lodash-es'
import { computed, inject, ref } from 'vue'

import type { VARIABLE_TYPE } from '@/constants/atom'
import { GLOBAL_VAR_IN_TYPE, LIMIT_VARIABLE_SELECT, PARAMETER_VAR_IN_TYPE, VAR_IN_TYPE } from '@/constants/atom'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import { useVariableStore } from '@/stores/useVariableStore'
import { GLOBAL_VAR_TYPE, ORIGIN_VAR, PARAMETER_VAR_TYPE, PROCESS_VAR_TYPE } from '@/views/Arrange/config/atom'
import type { VariableTypes } from '@/views/Arrange/types/atomForm'
import { atomScrollIntoView } from '@/views/Arrange/utils'

import type { VarTreeItem } from '../../types/flow'

import { createDom, generateValTree, varListUnique } from './hooks/useAtomVarPopover'
import VariableTreeTitle from './VariableTreeTitle.vue'

const props = defineProps({
  renderData: {
    type: Object as () => RPA.AtomDisplayItem,
    default: () => ({}),
  },
  varType: {
    type: String,
    default: '',
  },
})
// inject 变量类型
const variableType = inject<VariableTypes>('variableType', '') // 默认为空字符串，表示不限制类型
const simpleImage = Empty.PRESENTED_IMAGE_SIMPLE
let leafInputObj = {}

const { t } = useTranslation()
const variableStore = useVariableStore()
const flowStore = useFlowStore()
const processStore = useProcessStore()

/**
 * 变量类型选择限制
 * 1. 存在浏览器对象、word对象、excel对象作为输入参数的原子能力，分别只能选择对应的对象类型
 */
const isLimitSelect = computed(() =>
  LIMIT_VARIABLE_SELECT.includes(props.varType as VARIABLE_TYPE),
)

// 生成流变量
function getFlowVarTree(): VarTreeItem[] {
  const { formType: { type } } = props.renderData
  const flowVariableList = variableStore.filterCurrentVariableListByType(type)

  const filterArr = varListUnique(flowVariableList)
    .filter((item) => {
      if (!props.varType)
        return true

      if (isLimitSelect.value) {
        return item.types === props.varType
      }

      return true
    })
    .map(item => ({
      ...item,
      definition: `第${item.rowNum}行【${item.anotherName}】`,
      template: processStore.globalVarTypeList[item.types]?.template,
    }))

  return generateValTree(filterArr).reverse()
}

// 生成全局变量
function getGlobalVarTree(): VarTreeItem[] {
  const filterGlobalVarList = variableStore.globalVariableList
    .filter((item) => {
      if (!props.varType)
        return true

      const isItemLimitSelect = LIMIT_VARIABLE_SELECT.includes(item.varType as VARIABLE_TYPE)
      return isLimitSelect.value ? isItemLimitSelect : !isItemLimitSelect
    })
    .map(item => ({
      ...item,
      definition: item.varDescribe
        ? `全局变量【${item.varDescribe}】`
        : '全局变量',
    }))

  // TODO: generateValTree 耦合太严重了，应该抽离出来
  return generateValTree(filterGlobalVarList as unknown as any[])
}

// 生成配置参数
function getParameterVarTree(): VarTreeItem[] {
  return processStore.parameters.map((item) => {
    const { desc, funcList } = processStore.globalVarTypeList[item.varType]

    return {
      key: item.id,
      id: item.id,
      title: `${item.varName} (${desc})`,
      definition: item.varDescribe
        ? `配置参数【${item.varDescribe}】`
        : '配置参数',
      children: funcList.map(fn => ({
        title: `${fn.funcDesc} (${fn.resDesc})`,
        key: `${item.varName}/${fn.useSrc}`,
        isLeaf: true,
      })),
    }
  })
}

const varTypeList = [
  { label: PROCESS_VAR_TYPE, jumpable: true, type: VAR_IN_TYPE, generate: getFlowVarTree },
  { label: GLOBAL_VAR_TYPE, jumpable: false, type: GLOBAL_VAR_IN_TYPE, generate: getGlobalVarTree },
  { label: PARAMETER_VAR_TYPE, jumpable: false, type: PARAMETER_VAR_IN_TYPE, generate: getParameterVarTree },
]

const activeKey = ref<string>(
  find(varTypeList, { label: variableType })
    ? variableType
    : varTypeList[0].label,
)
const searchValue = ref<string>('')

const tabList = computed(() => {
  return find(varTypeList, { label: variableType })
    ? filter(varTypeList, { label: variableType })
    : varTypeList
})

const treeData = computed(() => {
  const generateFn = tabList.value.find(
    item => item.label === activeKey.value,
  )?.generate
  const treeDataList: VarTreeItem[] = generateFn?.() || []

  // 根据 searchValue 筛选 title
  return treeDataList.filter((item) => {
    if (!searchValue.value)
      return true

    return item.title.toLowerCase().includes(searchValue.value.toLowerCase())
  })
})

const selectedHandle: TreeProps['onSelect'] = (selectedKeys, info) => {
  const { selectedNodes, node } = info
  const activeType = varTypeList.find(item => item.label === activeKey.value)?.type

  if (selectedNodes.length < 1 || !Array.isArray(props.renderData.value) || !activeType)
    return

  let title = ''
  if (node.parent) {
    // 点击的是子节点
    const keyArr = (selectedKeys[0] as string).split('/')
    title = keyArr[1]
      .replace('@{self:self}', keyArr[0])
      .replace(/@\([^()]*\)/g, (args) => {
        const match = args.match(/\((.*?)\)/)
        const valData = leafInputObj[`@(@{${match[1]}})`]
        if (match[1].includes('str'))
          return valData
        if (valData) {
          if (!(selectedKeys[0] as string).includes('-'))
            return Number(valData) - 1
          return valData
        }
        return keyArr[1].includes('-') ? 1 : 0
      })
  }
  else {
    title = selectedNodes[0].title.split(' ')[0]
  }

  const obj = { val: title, category: activeType }

  createDom(obj, props.renderData, ORIGIN_VAR)
}

function leafInput(val: Record<string, unknown>) {
  leafInputObj = { ...leafInputObj, ...val }
}

function handleJump(id: string) {
  if (activeKey.value === PROCESS_VAR_TYPE) {
    atomScrollIntoView(id)
    flowStore.setJumpFlowId(id)
  }
}
</script>

<template>
  <a-input
    v-model:value="searchValue"
    class="atom-popover-search"
    :placeholder="t('searchVariables')"
    style="width: 230px"
  />
  <a-tabs
    v-model:active-key="activeKey"
    size="small"
    :tab-bar-gutter="18"
    class="mt-1"
  >
    <a-tab-pane
      v-for="tab in tabList"
      :key="tab.label"
      class="atom-popover-tabs"
      :tab-bar-style="{ fontSize: '12px' }"
      :tab="t(tab.label)"
    >
      <a-tree
        v-if="treeData.length > 0"
        block-node
        :tree-data="treeData"
        :height="160"
        @select="selectedHandle"
      >
        <template #title="{ title, definition, template, id }">
          <Popover placement="left" :align="{ offset: [-24, 0] }" :open="definition ? undefined : false">
            <template #content>
              <div class="flex items-center text-xs">
                定义：{{ definition }}
                <span
                  v-if="tab.jumpable"
                  class="flex items-center cursor-pointer text-primary gap-1"
                  @click="handleJump(id)"
                >
                  <rpa-icon name="jump" size="14" />
                  跳转
                </span>
              </div>
              <div v-if="template" class="text-xs">
                参考输出：{{ template }}
              </div>
            </template>
            <div class="input-box">
              <VariableTreeTitle
                :key="title"
                :title="title"
                @get-input-val="leafInput"
              />
            </div>
          </Popover>
        </template>
      </a-tree>
      <Empty v-else :image="simpleImage" :description="null" />
    </a-tab-pane>
  </a-tabs>
</template>

<style lang="scss" scoped>
.atom-popover-search {
  font-size: 12px;
}

.input-box {
  display: flex;
  align-items: center;
}

:deep(.ant-tabs-nav-list > .ant-tabs-tab) {
  font-size: 12px;
}

:deep(.ant-tree-title) {
  display: inline-flex;
  line-height: 28px;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  align-items: center;
}

:global(.ui-at) {
  display: inline-flex;
  align-items: center;
  border: 0;
  cursor: pointer;
}

:global(.ui-at::before) {
  display: inline-block;
  border-radius: 5px;
  padding: 0 5px;
  border: 1px solid #ccc;
  line-height: 18px;
  content: attr(data-name);
}

:deep(.ant-tree-list::-webkit-scrollbar) {
  width: 6px;
}
</style>
