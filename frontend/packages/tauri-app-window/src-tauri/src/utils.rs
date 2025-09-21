use tauri:: { Manager, Runtime};
use window_shadows::set_shadow;

pub fn set_window_shadow<R: Runtime>(app: &tauri::App<R>) {
    // 打印日志窗口
    println!("set window shadow");
    let window = app.get_window("iflyrpa-window").unwrap();
    set_shadow(&window, true).expect("Failed to set window shadow");
}
