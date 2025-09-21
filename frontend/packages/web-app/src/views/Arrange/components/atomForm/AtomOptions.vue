<script setup lang="ts">
import { message } from 'ant-design-vue'
import { cloneDeep } from 'lodash-es'
import { nanoid } from 'nanoid'
import { ref, watch } from 'vue'
import draggable from 'vuedraggable'

import GlobalModal from '@/components/GlobalModal/index.ts'
import { getRealValue } from '@/views/Arrange/components/atomForm/hooks/usePreview'

import AtomConfig from './AtomConfig.vue'

const { renderData } = defineProps({
  renderData: {
    type: Object as () => RPA.AtomDisplayItem,
    default: () => ({}),
  },
})
const emits = defineEmits(['refresh'])
const MAX_OPTION_LENGTH = 30
const ADD_OPTION = cloneDeep(renderData)

const optionsList = ref([])

watch(() => optionsList.value, (val) => {
  const valList = val.map(item => item.value)
  // const oneOption = {
  //   rId: nanoid(),
  //   value: {
  //     rpa: 'special',
  //     value: [
  //       { type: 'other', value: '选项1' },
  //       { type: 'var', value: 'result_button_1' },
  //     ]
  //   },
  // }
  if (checkValidate(valList, false)) {
    const optionResArr = val.map((item) => {
      return {
        rId: item.rId,
        value: {
          rpa: 'special',
          value: item.value,
        },
      }
    })
    emits('refresh', optionResArr)
  }
}, { deep: true })
function initData() {
  if (Array.isArray(renderData.value)) {
    !renderData.value?.length
      ? optionsList.value.push({
          ...ADD_OPTION,
          rId: nanoid(),
          key: `options${Date.now()}`,
          value: [{ type: 'other', value: '选项1' }],
          formType: {
            type: 'INPUT_VARIABLE',
          },
        })
      : renderData.value.forEach((val, index) => {
          optionsList.value.push({
            ...ADD_OPTION,
            key: `options${index}`,
            rId: val.rId,
            value: val.value.value,
            formType: {
              type: 'INPUT_VARIABLE',
            },
          })
        })
  }
}
initData()
function checkValidate(valList, showMessage = true) {
  function checkEmpty() {
    const flagIdx = valList.findIndex(val => getRealValue(val) === '')
    if (flagIdx !== -1 && showMessage) {
      message.warning('存在为空选项请修改')
    }
    return flagIdx === -1 // true 表示没有空值
  }
  function checkUnique() {
    let flag = true // 默认不重复
    const map = {}
    valList.forEach((val) => {
      const realVal = getRealValue(val)
      map[realVal] = (map[realVal] || 0) + 1
      if (map[realVal] > 1) {
        showMessage && message.warning(`存在重复值：${realVal}，请修改`)
        flag = false
        return false
      }
    })
    return flag
  }
  return checkEmpty() && checkUnique()
}
function deleteOneOption(index: number) { // 检测至少保留一个选项
  if (optionsList.value.length <= 1) {
    GlobalModal.warning({
      title: '提示',
      content: '至少保留一个选项',
      centered: true,
      keyboard: false,
    })
    return
  }
  optionsList.value.splice(index, 1)
}
function getNewOpt() {
  let index = 1
  const newOpt = [{ type: 'other', value: `选项${optionsList.value.length + index}` }]
  const valList = [...optionsList.value.map(item => item.value), newOpt]
  while (!checkValidate(valList, false)) {
    index = index + 1
    newOpt[0].value = `选项${optionsList.value.length + index}`
  }
  return newOpt
}
function addOneOption() {
  // 检测不能超过30个选项
  if (optionsList.value.length >= MAX_OPTION_LENGTH) {
    message.info('最多只能添加30个选项')
    return
  }
  // 检测选项是否唯一
  if (!checkValidate(optionsList.value.map(item => item.value)))
    return
  optionsList.value.push({
    ...ADD_OPTION,
    rId: nanoid(),
    key: `options${Date.now()}`,
    value: getNewOpt(),
    formType: {
      type: 'INPUT_VARIABLE',
    },
  })
}
</script>

<template>
  <div class="atom-options">
    <draggable
      ref="atomOptions"
      item-key="rId"
      filter=".forbid"
      class="atom-options_draggable space-y-2"
      :list="optionsList"
      :force-fallback="true"
    >
      <template #item="{ element: item, index }">
        <div class="atom-options_item">
          <AtomConfig :form-item="item" />
          <rpa-hint-icon name="bottom-pick-menu-del" class="iconDelete" enable-hover-bg @click="deleteOneOption(index)" />
          <rpa-hint-icon name="drag-handle" class="iconMove" enable-hover-bg />
        </div>
      </template>
    </draggable>
    <rpa-hint-icon name="add-circle" class="mt-1 text-primary" enable-hover-bg @click="addOneOption()">
      <template #suffix>
        <span class="ml-1">添加一项</span>
      </template>
    </rpa-hint-icon>
  </div>
</template>

<style lang="scss" scoped>
.atom-options {
  width: 100%;
  .atom-options_draggable {
    .atom-options_item {
      width: 100%;
      display: inline-flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px;
      margin-bottom: 8px;
      border-radius: 4px;

      .iconDelete,
      .iconMove {
        font-size: 16px;
        margin-left: 8px;
      }
      .iconMove {
        cursor: move;
        margin-left: 4px;
      }
    }

    // Dragging styles
    .sortable-ghost {
      border-top: 1px solid var(--color-primary);
      border-radius: 0;
    }
  }
  .dragclass {
    background-color: #f0f0f0;
    border-radius: 6px;
    opacity: 0.5;
  }
  .ant-btn {
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
.atom-popover {
  .atom-popover-footer {
    border-top: 1px solid #f0f0f0;
  }
}

:deep(.ant-popover) {
  display: none;
}

:deep(.ant-popover-content) {
  display: none;
}
</style>
