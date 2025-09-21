<!-- @format -->
<script lang="tsx" setup>
import { MinusCircleOutlined, PlusCircleOutlined, PlusOutlined } from '@ant-design/icons-vue'
import type { ColumnsType } from 'ant-design-vue/es/table'
import { h, nextTick, provide, reactive, ref, watch } from 'vue'

import type { FormRules } from '@/types/common'
import type { AttrFieldsType, NodeFieldsType } from '@/views/Arrange/types/arrangeTools'
import type { VariableTypes } from '@/views/Arrange/types/atomForm'
import { addAttr, addNode } from '@/views/Arrange/utils/elementsUtils'

import AtomConfig from '../atomForm/AtomConfig.vue'

const props = defineProps({
  nodeSource: {
    type: Array<{
      _version?: string
      _checkDisabled?: boolean
      _addDisabled?: boolean
      _deleteDisabled?: boolean
      value: string
      checked: boolean
      tag: string
      attrs?: any[]
    }>,
    default: () => [],
  },
  nodeFields: {
    type: Object as () => NodeFieldsType,
    default: () => ({
      name: 'name',
      value: 'value',
      checked: 'checked',
    }),
  },
  attrFields: {
    type: Object as () => AttrFieldsType,
    default: () => ({
      name: 'name',
      type: 'type',
      value: 'value',
      checked: 'checked',
    }),
  },
})

const currentNodeIndex = ref(0) // 当前节点索引
const openAddNode = ref(false) // 是否打开添加节点弹窗
const addNodeFormRef = ref(null) // 添加节点表单引用
const addNodeForm = reactive({ name: '' })
const currentKey = ref('') // 当前选中的节点key

const rules = reactive<FormRules>({
  name: [{
    required: true,
    message: '请输入节点',
    trigger: 'change',
    validator: async (_rule, value) => {
      if (!value.replace(/\s+/g, '')) {
        return Promise.reject(new Error('请输入节点'))
      }
      else {
        return Promise.resolve()
      }
    },
  }],
})
provide<VariableTypes>('variableType', 'globalVariables')
// 节点行点击事件
function nodeRowClick(record, index) {
  currentNodeIndex.value = index
  props.nodeSource[currentNodeIndex.value].attrs = record.attrs
}
// 添加属性
function addAttrNode() {
  const node = props.nodeSource[currentNodeIndex.value]
  const index = props.nodeSource[currentNodeIndex.value].attrs.length
  const attr = addAttr(node._version, index)
  props.nodeSource[currentNodeIndex.value].attrs.push(attr)
  nextTick(() => {
    // 滚动到最后一行
    const dom = document.querySelector('#attrTable table tbody tr:last-child')
    dom?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  })
}
// 删除属性
function deleteNode(index) {
  props.nodeSource[currentNodeIndex.value].attrs.splice(index, 1)
}
// 属性列
function customRowFn(record, index) {
  return {
    onClick: () => {
      nodeRowClick(record, index)
    },
  }
}
// 节点class
function rowClassNameFn(record, index) {
  return index === currentNodeIndex.value ? 'bg-[#4E68F6]/[0.1]' : ''
}
// 删除属性
function confirmDeleteAttr(index) {
  deleteNode(index)
}
// 删除节点
function confirmDeleteNode(index) {
  props.nodeSource.splice(index, 1)
}
function addNodeSource(index) {
  currentNodeIndex.value = index
  openAddNode.value = true
}
function okAddNode() {
  addNodeFormRef.value.validateFields(['name']).then((valid: any) => {
    if (valid) {
      openAddNode.value = false
      const originNode = JSON.parse(JSON.stringify(props.nodeSource[currentNodeIndex.value]))
      originNode.tag = addNodeForm.name
      originNode.value = addNodeForm.name
      const node = addNode(originNode._version, originNode)
      props.nodeSource.splice(currentNodeIndex.value + 1, 0, node)
      nodeRowClick(node, currentNodeIndex.value + 1)
    }
  })
}
function cancelAddNode() {
  openAddNode.value = false
  addNodeFormRef.value.resetFields()
}
// 节点列
const nodeColumns = reactive<ColumnsType>([
  {
    title: '元素节点',
    align: 'left',
    children: [
      {
        title: '启用',
        dataIndex: 'checked',
        key: props.nodeFields.checked,
        width: 15,
        align: 'center',
      },
      {
        title: '节点',
        dataIndex: 'value',
        key: 'value',
        width: 30,
        ellipsis: true,
      },
      {
        title: '操作',
        dataIndex: 'operation',
        key: 'operation',
        width: 20,
        align: 'center',
      },
    ],
  },
])
// 属性列
const attrColumns = reactive<ColumnsType>([
  {
    title: '属性节点',
    align: 'left',
    children: [
      {
        title: '启用',
        dataIndex: 'checked',
        key: props.attrFields.checked,
        width: 15,
        align: 'center',
      },
      {
        title: '属性名',
        dataIndex: 'name',
        key: props.attrFields.name,
        width: 30,
        ellipsis: true,
      },
      {
        title: '匹配',
        dataIndex: 'type',
        key: props.attrFields.type,
        width: 40,
      },
      {
        title: '值',
        dataIndex: 'value',
        key: props.attrFields.value,
        width: 70,
        ellipsis: true,
      },
      {
        title: '操作',
        dataIndex: 'attrOper',
        key: 'attrOper',
        width: 20,
        align: 'center',
      },
    ],
  },
])

