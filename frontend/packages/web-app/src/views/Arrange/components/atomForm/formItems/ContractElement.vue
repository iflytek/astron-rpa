/** 使用场景：「合同要素提取-要素」 */
<script setup lang="ts">
import { EditOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { Tag, theme } from 'ant-design-vue'
import { ref, computed } from 'vue'

import { ContractEleModal } from '@/views/Arrange/components/tools/components'

import type { FormItemProps, FormItemEmits } from './index'

type PresetDataItem = string
type CustomDataItem  = {
  key: string
  name: string
  desc: string
  example: string
}

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const { token } = theme.useToken()

const { preset, custom } = JSON.parse(props.item.value as string || '{}')
const code = props.item.formType.params.code // code字段决定 - 1:只显示预置要素 2:只显示自定义要素 3: 两个都显示

const presetData = ref<PresetDataItem[]>(preset || [])
const customData = ref<CustomDataItem[]>(custom || [])

const filterOptions = computed(() => {
  const options = props.item.formType.params.options as string[];
  return options.map(op => ({ label: op, value: op }))
})

function updateValue() {
  emits('update', props.item.key, JSON.stringify({
    preset: presetData.value,
    custom: customData.value,
  }))
}

function openContractEleModal(isEdit: boolean, record?: CustomDataItem) {
  NiceModal.show(ContractEleModal, {
    isEdit,
    record,
    customData: customData.value,
    onOk: (data) => {
      if (!isEdit) {
        customData.value.push(data)
      } else {
        customData.value = customData.value.map(it => it.key === data.key ? data : it)
      }
      updateValue()
    },
  })
};

function handleCustomItemAdd() {
  openContractEleModal(false)
};

function handleCustomItemEdit(item: CustomDataItem) {
  openContractEleModal(true, item)
};

function handleCustomItemDelete(item: CustomDataItem) {
  customData.value = customData.value.filter(it => it.key !== item.key)
  updateValue()
};

function handlePresetItemDelete(item: PresetDataItem) {
  presetData.value = presetData.value.filter(it => it !== item)
  updateValue()
};

function addPresetItem(op: string) {
  if (!presetData.value.includes(op)) {
    presetData.value.push(op)
    updateValue()
  }
}
</script>

<template>
  <section class="atom-contract-element w-full">
    <div v-if="code !== 2" class="preset">
      <div class="flex items-center justify-center gap-1">
        <div class="text-[#7b7c7d]">
          预置要素：
        </div>
        <a-select
          class="flex-1"
          mode="multiple"
          :value="[]"
          :options="filterOptions"
          placeholder="请选择预置要素"
          @select="addPresetItem"
        />
      </div>
      <Tag
        v-for="item in presetData"
        :key="item"
        :color="token.colorPrimary"
        class="preset-result-item rounded-xl mt-1"
        closable
        @close="handlePresetItemDelete(item)"
      >
        {{ item }}
      </Tag>
    </div>
    <div v-if="code !== 1" class="mt-2.5">
      <div class="flex items-center justify-between gap-1">
        <span class="text-[#7b7c7d]">自定义要素：</span>
        <rpa-hint-icon name="python-package-plus" enable-hover-bg class="text-primary" @click="handleCustomItemAdd">
          <template #suffix>
            添加自定义要素
          </template>
        </rpa-hint-icon>
      </div>
      <div class="custom-result border border-border">
        <Tag
          v-for="item in customData"
          :key="item.key"
          class="rounded-xl"
          closable
          @close="handleCustomItemDelete(item)"
        >
          <span>{{ item.name }}</span>
          <EditOutlined @click="handleCustomItemEdit(item)" />
        </Tag>
      </div>
    </div>
  </section>
</template>

<style lang="scss" scoped>
.custom-result {
  margin-top: 4px;
  border-radius: 4px;
  padding: 4px;
  min-height: 32px;
  max-height: 380px;
  overflow: auto;
}
</style>
