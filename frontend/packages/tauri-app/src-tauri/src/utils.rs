use tauri:: { Manager, Runtime};

#[cfg(target_os = "windows")]
use window_shadows::set_shadow;

pub fn set_window_shadow<R: Runtime>(app: &tauri::App<R>) {
    #[cfg(target_os = "windows")]
    {
        let window = app.get_window("main").unwrap();
        set_shadow(&window, true).expect("Failed to set window shadow");
    }
    #[cfg(not(target_os = "windows"))]
    {
        // 在非Windows系统上，窗口阴影功能不可用，跳过
    }
}
