if (typeof window === 'undefined') {
  throw new TypeError('This code must be run in a browser environment.')
}

let maxRetries = 100

function init() {
  if (window.__TAURI_METADATA__) {
    import('./windowManager').then((module) => {
      const TauriWindowManager = module.default
      window.WindowManager = new TauriWindowManager()
    })
    import('./shortCutManager').then((module) => {
      window.ShortCutManager = module.default
    })
    import('./clipboardManager').then((module) => {
      window.ClipboardManager = module.default
    })
    import('./utilsManager').then((module) => {
      window.UtilsManager = module.default
    })
    import('./updaterManager').then((module) => {
      window.UpdaterManager = module.default
    })
    console.log('%c Tauri SDK initialization is complete', 'color: white; background-color: green;')
  }
  else {
    setTimeout(() => {
      maxRetries-- > 0 ? init() : console.warn('Tauri SDK initialization failed: __TAURI_METADATA__ not found')
    }, 0)
  }
}

init()
