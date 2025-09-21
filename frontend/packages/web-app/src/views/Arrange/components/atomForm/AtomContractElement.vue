<script setup lang="ts">
import { EditOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { Empty, Tag } from 'ant-design-vue'
import { ref, watch, watchEffect } from 'vue'

import { ContractEleModal } from '@/views/Arrange/components/tools/components'

const { renderData } = defineProps({
  renderData: {
    type: Object as () => RPA.AtomDisplayItem,
    default: () => ({}),
  },
})
const emits = defineEmits(['refresh'])

const { value, formType } = renderData
const { preset, custom } = JSON.parse(value as string || '{}')
const { params: { code, options = [] } } = formType // code字段决定 - 1:只显示预置要素 2:只显示自定义要素 3: 两个都显示

const searchValue = ref('')
const presetData = ref(preset || [])
const customData = ref(custom || [])
const filterOptions = ref([])

watch(() => searchValue.value, (val) => {
  filterOptions.value = options.filter(op => op.includes(val))
}, { immediate: true })

watchEffect(() => {
  let res = ''
  if (!presetData.value.length && !customData.value.length) {
    res = ''
  }
  else {
    res = JSON.stringify({
      preset: presetData.value,
      custom: customData.value,
    })
  }
  emits('refresh', res)
})

function openContractEleModal(isEdit: boolean, record?: {
  key: string
  name: string
  desc: string
  example: string
}) {
  NiceModal.show(ContractEleModal, {
    isEdit,
    record,
    customData: customData.value,
    onOk: (data) => {
      if (!isEdit) {
        customData.value.push(data)
        return
      }
      const idx = customData.value.findIndex(it => it.key === data.key)
      customData.value.splice(idx, 1, data)
    },
  })
};
function handleCustomItemAdd() {
  openContractEleModal(false)
};
function handleCustomItemEdit(item) {
  openContractEleModal(true, item)
};
function handleCustomItemDelete(item) {
  const idx = customData.value.findIndex(it => it.key === item.key)
  customData.value.splice(idx, 1)
};
function handlePresetItemDelete(item) {
  const idx = presetData.value.findIndex(it => it === item)
  presetData.value.splice(idx, 1)
};
function addPresetItem(op: string) {
  if (presetData.value.findIndex(it => it === op) > -1)
    return
  presetData.value.push(op)
}
</script>

<template>
  <section class="atom-contract-element">
    <div v-if="code !== 2" class="preset">
      <div class="preset-search">
        <div class="preset-search_title">
          预置要素：
        </div>
        <a-dropdown>
          <a-input v-model:value="searchValue" placeholder="请选择预置要素" />
          <template #overlay>
            <a-menu v-if="filterOptions.length > 0" class="menuscroll">
              <a-menu-item v-for="op in filterOptions" :key="op" @click="addPresetItem(op)">
                {{ op }}
              </a-menu-item>
            </a-menu>
            <div v-else class="empty">
              <a-empty :image="Empty.PRESENTED_IMAGE_SIMPLE" />
            </div>
          </template>
        </a-dropdown>
      </div>
      <div class="preset-result">
        <Tag v-for="item in presetData" :key="item" color="#2c69ff" style="border-radius: 12px; margin-bottom: 3px;" closable @close="handlePresetItemDelete(item)">
          {{ item }}
        </Tag>
      </div>
    </div>
    <div v-if="code !== 1" class="custom">
      <div class="custom-title">
        <span>自定义要素：</span>
        <rpa-hint-icon name="python-package-plus" enable-hover-bg class="text-primary" @click="handleCustomItemAdd">
          <template #suffix>
            添加自定义要素
          </template>
        </rpa-hint-icon>
      </div>
      <div class="custom-result">
        <Tag v-for="item in customData" :key="item.key" style="border-radius: 12px;" closable @close="handleCustomItemDelete(item)">
          <span>{{ item.name }}</span>
          <EditOutlined @click="handleCustomItemEdit(item)" />
        </Tag>
      </div>
    </div>
  </section>
</template>

<style lang="scss" scoped>
$title-color: #7b7c7d;
.empty {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4px;
  background-color: #ffffff;
  background-clip: padding-box;
  border-radius: 8px;
  outline: none;
  box-shadow:
    0 6px 16px 0 rgba(0, 0, 0, 0.08),
    0 3px 6px -4px rgba(0, 0, 0, 0.12),
    0 9px 28px 8px rgba(0, 0, 0, 0.05);
}
.menuscroll {
  max-height: 250px;
  overflow: auto;
}
.atom-contract-element {
  width: 100%;
  .preset {
    &-search {
      display: flex;
      justify-content: space-between;
      align-items: center;
      &_title {
        width: 110px;
        color: $title-color;
      }
    }
    &-result {
      margin-top: 4px;
    }
  }
  .custom {
    margin-top: 10px;
    &-title {
      color: $title-color;
      display: flex;
      justify-content: space-between;
      align-items: center;
      .ant-btn > span {
        vertical-align: middle;
      }
    }
    &-result {
      margin-top: 4px;
      border: 1px solid #d9d9d9;
      border-radius: 4px;
      padding: 4px;
      min-height: 32px;
      max-height: 380px;
      overflow: auto;
    }
  }
}
</style>
