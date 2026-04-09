import { contextBridge, ipcRenderer } from "electron";

import type { IpcRenderer } from "../types";

ipcRenderer.on("electron-info", (_ev, data) => {
  localStorage.setItem("electron", data);
});

const _ipcRenderer: IpcRenderer = {
  send(channel, ...args) {
    return ipcRenderer.send(channel, ...args);
  },
  invoke(channel, ...args) {
    return ipcRenderer.invoke(channel, ...args);
  },
  on(channel, listener) {
    ipcRenderer.on(channel, listener);
    return () => {
      ipcRenderer.removeListener(channel, listener);
    };
  },
  off(channel, listener) {
    return ipcRenderer.off(channel, listener);
  },
};

contextBridge.exposeInMainWorld("electron", {
  ipcRenderer: _ipcRenderer,
  globalShortcut: {
    register: (shortcut: string, callback: () => void) => {
      return ipcRenderer
        .invoke("global-shortcut-register", shortcut, callback)
        .then(() => true)
        .catch((err: Error) => {
          console.error("Failed to register global shortcut:", err);
          return false;
        });
    },
    unregister: (shortcut: string) => {
      return ipcRenderer
        .invoke("global-shortcut-unregister", shortcut)
        .then(() => true)
        .catch((err: Error) => {
          console.error("Failed to unregister global shortcut:", err);
          return false;
        });
    },
    unregisterAll: () => {
      return ipcRenderer
        .invoke("global-shortcut-unregister-all")
        .then(() => true)
        .catch((err: Error) => {
          console.error("Failed to unregister all global shortcuts:", err);
          return false;
        });
    },
  },
  clipboard: {
    readText: async () => {
      const text = await ipcRenderer.invoke("clipboard-read-text");
      return text;
    },
    writeText: (text: string) => {
      return ipcRenderer
        .invoke("clipboard-write-text", text)
        .then(() => true)
        .catch((err: Error) => {
          console.error("Failed to write text to clipboard:", err);
          return false;
        });
    },
  },
});
