import { IWorkbookData } from '@univerjs/core'

import LuckyExcel from './luckyexcel'

const waitUserSelectExcelFile = (params: {
  onSelect?: (result: File) => void;
  onCancel?: () => void;
  onError?: (error: any) => void;
  accept?: string;
}) => {
  const { onSelect, onCancel, onError, accept = '.csv' } = params;
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = accept;
  input.click();
  input.oncancel = () => {
    onCancel?.();
  };
  input.onchange = () => {
    const file = input.files?.[0];
    if (!file) return;
    onSelect?.(file);
  };
  input.onerror = (error) => {
    onError?.(error);
  }
};

const importExcelFile = () => {
  return new Promise<IWorkbookData>((resolve, reject) => {
    try {
      waitUserSelectExcelFile({
        accept: '.xlsx,.xls,.csv',
        onSelect: (file: File) => {
          const name = file.name || '';
          const isCsv = /\.csv$/i.test(name) || file.type === 'text/csv';

          if (isCsv) {
            LuckyExcel.transformCsvToUniver(file, resolve);
          } else {
            LuckyExcel.transformExcelToUniver(file, resolve);
          }
        }
      })
    } catch (error) {
      reject(error);
    }
  });
}

const exportExcelFile = (snapshot: IWorkbookData, fileName?: string) => {
  return new Promise<ArrayBuffer>((resolve, reject) => {
    LuckyExcel.transformUniverToExcel({
      snapshot,
      fileName,
      getBuffer: true,
      success: (buffer) => buffer ? resolve(buffer) : reject(new Error('No buffer returned')),
      error: (error) => reject(error),
    })
  })
}

export const sheetUtils = {
  waitUserSelectExcelFile,
  importExcelFile,
  exportExcelFile,
}
