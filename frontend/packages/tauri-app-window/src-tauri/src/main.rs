#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]
use tauri::{Manager, Window, WindowBuilder, WindowUrl, LogicalSize, LogicalPosition};
use std::env;
use std::path::PathBuf;
use tauri::Url;
use serde::Deserialize;
use serde::Serialize;
use lazy_static::lazy_static;
use std::sync::atomic::{AtomicU32};
use std::sync::Mutex;
use std::string::String;
use std::io::{self, BufRead};
use tauri::api::path::resource_dir;

use crate::utils::set_window_shadow;
mod utils;


#[derive(Serialize)]
struct Info {
    url: String, // 加载的url,可利用query格式追加业务参数
    name: String, // 窗口名称
    content: String, // 知识问答窗口需要的参数
}

lazy_static! {
    static ref PROCESS_ID: AtomicU32 = AtomicU32::new(0);
    static ref URL: Mutex<String> = Mutex::new(String::new());
    static ref NAME: Mutex<String> = Mutex::new(String::new());
    static ref CONTENT: Mutex<String> = Mutex::new(String::new());
    static ref WINDOW_LABEL: Mutex<String> = Mutex::new(String::new());
}

#[tauri::command]
async fn render_ready(window: Window) {
    let label = WINDOW_LABEL.lock().unwrap().clone();
    // let win = window.get_window("iflyrpa-window").unwrap();
    let win = window.get_window(label.as_str()).unwrap();
    let app_info = Info {
        url: URL.lock().unwrap().clone(),
        name: NAME.lock().unwrap().clone(),
        content: CONTENT.lock().unwrap().clone(),
    };
    // app_info 转换为 string
    let app_info_str = serde_json::to_string(&app_info).unwrap();
    win.emit("render-ready", app_info_str).unwrap();
}
#[tauri::command]
async fn page_handler(operType: String, data: String, window: Window) { // 依次处理不同窗口渲染进程传参给主进程的操作
    if operType == "AISave" {
        println!("{}", data);
        return;
    }
    if operType == "UserForm" {
        if data == "noresize".to_string() {
            window.set_resizable(false);
            return;
        }
        println!("{}", data);
        return;
    }
}

#[tauri::command]
async fn listen_to_stdin(window: Window) { // 监听标准输入
    let win = window.get_window("userform").unwrap();
    println!("BIG_DATA_SEND"); // 输出在控制台告诉后端页面起来了，可以传数据了
    let stdin = io::stdin();
    let handle = stdin.lock();
    
    for line in handle.lines() {
        match line {
            Ok(input) => {
                println!("Received input: {}", input);
                // 这里可以处理输入，比如发送到主窗口等
                win.emit("listen_to_stdin", input).unwrap();
            },
            Err(e) => eprintln!("Error reading line: {}", e),
        }
    }
}


