import { defineAsyncComponent } from 'vue'
import type { IWorkbookData as ISheetWorkbookData, IWorksheetData } from '@univerjs/core';

import { type ICellValue } from './Sheet.vue'

export const Sheet = defineAsyncComponent(() => import('./Sheet.vue'))

export { sheetUtils } from './utils'

export { LocaleType as SheetLocaleType } from '@univerjs/presets'

export type { ISheetWorkbookData, IWorksheetData, ICellValue }
