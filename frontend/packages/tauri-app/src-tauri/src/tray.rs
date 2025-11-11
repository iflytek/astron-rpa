use tauri::{
    AppHandle, CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu,
    SystemTrayMenuItem,
    api::dialog::ask,
};
use lazy_static::lazy_static;
use std::sync::Mutex;
use std::sync::atomic::{AtomicBool, Ordering};

lazy_static! {
    static ref GMODE: Mutex<String> = Mutex::new(String::new()); // "normal" 或 "scheduling"
    static ref SCHEDULING_STATUS: Mutex<String> = Mutex::new(String::new()); // "busy" 或 "idle"
    static ref ASK_DIALOG_SHOWING: AtomicBool = AtomicBool::new(false); // 弹窗状态
}

pub fn menu() -> SystemTray {
    let mut gmode = GMODE.lock().unwrap();
    *gmode = "normal".to_string();
    let mut status = SCHEDULING_STATUS.lock().unwrap();
    *status = "idle".to_string();

    let tray_menu = build_normal_menu();
    SystemTray::new().with_tooltip("星辰RPA").with_menu(tray_menu)
}

// normal 模式菜单
fn build_normal_menu() -> SystemTrayMenu {
    let quit = CustomMenuItem::new("quit".to_string(), "退出");
    let show = CustomMenuItem::new("show".to_string(), "显示");
    let hide = CustomMenuItem::new("hide".to_string(), "隐藏");
    SystemTrayMenu::new()
        .add_item(show)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(hide)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit)
}

// 调度模式菜单（根据状态切换）
fn build_scheduling_menu(status: &str) -> SystemTrayMenu {
    let status_item = if status == "busy" {
        CustomMenuItem::new("status".to_string(), "调度模式（运行中）")
    } else {
        CustomMenuItem::new("status".to_string(), "调度模式（空闲）")
    };
    let stop_task = CustomMenuItem::new("stop_task".to_string(), "中止当前任务");
    let exit_scheduling = CustomMenuItem::new("exitscheduling".to_string(), "退出调度模式");
    let exit_app = CustomMenuItem::new("exitapp".to_string(), "退出数字员工平台");

    let mut menu = SystemTrayMenu::new()
        .add_item(status_item)
        .add_native_item(SystemTrayMenuItem::Separator);

    if status == "busy" {
        menu = menu.add_item(stop_task);
    }
    menu
        .add_item(exit_scheduling)
        .add_item(exit_app)
}

// 切换菜单（mode: "normal" 或 "scheduling"，status: "idle"/"busy"）
pub fn menu_change(mode: &str, status: Option<&str>) -> SystemTrayMenu {
    let mut gmode = GMODE.lock().unwrap();
    *gmode = mode.to_string();
    println!("mode: {}", mode.to_string());
    println!("gmode: {}", gmode.to_string());

    let mut scheduling_status = SCHEDULING_STATUS.lock().unwrap();
    if let Some(s) = status {
        *scheduling_status = s.to_string();
    }

    match mode {
        "normal" => build_normal_menu(),
        "scheduling" => build_scheduling_menu(&scheduling_status),
        _ => build_normal_menu(),
    }
}

pub fn system_tray_event_handler(app: &AppHandle, event: SystemTrayEvent) {
    let window = app.get_window("main").unwrap();
    let mode = GMODE.lock().unwrap().clone(); // 锁定并克隆，尝试获取模式，不要在这里持有锁

    match event {
        SystemTrayEvent::LeftClick {
            position: _,
            size: _,
            ..
        } => {
            if mode.to_string() == "normal" {
                // 若窗口已隐藏，则显示窗口
                if !window.is_visible().unwrap() {
                    window.show().unwrap();
                } else if window.is_minimized().unwrap() { // 若窗口已最小化，则取消最小化
                    window.unminimize().unwrap();
                    // 置顶
                    window.set_focus().unwrap();
                } else {
                    window.minimize().unwrap();
                }
            }
        }
        SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
            "quit" => {
                std::process::exit(0);
            }
            "show" => {
                if window.is_minimized().unwrap() {
                    window.unminimize().unwrap();
                }
                window.show().unwrap();
            }
            "hide" => {
                window.hide().unwrap();
            }
            "exitscheduling" => {
                if ASK_DIALOG_SHOWING.swap(true, Ordering::SeqCst) { // 已有弹窗，直接返回
                    return;
                }
                // 调起系统 confirm 对话框与用户交互
                let app_clone = app.clone();
                ask(Some(&app_clone.get_window("main").unwrap()), "退出调度模式", "退出后卓越中心无法下发任务到本机，当前的调度任务同时取消", move |answer| {
                    println!("用户选择了: {}", answer);
                    ASK_DIALOG_SHOWING.store(false, Ordering::SeqCst);
                    if answer {
                        let window_clone = app_clone.get_window("main").unwrap();
                        window_clone.show().unwrap();
                        window_clone.emit("exit_scheduling_mode", {}).unwrap(); // 退出调度模式通知引擎
                        let tray_menu = menu_change("normal", None); // 根据状态构建新菜单
                        app_clone.tray_handle().set_menu(tray_menu).unwrap();
                    } else {
                        println!("用户取消了退出调度模式");
                    }
                });
            }
            "stop_task" => {
                if ASK_DIALOG_SHOWING.swap(true, Ordering::SeqCst) {
                    return;
                }
                // 调起系统 confirm 对话框与用户交互
                let app_clone = app.clone();
                ask(Some(&app_clone.get_window("main").unwrap()), "中止任务", "是否确认中止当前任务", move |answer| {
                    println!("用户选择了: {}", answer);
                    ASK_DIALOG_SHOWING.store(false, Ordering::SeqCst);
                    if answer {
                        window.emit("stop_task", {}).unwrap(); // 通知前端中止任务
                    } else {
                        println!("用户取消了中止任务");
                    }
                });
            }
            "status" => { 
                // 什么都不做
            }
            "exitapp" => {
                std::process::exit(0);
            }
            _ => {}
        },
        _ => {}
    }
}
