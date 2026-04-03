import type { IWorkbookData as ISheetWorkbookData, IWorksheetData } from '@univerjs/core'
import type { LocaleType as SheetLocaleType } from '@univerjs/presets'
import { defineAsyncComponent } from 'vue'

import type { ICellValue } from './Sheet.vue'

export const Sheet = defineAsyncComponent(() => import('./Sheet.vue'))

export type { ICellValue, ISheetWorkbookData, IWorksheetData, SheetLocaleType }
