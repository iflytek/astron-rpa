import { defineStore } from "pinia";
import { useAsyncState } from "@vueuse/core";

import { getRemoteFiles, getRemoteParams } from "@/api/atom";

interface ISharedVariableType {
  id: number;
  sharedVarName: string;
  sharedVarType: string;
  sharedVarValue: string;
  subVarList: {
    varName: string;
    varType: string;
    varValue: string;
  }[];
}

const fetchSharedVariables = (): Promise<RPA.SharedVariableType[]> =>
  getRemoteParams<ISharedVariableType>().then((data) =>
    data.map((item) => ({
      value: item.id,
      label: item.sharedVarName,
      subVarList: item.subVarList || [],
    })),
  );

const fetchSharedFiles = (): Promise<RPA.SharedFileType[]> =>
  getRemoteFiles({ pageSize: 1000 }).then((data) => data.records);

export const useSharedData = defineStore("sharedData", () => {
  // 共享数据列表
  const { state: sharedVariables, execute: getSharedVariables } = useAsyncState(
    fetchSharedVariables,
    [],
    { resetOnExecute: false },
  );

  // 共享文件列表
  const { state: sharedFiles, execute: getSharedFiles } = useAsyncState(
    fetchSharedFiles,
    [],
    { resetOnExecute: false },
  );

  return { sharedVariables, getSharedVariables, sharedFiles, getSharedFiles };
});
