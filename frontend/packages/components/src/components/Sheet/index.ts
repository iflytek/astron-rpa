import { defineAsyncComponent } from 'vue'
import type { IWorkbookData as ISheetWorkbookData, IWorksheetData } from '@univerjs/core';
import { LocaleType as SheetLocaleType } from '@univerjs/presets'

import { type ICellValue } from './Sheet.vue'

export const Sheet = defineAsyncComponent(() => import('./Sheet.vue'))

export type { ISheetWorkbookData, IWorksheetData, ICellValue, SheetLocaleType }