watch(() => props.nodeSource, () => {
  currentNodeIndex.value = 0 // 重置当前节点索引
  currentKey.value = Math.random().toString(36).substring(2, 15) // 更新当前key以触发attrTable重新渲染
}, { immediate: true })
</script>

<template>
  <div class="directory-table normal-border">
    <a-row>
      <a-col :span="7" class="nodeCol font-size-12 border-right">
        <a-table
          class="node-table"
          table-layout="fixed"
          :columns="nodeColumns"
          :data-source="nodeSource"
          :pagination="false"
          :custom-row="customRowFn"
          :scroll="{ y: nodeSource.length > 4 ? 170 : null }"
          :row-class-name="rowClassNameFn"
        >
          <template #bodyCell="{ column, record, index }">
            <template v-if="column.key === 'checked'">
              <a-checkbox v-model:checked="record.checked" :disabled="record._checkDisabled" />
            </template>
            <template v-else-if="column.key === 'operation'">
              <a-tooltip title="添加节点">
                <PlusCircleOutlined class="text-blue-500" @click="addNodeSource(index)" />
              </a-tooltip>
              <a-popconfirm
                title="是否删除当前节点"
                ok-text="是"
                cancel-text="否"
                @confirm="confirmDeleteNode(index)"
              >
                <MinusCircleOutlined class="text-blue-500 ml-2" />
              </a-popconfirm>
            </template>
            <template v-else>
              <input v-model="record.value" type="text" class="node-input font-size-12" :disabled="record._valueDisabled" :maxlength="32">
              <!-- <span contenteditable="true">{{ record.value }}</span> -->
            </template>
          </template>
        </a-table>
      </a-col>
      <a-col :span="17" class="nodeCol font-size-12">
        <a-table id="attrTable" :key="currentKey" class="attr-table" table-layout="fixed" :columns="attrColumns" :data-source="nodeSource[currentNodeIndex]?.attrs" :pagination="false" :scroll="{ y: 136 }">
          <template #bodyCell="{ column, record, index }">
            <template v-if="column.key === 'checked'">
              <a-checkbox v-model:checked="record.checked" :disabled="record._checkDisabled" />
            </template>
            <template v-else-if="column.key === 'name'">
              <a-input v-model:value="record.name" class="attr-input font-size-12" :disabled="record._nameDisabled" :maxlength="64" />
            </template>
            <template v-else-if="column.key === 'type'">
              <a-select v-model:value="record.type" class="attr-select  font-size-12" :disabled="record._typeDisabled">
                <a-select-option v-for="item in record._typesPattern" :key="item.value" class="font-size-12" :value="item.value">
                  {{ item.label }}
                </a-select-option>
              </a-select>
            </template>
            <template v-else-if="column.key === 'value'">
              <a-tooltip v-if="record.type === 2" title="支持JavaScript new RegExp(your code string)表达式">
                <AtomConfig :key="`${currentNodeIndex}${index}`" class="font-size-12" :form-item="record.variableValue" />
              </a-tooltip>
              <AtomConfig v-else :key="`${currentNodeIndex}${index}`" class="font-size-12" :form-item="record.variableValue" />
            </template>
            <template v-else-if="column.key === 'attrOper'">
              <a-popconfirm
                title="是否删除当前节点"
                ok-text="是"
                cancel-text="否"
                @confirm="confirmDeleteAttr(index)"
              >
                <MinusCircleOutlined style="color: #4E68F6;" />
              </a-popconfirm>
            </template>
            <template v-else>
              <span>{{ record.value }}</span>
            </template>
          </template>
        </a-table>
        <a-button type="text" class=" add-attr flex items-center justify-center font-size-12" size="small" :icon="h(PlusOutlined)" @click="addAttrNode">
          添加属性
        </a-button>
      </a-col>
    </a-row>
    <a-modal v-model:open="openAddNode" :width="400" :height="160" title="添加节点" ok-text="确认" cancel-text="取消" @ok="okAddNode" @cancel="cancelAddNode">
      <a-form ref="addNodeFormRef" :model="addNodeForm" :rules="rules">
        <a-form-item label="元素节点" :label-col="{ span: 6 }" :wrapper-col="{ span: 18 }" name="name">
          <a-input v-model:value="addNodeForm.name" placeholder="请输入节点" :maxlength="64" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<style lang="scss" scoped>
