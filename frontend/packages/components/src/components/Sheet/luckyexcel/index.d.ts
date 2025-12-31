import { IuploadfileList } from "./ICommon";
import exceljs from "@zwight/exceljs";
import { IWorkbookData } from "@univerjs/core";

declare class LuckyExcel {
  constructor();
  static transformExcelToLucky(excelFile: File, callback?: (files: IuploadfileList, fs?: string) => void, errorHandler?: (err: Error) => void): void;
  static transformExcelToLuckyByUrl(url: string, name: string, callBack?: (files: IuploadfileList, fs?: string) => void, errorHandler?: (err: Error) => void): void;
  static transformExcelToUniver(excelFile: File, callback?: (files: IWorkbookData, fs?: string) => void, errorHandler?: (err: Error) => void): void;
  static transformCsvToUniver(file: File, callback?: (files: IWorkbookData, fs?: string[][]) => void, errorHandler?: (err: Error) => void): void;
  static transformUniverToExcel(params: {
    snapshot: any;
    fileName?: string;
    getBuffer?: boolean;
    success?: (buffer?: exceljs.Buffer) => void;
    error?: (err: Error) => void;
  }): Promise<void>;
  static transformUniverToCsv(params: {
    snapshot: any;
    fileName?: string;
    getBuffer?: boolean;
    sheetName?: string;
    success?: (csvContent?: string | {
      [key: string]: string;
    }) => void;
    error?: (err: Error) => void;
  }): Promise<void>;
  private static downloadFile;
}

export default LuckyExcel
