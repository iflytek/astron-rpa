<script lang="ts" setup>
import { BorderTopOutlined, EditOutlined, MoreOutlined, PlusCircleOutlined, RedoOutlined, TableOutlined } from '@ant-design/icons-vue'
import { Empty } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { defineAsyncComponent, h, onMounted } from 'vue'

import VxeGrid from '@/plugins/VxeTable'

import { useBatchPickStore } from '@/stores/useBatchPickStore'

import Header from '../Header.vue'

import { useDataBatch } from './useDataBatch'

const BatchModal = defineAsyncComponent(() => import('./BatchModal.vue'))

const {
  formState,
  menuItems,
  selectedColumnIndex,
  gridOptions,
  gridRef,
  formRef,
  rules,
  batchFormType,
  activeColumn,
  batchModalRef,
  checkData,
  columnClick,
  menuClick,
  loadGridData,
  save,
  cancel,
  newBatch,
  batchTableHead,
  clear,
  addSimilarData,
  handleModalOk,
  editTableElement,
  hookInit,
  closeDataBatch,
  openSourcePage,
  moreMenuClick,
  checkboxClick,
  batchModalVisible,
  batchModalConfig,
} = useDataBatch()

const useBatchPick = useBatchPickStore()
const { t } = useTranslation()

function headerCellMenuTop(length: number) {
  return length > 6 ? 'margin-top: 40px;' : 'margin-top: 0px;'
}

function batchButtonText() {
  const textMap = {
    'similar': t('dataBatch.newColumn'),
    'table': t('dataBatch.rebatch'),
    '': t('dataBatch.startBatch'),
  }
  return textMap[batchFormType.value]
}

function batchButtonIcon() {
  const iconMap = {
    'similar': h(PlusCircleOutlined),
    'table': h(RedoOutlined),
    '': h(TableOutlined),
  }
  return iconMap[batchFormType.value]
}

onMounted(() => {
  hookInit()
  loadGridData()
  console.log({
    width: window.innerWidth,
    height: window.innerHeight,
    dpr: devicePixelRatio,
  })
})
</script>

