<script lang="ts" setup>
import type { ISheetWorkbookData } from '@rpa/components'
import { ref } from 'vue'

import { useDataSheetStore } from './useDataSheet'

let workbookData: ISheetWorkbookData | null = null

interface FormState {
  open: boolean
  sheetOptions: { label: string, value: string }[]
  selectedSheet?: string
}

const { isReady, sheetRef, createWorkbook } = useDataSheetStore()

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
  workbookData = await sheetRef.value.utils.importExcelFile()

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
      <span class="ml-1 text-xs">{{ $t('common.import') }}</span>
    </template>
  </rpa-hint-icon>

  <a-modal :open="formState.open" :title="$t('sheet.dataImport')" @cancel="handleCancel" @ok="handleOk">
    <a-form ref="formRef" layout="vertical" :model="formState">
      <a-form-item :label="$t('sheet.selectSheet')" required>
        <a-select v-model:value="formState.selectedSheet" :options="formState.sheetOptions" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
