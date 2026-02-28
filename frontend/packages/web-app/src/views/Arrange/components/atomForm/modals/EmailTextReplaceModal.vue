<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { message } from 'ant-design-vue'
import type { ColumnsType } from 'ant-design-vue/es/table'
import { useTranslation } from 'i18next-vue'
import { cloneDeep } from 'lodash-es'
import { nanoid } from 'nanoid'
import type { UnwrapRef } from 'vue'
import { reactive, ref } from 'vue'

import AtomConfig from '../AtomConfig.vue'
import { getRealValue } from '../hooks/usePreview'

const props = defineProps<{ option: string }>()
const emits = defineEmits(['ok'])

const modal = NiceModal.useModal()
const { t } = useTranslation()

interface DataItem {
  id: string
  origintext: RPA.AtomDisplayItem
  replacetext: RPA.AtomDisplayItem
}

const columns: ColumnsType = [{
  title: t('emailTextReplace.originText'),
  dataIndex: 'origintext',
  key: 'origintext',
  ellipsis: true,
}, {
  title: t('emailTextReplace.replaceText'),
  key: 'replacetext',
  dataIndex: 'replacetext',
  ellipsis: true,
}, {
  title: t('operate'),
  key: 'operation',
  dataIndex: 'operation',
  width: 100,
  ellipsis: true,
}]
const dataSource = ref(tranformToFront(JSON.parse(props.option || '[]')) as DataItem[])
// console.log('dataSource', dataSource.value)
const editingKey = ref('') // 当前正在编辑的行

// 转换成前端需要的数据结构
function tranformToFront(paramsArray) {
  // console.log('tranformToFront', paramsArray)
  return paramsArray.map(item => ({
    id: nanoid(),
    origintext: {
      formType: { type: 'INPUT_VARIABLE' },
      key: nanoid(),
      title: '',
      value: item.origintext.value,
    },
    replacetext: {
      formType: { type: 'INPUT_VARIABLE' },
      key: nanoid(),
      title: '',
      value: item.replacetext.value,
    },
  }))
}

// 转换成后端需要的数据结构
function tranformToEnd(paramsData) {
  const res = paramsData.map((item: DataItem) => ({
    origintext: {
      rpa: 'special',
      value: item.origintext.value,
    },
    replacetext: {
      rpa: 'special',
      value: item.replacetext.value,
    },
  }))
  // console.log('tranformToEnd', res)
  return res
}

function handleOk() {
  emits('ok', JSON.stringify(tranformToEnd(dataSource.value)))
  modal.hide()
}

const editableData: UnwrapRef<Record<string, DataItem>> = reactive({})

function edit(key: string) {
  editableData[key] = cloneDeep(dataSource.value.filter(item => key === item.id)[0])
  editingKey.value = key
}

function save(key: string) {
  // 检测当前保存的这一行替换规则是否重复或者为空
  const editOrignText = getRealValue(editableData[key].origintext.value)
  const idx = dataSource.value.findIndex(item => getRealValue(item.origintext.value) === editOrignText && item.id !== key)
  if (idx !== -1 || !editOrignText) {
    message.warning(t('emailTextReplace.duplicateOrEmpty'))
    return
  }
  Object.assign(dataSource.value.filter(item => key === item.id)[0], editableData[key])
  delete editableData[key]
  editingKey.value = ''
}

function onDelete(key: string) {
  dataSource.value = dataSource.value.filter(item => item.id !== key)
  editingKey.value === key && (editingKey.value = '')
}

function handleAdd() {
  if (editingKey.value) {
    message.warning(t('emailTextReplace.saveCurrentFirst'))
    return
  }
  const newKey = nanoid()
  const inputConfig = {
    formType: { type: 'INPUT_VARIABLE' },
    title: '',
    value: [{
      type: 'other',
      value: '',
    }],
  }
  const newData: DataItem = {
    id: newKey,
    origintext: {
      ...JSON.parse(JSON.stringify(inputConfig)),
      key: nanoid(),
    },
    replacetext: {
      ...JSON.parse(JSON.stringify(inputConfig)),
      key: nanoid(),
    },
  }
  dataSource.value.unshift(newData)
  // 新增行自动处于编辑态
  editableData[newKey] = cloneDeep(dataSource.value.filter(item => newKey === item.id)[0])
  editingKey.value = newKey
};
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="$t('emailTextReplace.title')"
    class="email-text-replace-modal"
    :width="800"
    centered
    @ok="handleOk"
  >
    <a-button type="primary" @click="handleAdd">
      {{ $t('emailTextReplace.addRule') }}
    </a-button>
    <a-table
      class="editable-table"
      :columns="columns"
      :data-source="dataSource"
      size="small"
      bordered
      :scroll="{ y: 220 }"
      :pagination="{
        pageSize: 15,
        size: 'small',
        disabled: editingKey !== '',
        showTotal: () => t('emailTextReplace.recordTotal', { count: dataSource.length }),
      }"
    >
      <template #bodyCell="{ column, text, record }">
        <template v-if="['origintext', 'replacetext'].includes(column.dataIndex as string)">
          <div>
            <AtomConfig v-if="editableData[record.id]" :form-item="editableData[record.id][column.dataIndex as string]" />
            <template v-else>
              <span v-for="item in text?.value" :key="item?.value">
                <span v-if="item?.type === 'var'">
                  <hr class="dialog-tag-input-hr" :data-name="item?.value">
                </span>
                <span v-else>
                  {{ item.value }}
                </span>
              </span>
            </template>
          </div>
        </template>
        <template v-else-if="column.dataIndex === 'operation'">
          <div class="editable-row-operations">
            <span v-if="editableData[record.id]">
              <a-typography-link @click="save(record.id)">{{ $t('save') }}</a-typography-link>
              <a-popconfirm :title="$t('deleteConfirmTip')" @confirm="onDelete(record.id)">
                <a>{{ $t('delete') }}</a>
              </a-popconfirm>
            </span>
            <span v-else>
              <a :style="`${editingKey !== record.id && editingKey !== '' ? 'opacity: 0.2; pointer-events: none;' : ''}`" @click="edit(record.id)">{{ $t('edit') }}</a>
              <a-popconfirm :title="$t('deleteConfirmTip')" @confirm="onDelete(record.id)">
                <a>{{ $t('delete') }}</a>
              </a-popconfirm>
            </span>
          </div>
        </template>
      </template>
    </a-table>
  </a-modal>
</template>

<style lang="scss">
.editable-row-operations a {
  margin-right: 8px;
}
.email-text-replace-modal {
  .editable-table {
    height: 300px;
    margin: 10px 0;
  }
}
</style>
