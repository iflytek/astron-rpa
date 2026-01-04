<script lang="ts" setup>
import { sheetUtils } from '@rpa/components'
import type { ISheetWorkbookData } from '@rpa/components'
import { ref } from 'vue'

import { useDataSheetStore } from './useDataSheet'

let workbookData: ISheetWorkbookData | null = null

interface FormState {
  open: boolean
  sheetOptions: { label: string, value: string }[]
  selectedSheet?: string
}

const { isReady, createWorkbook } = useDataSheetStore()

const formRef = ref()
const formState = ref<FormState>({
  open: false,
  sheetOptions: [],
  selectedSheet: undefined,
})

async function handleOk() {
  await formRef.value.validate()
  const { selectedSheet: sheetId } = formState.value

  createWorkbook({
    ...workbookData,
    sheets: { [sheetId]: workbookData.sheets[sheetId] },
    sheetOrder: [sheetId],
  })

  handleCancel()
}

async function handleImport() {
  workbookData = await sheetUtils.importExcelFile()

  const sheetOptions = Object.values(workbookData.sheets).map(sheet => ({
    label: sheet.name,
    value: sheet.id,
  }))

  formState.value = {
    open: true,
    sheetOptions,
    selectedSheet: sheetOptions[0]?.value,
  }
}

function handleCancel() {
  formState.value.open = false
}
</script>

<template>
  <rpa-hint-icon name="upload-folder" enable-hover-bg :disabled="!isReady" @click="handleImport">
    <template #suffix>
      <span class="ml-1 text-xs">导入</span>
    </template>
  </rpa-hint-icon>

  <a-modal :open="formState.open" title="数据导入" @cancel="handleCancel" @ok="handleOk">
    <a-form ref="formRef" layout="vertical" :model="formState">
      <a-form-item label="请选择需要导入的 sheet 页" required>
        <a-select v-model:value="formState.selectedSheet" :options="formState.sheetOptions" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
