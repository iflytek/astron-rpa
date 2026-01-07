import { SheetLocaleType } from '@rpa/components'
import type { ISheetWorkbookData, IWorksheetData } from '@rpa/components'

const DEFAULT_SHEET_NAME = 'sheet'
const DEFAULT_EXCEL_NAME = 'datatable.xlsx'

/**
 * 将后端保存的 datatable 数据转成 univer 工作簿数据
 * @param data
 * @returns
 */
export function transformToWorkbookData(data: RPA.IDataTableSheet): Partial<ISheetWorkbookData> {
  if (!data?.data) {
    return {}
  }

  const cellData: IWorksheetData['cellData'] = {}

  for (let row = 0; row < data.data.length; row++) {
    const rowArray = data.data[row]
    for (let col = 0; col < rowArray.length; col++) {
      const cellValue = rowArray[col]

      if (!cellData[row]) {
        cellData[row] = {}
      }

      cellData[row][col] = { v: cellValue }
    }
  }

  return {
    appVersion: '',
    id: Date.now().toString(),
    locale: SheetLocaleType.ZH_CN,
    name: DEFAULT_EXCEL_NAME,
    resources: [],
    sheetOrder: [DEFAULT_SHEET_NAME],
    sheets: {
      [DEFAULT_SHEET_NAME]: {
        id: DEFAULT_SHEET_NAME,
        cellData,
      },
    },
  }
}
