export const WindowControl = {
  getCurrent: () => {
    return new Promise<chrome.windows.Window>((resolve) => {
      chrome.windows.getCurrent(null, (wnd) => {
        resolve(wnd)
      })
    })
  },
  update: (windowId: number, updateInfo) => {
    return new Promise((resolve) => {
      chrome.windows.update(windowId, updateInfo, (wnd) => {
        resolve(wnd)
      })
    })
  },
}