<template>
  <div id="dataBatch" class="data-batch">
    <Header :title="t('dataBatch.title')" :maximize="false" :close-fn="closeDataBatch" :dbtoggle-prevent="true" />
    <div class="data-batch-content">
      <!-- 表格名称 -->
      <a-form ref="formRef" :model="formState" :rules="rules" layout="vertical" class="data-batch-form">
        <a-form-item :label="t('dataBatch.tableName')" name="name">
          <a-input v-model:value="formState.name" class="a-input" :placeholder="t('dataBatch.tableNamePlaceholder')" />
        </a-form-item>
      </a-form>
      <!-- 表格按钮 -->
      <a-row class="data-batch-action">
        <a-col :span="6" class="text-left flex items-center text-[12px]">
          {{ t('dataBatch.tablePreview') }}
        </a-col>
        <a-col :span="18" class="text-right">
          <a-button class="mr-2 batch-btn text-[12px]" :disabled="useBatchPick.isPicking || gridOptions.loading" :icon="batchButtonIcon()" @click="() => { newBatch() }">
            {{ batchButtonText() }}
          </a-button>
          <a-button class="mr-2 batch-btn text-[12px]" :disabled="useBatchPick.isPicking || gridOptions.loading" :icon="h(BorderTopOutlined)" @click="batchTableHead">
            {{ t('dataBatch.tableHeaderBatch') }}
          </a-button>
          <a-button class="mr-2 batch-btn text-[12px]" :disabled="useBatchPick.isPicking || gridOptions.loading" danger @click="clear">
            {{ t('dataBatch.emptyTable') }}
          </a-button>
        </a-col>
      </a-row>
      <div v-if="batchFormType" class="absolute bottom-0 left-0 n-result">
        <div class="data-type">
          <span v-if="batchFormType === 'table'">{{ t('dataBatch.reconizeTable') }}， <span class="color-blue cursor-pointer" @click="() => { editTableElement() }">{{ t('dataBatch.editTableElement') }}</span></span>
          <span v-if="batchFormType === 'similar'">
            {{ t('dataBatch.currentColumn') }}&nbsp;<b>{{ activeColumn?.title }}</b>，<span class="color-blue cursor-pointer" @click="() => { addSimilarData(selectedColumnIndex) }">{{ t('dataBatch.addSimilarData') }}</span>
          </span>
        </div>
      </div>
      <div v-else class="absolute bottom-0 left-0 n-result h-[28px]" />
      <!-- 表格预览 -->
      <div class="data-batch-table">
        <VxeGrid v-bind="gridOptions" ref="gridRef" class="batch-table" @header-cell-click.prevent="columnClick">
          <template #customHeader="{ column, columnIndex }">
            <div class="header-cell">
              <div class="header-cell-title" :title="column.title">
                {{ column.title }}
              </div>
              <a-dropdown :trigger="['click']" :destroy-popup-on-hide="true">
                <MoreOutlined @click.stop="moreMenuClick(columnIndex)" />
                <template #overlay>
                  <a-menu class="header-cell-menu" :style="headerCellMenuTop(menuItems.length)" @click="(item) => { menuClick(item, columnIndex) }">
                    <template v-for="item in menuItems" :key="item.key">
                      <a-sub-menu v-if="item.children" :key="`${item.key}`" class="header-cell-sub-menu ">
                        <template #title>
                          <span v-if="item.active" class="header-cell-menu-item-active text-[12px]" />
                          <span class="text-[12px]">{{ t(`dataBatch.${item.key}`) }}</span>
                        </template>
                        <a-menu-item v-for="child in item.children" :key="child.key">
                          <span class="flex items-center text-[12px]">
                            <a-checkbox v-if="child.checkable" v-model:checked="child.checked" class="mr-2" @click="(e) => { checkboxClick(e, columnIndex, child) }" />
                            <span class="mr-2">{{ t(`dataBatch.${child.key}`) }}</span>
                            <EditOutlined v-if="child.showEdit" class="ml-auto hover:text-blue-500" @clikc="menuClick(item, columnIndex)" />
                          </span>
                        </a-menu-item>
                      </a-sub-menu>
                      <a-menu-item v-else :key="`${item.key}-else`">
                        <span v-if="item.active" class="header-cell-menu-item-active text-[12px]" />
                        <span class="text-[12px]">{{ t(`dataBatch.${item.key}`) }}</span>
                      </a-menu-item>
                    </template>
                  </a-menu>
                </template>
              </a-dropdown>
            </div>
          </template>
          <template #empty>
            <a-empty :image="Empty.PRESENTED_IMAGE_SIMPLE">
              <template #description>
                <span v-if="!checkData">{{ t('dataBatch.emptyData') }}</span>
                <span v-else>{{ t('dataBatch.openOriginWebPage') }}，<span class="link" @click="openSourcePage">{{ t('dataBatch.openNow') }}</span></span>
              </template>
            </a-empty>
          </template>
        </VxeGrid>
      </div>
      <div v-if="batchFormType" class="absolute bottom-0 left-0 w-full footer-result">
        <div class="data-info">
          {{ t('dataBatch.realData') }}: <span class="color-blue colLength">{{ gridOptions.rowLength }}</span>{{ t('dataBatch.row') }},<span class="color-blue rowLength">{{ gridOptions.columnLength }}</span>{{ t('dataBatch.column') }}
        </div>
      </div>
      <!-- 底部操作栏 -->
      <div class="data-batch-footer">
        <a-row class="mt-4 text-right">
          <a-col :span="24">
            <a-button class="mr-2 a-btn" :disabled="useBatchPick.isPicking" @click="cancel">
              {{ t('cancel') }}
            </a-button>
            <a-button class="mr-2 a-btn" type="primary" :disabled="useBatchPick.isPicking" @click="save">
              {{ t('save') }}
            </a-button>
          </a-col>
        </a-row>
      </div>
    </div>
    <BatchModal v-if="batchModalVisible" ref="batchModalRef" :config="batchModalConfig" @ok="handleModalOk" />
  </div>
</template>