fn main() {
    let current_pid = std::process::id(); // 获取当前进程的 PID
    // 打印当前进程的 PID
    println!("current_pid : {:?}", current_pid);

    let os = std::env::consts::OS; // 获取操作系统类型
    println!("Operating System: {}", os);

    // 获取当前目录
    let current_dir = env::current_dir().unwrap();
    println!("current_dir : {:?}", current_dir);

    // 获取启动参数
    let args: Vec<String> = env::args().collect();
    println!("start args : {:?}", args);

    let mut width = 580.0;
    let mut height = 400.0;
    let mut pos = "".to_string(); // "left_top", "right_top", "left_bottom", "right_bottom", "top_center" 居中置顶 "" 默认居中
    let mut transparent = true;
    let mut top = false;
    let mut title = "iflyrpa-window".to_string();
    let mut url = "https://tauri.localhost/".to_string();
    let mut shadow = false;
    let mut mini = false;
    
    for arg in &args {
        // 读取参数 --url, --name, --width, --height, --transparent 
        if arg.starts_with("--url=") { // 从参数中找到--url=开头的参数
            url = arg.splitn(2, "=").nth(1).unwrap().to_string();
        } else if arg.starts_with("--name=") { // 从参数中找到--name=开头的参数
            let mut name = NAME.lock().unwrap();
            *name = arg.splitn(2, "=").nth(1).unwrap().to_string();
        } else if arg.starts_with("--content=") { // 从参数中找到--content=开头的参数
            let mut content = CONTENT.lock().unwrap();
            *content = arg.splitn(2, "=").nth(1).unwrap().to_string();
        } else if arg.starts_with("--width=") { // 从参数中找到--width=开头的参数
            width = arg.splitn(2, "=").nth(1).unwrap().parse().unwrap();
        } else if arg.starts_with("--height=") { // 从参数中找到--height=开头的参数
            height = arg.splitn(2, "=").nth(1).unwrap().parse().unwrap();
        } else if arg.starts_with("--transparent=") { // 从参数中找到--transparent=开头的参数
            transparent = arg.splitn(2, "=").nth(1).unwrap().parse().unwrap();
        } else if arg.starts_with("--top=") { // 从参数中找到--top=开头的参数
            top = arg.splitn(2, "=").nth(1).unwrap().parse().unwrap();
        } else if arg.starts_with("--pos=") { // 从参数中找到--pos=开头的参数
            pos = arg.splitn(2, "=").nth(1).unwrap().to_string();
        } else if arg.starts_with("--shadow=") { // 从参数中找到--shadow=开头的参数
            shadow = true
        } else if arg.starts_with("--mini=1") { // 从参数中找到--mini=开头的参数
            mini = true;
            // url 上添加参数 mini=1
            url = format!("{}&mini=1", url);
        }
    };


    // 启动窗口
    tauri::Builder::default()
    .setup(move|app| {

        let isdev = env::var("TAURI_DEV_SUB_WIN").unwrap_or_default() == "true";
        let remote_addr = match isdev {
            true => "http://localhost:1420/logwin.html".to_string(),
            false => url.clone(),
        };

        let mut window_label = WINDOW_LABEL.lock().unwrap();
        if url.contains("logwin") {
            *window_label = "logwin".to_string();
        } else if url.contains("multichat") {
            *window_label = "multichat".to_string();
        } else if url.contains("userform") {
            *window_label = "userform".to_string();
        } else {
            *window_label = "iflyrpa-window".to_string();
        }

        // 打开一个窗口
        let new_window = WindowBuilder::new(app, window_label.to_string(), WindowUrl::External(Url::parse(&remote_addr).unwrap()))
        .title("iflyrpa-window")
        .inner_size(600.0, 480.0) // 设置窗口大小
        .center() // 设置窗口居中, 默认是居中的
        .decorations(false) // 设置窗口没有边框
        .always_on_top(top) // 设置窗口置顶
        .resizable(false) // 设置窗口不可调整大小
        .transparent(transparent) // 设置窗口透明
        .disable_file_drop_handler()  // 禁用文件拖放
        .build()
        .unwrap();

        let monitor = new_window.current_monitor().unwrap().expect("Failed to get monitor");
        let scale_factor = monitor.scale_factor();

        let logic_width = monitor.size().width as f64 / scale_factor as f64;
        let logic_height = monitor.size().height as f64 / scale_factor as f64;
        let mut factor_width;
        let mut factor_height;
        let mut x_coeff = 1.0;
        let mut y_coeff = 1.0;
        let mut w_base = logic_width;
        let mut h_base = logic_height;
        let mut min_width = 400.0;
        let mut max_width = 800.0;
        let mut min_height = 300.0;
        let mut max_height = 600.0;
        if window_label.as_str() == "logwin" {
            x_coeff = 0.2;
            y_coeff = 0.13;
            min_width = 360.0;
            max_width = 450.0;
            min_height = 120.0;
            max_height = 150.0;
        } else if window_label.as_str() == "multichat" {
            x_coeff = 0.4;
            y_coeff = 0.5;
        } else if window_label.as_str() == "userform" {
            x_coeff = 0.25;
            y_coeff = 0.35;
            if url.contains("option") {
                y_coeff = 0.15;
                min_height = 60.0;
            }
        } else {
            w_base = width;
            h_base = height;
        }
        factor_width = w_base * x_coeff * scale_factor as f64;
        factor_height = h_base * y_coeff * scale_factor as f64;
        // factor_width 不能小于 min_width, 不能大于 max_width
        if factor_width < min_width {
            factor_width = min_width;
        }
        if factor_width > max_width {
            factor_width = max_width;
        }
        // factor_height 不能小于 min_height, 不能大于 max_height
        if factor_height < min_height {
            factor_height = min_height;
        }
        if factor_height > max_height {
            factor_height = max_height;
        }
        if mini {
            factor_width = factor_width * 0.1;
        }

        new_window.set_size(LogicalSize::new(factor_width, factor_height)).unwrap(); // 设置窗口大小
        // 若 pos 不为空，则设置窗口位置， "left_top"表示左上角, "right_top"表示右上角, "left_bottom"表示左下角, "right_bottom"表示右下角
        match pos.as_str() {
            "left_top" => {
                new_window.set_position(LogicalPosition::new(2.0, 2.0)).unwrap();
            }
            "right_top" => {
                new_window.set_position(LogicalPosition::new(logic_width - factor_width, 2.0)).unwrap();
            }
            "left_bottom" => {
                new_window.set_position(LogicalPosition::new(2.0, logic_height - factor_height - 42.0)).unwrap();
            }
            "right_bottom" => {
                new_window.set_position(LogicalPosition::new(logic_width - factor_width, logic_height - factor_height - 42.0)).unwrap();
            }
            "top_center" => {
                new_window.set_position(LogicalPosition::new((logic_width - factor_width) / 2.0, 2.0)).unwrap();
            }
            _ => {
                new_window.center().unwrap();
            }
        }

        match shadow {
            true => set_window_shadow(app), // 设置窗口阴影
            _ => (),
        }
        Ok(())
    })
    .invoke_handler(tauri::generate_handler![listen_to_stdin, render_ready, page_handler])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
fn get_installation_path() -> Result<PathBuf, Box<dyn std::error::Error>> {
    let exe_path = env::current_exe()?;
    let install_path = exe_path.parent().ok_or("Failed to get installation directory")?;
    Ok(install_path.to_path_buf())
}