.directory-table {
  :deep(.ant-table-wrapper .ant-table-container .ant-table-body::-webkit-scrollbar) {
    width: 6px;
    background-color: #f5f5f5;
  }

  :deep(.ant-table-wrapper .ant-table-container .ant-table-body::-webkit-scrollbar-thumb) {
    background-color: #cecece;
  }

  :deep(.form-item-container .editor-container) {
    margin: 2px 0px;
    padding: 4px;
  }

  :deep(.editor) {
    max-height: 88px;
    overflow-y: auto;
  }

  :deep(.ant-select-single .ant-select-selector .ant-select-selection-item) {
    font-size: 12px;
  }
}

.font-size-12 {
  font-size: 12px;
}

.nodeCol {
  max-height: 228px;
  height: 228px;
  overflow: hidden;
}
.attr-table {
  height: 194px;
}

.border-right {
  border-right: 1px solid $color-border;
}

.node-input {
  width: 100%;
  display: inline-block;
  height: 28px;
  outline: none;
  padding: 0px 4px;
  background: transparent;
}

.node-input:focus {
  border-bottom: 1px solid #4e68f6;
}

.attr-input {
  height: 28px;
}

.attr-select {
  height: 28px;
  width: 90%;

  :deep(.ant-select-selector) {
    height: 28px;
  }
}

.add-attr {
  position: absolute;
  bottom: 4px;
  left: 10px;
}

:deep(.ant-table-wrapper .ant-table-thead > tr > th),
:deep(.ant-table-thead > tr > th) {
  font-weight: 600;
}

:deep(.ant-table-wrapper .ant-table-thead > tr > th),
:deep(.ant-table-thead > tr > th),
:deep(.ant-table-tbody > tr > td) {
  padding: 5px 3px;
  font-size: 12px;
  // color: rgb(29, 29, 29);
}

:deep(.ant-table-row-cell-hover) {
  background: rgb(78, 104, 246, 0.05);
}

:deep(.ant-table-wrapper .ant-table-tbody > tr.ant-table-row:hover > td) {
  background: rgb(78, 104, 246, 0.05);
}
</style>