<style lang="scss" scoped>
#dataBatch {
  position: relative;
  :deep(.app_control) {
    position: absolute;
    top: -1px;
    right: -1px;
  }
  :deep(.app_control__item) {
    font-size: 16px;
  }
  :deep(.ant-modal-root .ant-modal-mask) {
    position: absolute;
  }
}

.dark #dataBatch {
  :deep(.app_control) {
    color: #fafafa;
  }
}
.data-batch {
  --headerHeight: 40px;
  width: 100%;
  height: 100%;
  padding-top: var(--headerHeight);
  font-size: 12px;
  box-sizing: border-box;

  :deep(.app_control_text) {
    font-size: 16px;
  }

  .data-batch-content {
    height: 100%;
    padding: 0px 16px;
    color: #606266;

    .data-batch-form {
      // width: 240px;
      font-size: 12px;

      :deep(.ant-form-item) {
        margin-bottom: 4px;
      }
      .a-input {
        font-size: 12px;
      }

      :deep(.ant-form-item-explain-error) {
        position: absolute;
      }
    }

    .data-batch-action {
      margin-bottom: 4px;

      .batch-btn {
        padding: 0px 8px;
        height: 26px;
        :deep(.anticon) {
          vertical-align: 0.08rem;
        }
      }
    }

    .data-batch-table {
      padding: 1px;
      overflow: auto;
      width: 100%;
      height: calc(100% - 186px);

      :deep(.ant-table-cell) {
        max-width: 300px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      :deep(.vxe-header--column.col--ellipsis > .vxe-cell .vxe-cell--title) {
        display: inline-block;
        width: 100%;
      }

      .header-cell {
        width: 100%;
        display: flex;
        align-items: center;

        .header-cell-title {
          overflow: hidden;
          user-select: none;
          display: inline-block;
          width: calc(100% - 8px);
          text-overflow: ellipsis;
        }
      }

      :deep(.vxe-header--column) {
        width: fit-content;
      }
    }

    .footer-result {
      position: relative;
      float: left;
      font-size: 12px;
      line-height: 28px;
      width: 70%;
      text-align: left;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;

      .color-blue {
        color: #1890ff;
      }

      .colLength,
      .rowLength {
        font-size: 14px;
        font-weight: bold;
        margin: 0 3px;
      }
    }
    .n-result {
      position: relative;
      float: left;
      font-size: 12px;
      line-height: 28px;
      width: 100%;
      text-align: left;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
      margin-bottom: 4px;

      .color-blue {
        color: #1890ff;
      }

      .data-type {
        padding: 0px 8px;
        background: #efefff;
        border-radius: 4px;
      }
    }
    .data-batch-footer {
      .a-btn {
        font-size: 13px;
      }
    }
  }
}

.header-cell-menu {
  margin-top: 40px;
  overflow-y: auto;
  font-size: 12px;

  .header-cell-sub-menu {
    display: flex;
    align-items: center;
    font-size: 12px;
  }
}

.header-cell-menu-item-active {
  position: absolute;
  top: 14px;
  left: 0px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #1890ff;
  display: inline-block;
}

.link {
  color: #1890ff;
  cursor: pointer;
}
.font-12 {
  font-size: 12px;
}

:deep(.ant-dropdown-menu-submenu-arrow-icon) {
  position: relative;
  top: -3px;
}

:deep(.ant-dropdown .ant-dropdown-menu .ant-dropdown-menu-item) {
  font-size: 12px;
}

.batch-table {
  --vxe-ui-font-size-default: 18px;
  --vxe-ui-font-size-medium: 16px;
  --vxe-ui-font-size-small: 14px;
  --vxe-ui-font-size-mini: 12px;
  --vxe-ui-table-header-background-color: #f3f3f7;
  --vxe-ui-table-column-current-background-color: #efefff;
}
.dark .batch-table {
  --vxe-ui-table-header-background-color: rgb(255 255 255 / 8%);
  --vxe-ui-table-column-current-background-color: #33326c;
}
.dark .data-batch .data-batch-content .n-result .data-type {
  background: #33326c;
}
.dark .data-batch {
  border: 1px solid rgb(255 255 255 / 8%);
}
.dark .data-batch .data-batch-content {
  color: #ffffffa6;
}
</style>
