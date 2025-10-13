#![cfg_attr(all(target_os = "windows"),windows_subsystem = "windows")]

use std::env;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::io::{BufRead, BufReader};
use std::collections::HashMap;
use std::ffi::OsStr;
use std::thread;
use log::{info, error};
use std::time::{Duration, SystemTime};
use std::fs;
use serde::{Deserialize};
use tauri::{Manager, Url, Window, WindowEvent};
use tauri::{WindowBuilder, WindowUrl};
use tauri::api::path::{app_data_dir};
use lazy_static::lazy_static;
use std::sync::atomic::{AtomicBool, Ordering};
use fern;
use hyper::{Body, Client, Uri};
use hyper_tls::HttpsConnector;
use hyper::body::HttpBody;
use tokio::{fs::File, io::AsyncWriteExt};
use base64::{Engine as _, engine::general_purpose};

// Windows特有的导入，使用条件编译
#[cfg(target_os = "windows")]
use windows::Win32::System::Threading::CREATE_NO_WINDOW;
#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

mod tray;
mod utils;

const PRO_NAME: &str = "astron-rpa";
const DATA_PATH: &str = "data";

#[derive(Debug, Deserialize, Default)]
struct AppConfig {
    remote_addr: String
}

lazy_static! {
    static ref MIAN_WINDOW_ONLOAD: AtomicBool = AtomicBool::new(false);
}


#[tauri::command]
fn main_window_onload() {
    MIAN_WINDOW_ONLOAD.store(true, Ordering::SeqCst);
}

#[tauri::command]
fn tray_change(mode: &str, status: Option<&str>, window: Window) {
    let app = window.app_handle();
    let new_menu = tray::menu_change(mode, status); // 根据状态构建新菜单
    app.tray_handle().set_menu(new_menu).unwrap();
}

fn setup_logger(log_dir: &Path) -> Result<(), String> {
    fs::create_dir_all(log_dir).map_err(|e| format!("创建日志目录失败: {} ({})", log_dir.display(), e))?;

    let log_file = log_dir.join("main.log");

    fern::Dispatch::new()
        .format(|out, message, record| {
            out.finish(format_args!(
                "{} | {} | {} - {}",
                chrono::Local::now().format("%Y-%m-%d %H:%M:%S"),
                format!("{:8}", record.level().to_string()),
                record.target(),
                message
            ))
        })
        .level(log::LevelFilter::Debug) // 全局日志级别
        .chain(std::io::stdout())       // 同时输出到控制台
        .chain(fern::log_file(&log_file).map_err(|e| format!("日志路径初始化失败: {}", e))?) // 写入文件
        .apply().map_err(|e| format!("日志初始化失败: {}", e))?;

    Ok(())
}

fn is_on_c_drive(path: &Path) -> bool {
    #[cfg(target_os = "windows")]
    {
        match path.ancestors().nth(1) {  // nth(1) 通常是盘符根路径（例如 "C:"）
            Some(root) => root.to_string_lossy().starts_with("C:"),
            None => false,
        }
    }
    #[cfg(not(target_os = "windows"))]
    {
        // 在非Windows系统上，总是返回false，使用安装目录
        true
    }
}

fn work_dir(app_handle: &tauri::AppHandle) -> Result<PathBuf, String> {
    let install_dir = install_dir(Some(app_handle))?;

    let work_dir = if is_on_c_drive(&install_dir) {
        let user_app_dir = app_data_dir(app_handle.config().as_ref()).ok_or("work目录获取异常")?;
        if !Path::new(&user_app_dir).exists() {
            fs::create_dir_all(&user_app_dir).map_err(|e| format!("创建work目录异常{}", e))?;
        }
        user_app_dir
    } else {
        let work_path = install_dir.join(DATA_PATH);
        if !work_path.exists() {
            fs::create_dir_all(&work_path).map_err(|e| format!("创建work目录异常{}", e))?;
        }
        work_path
    };

    Ok(work_dir)
}

fn install_dir(_app_handle: Option<&tauri::AppHandle>) -> Result<PathBuf, String> {
    #[cfg(target_os = "windows")]
    {
        let exe_path = env::current_exe().map_err(|e|format!("获取当前启动目录异常{}",e))?;
        let install_path = exe_path.parent().ok_or("获取安装目录异常")?;
        Ok(install_path.to_path_buf())
    }
    #[cfg(not(target_os = "windows"))]
    {
        // 在 Linux 上使用 resource_dir 方法
        let app_handle = _app_handle.ok_or("AppHandle 不可用")?;
        let resource_dir = tauri::api::path::resource_dir(&app_handle.package_info(), &app_handle.env())
            .ok_or_else(|| "Failed to get resource directory".to_string())?;
        let install_dir = resource_dir.clone();
        Ok(install_dir)
    }
}

fn conf(app_handle: Option<&tauri::AppHandle>) -> Result<AppConfig, String> {
    let config_path = install_dir(app_handle)?.join("resources").join("conf.json");
    let config_data = fs::read_to_string(config_path).map_err(|e|format!("配置读取异常{}",e))?;
    let config: AppConfig = serde_json::from_str(&config_data).map_err(|e|format!("配置解析异常{}",e))?;
    Ok(config)
}

fn main() -> Result<(), String> {
    // 检测是否重复打开
    let process_name = env::current_exe()
        .ok()
        .as_ref()
        .and_then(|p| p.file_name())
        .and_then(|name| name.to_str())
        .ok_or("获取名称异常")?
        .to_string();
    let r = check_if_running(&process_name)?;
    if r {
        // 将窗口置顶, 并提前结束
        return Ok(());
    }

    // 启动tauri
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![main_window_onload, tray_change])
        .setup(|app| {
            let app_handle = app.handle();

            // 初始化日志服务
            setup_logger(&work_dir(&app_handle)?.join("logs")).expect("初始化日志错误");

            // 日志读取
            let config = conf(Some(&app_handle))?;

            // 启动主窗口
            let window_url = WindowUrl::App("index.html".into());

            WindowBuilder::new(app, "main", window_url)
                .title(PRO_NAME)
                .inner_size(1200.0, 718.0)
                .center()
                .decorations(false) // 设置窗口没有边框
                .disable_file_drop_handler()  // 禁用文件拖放
                .build()
                .unwrap();

            // 设置窗口阴影
            utils::set_window_shadow(app);

            // 异步启动
            thread::spawn(move || {
                match start(app_handle, config) {
                    Ok(_) => {},
                    Err(e) => {
                        error!("{}", e);
                    }
                }
            });

            Ok(())
        })
        .system_tray(tray::menu())
        .on_system_tray_event(tray::system_tray_event_handler)
        .on_window_event(|event| {
            if let WindowEvent::CloseRequested { .. } = event.event() {
                event.window().close().unwrap();
            }
        })
        .run(tauri::generate_context!())
        .unwrap_or_else(|e| {
            log::error!("error while running tauri application {}", e);
        });
    Ok(())
}

fn start(app_handle: tauri::AppHandle, config: AppConfig) -> Result<(), String> {
    let work_dir = work_dir(&app_handle)?;
    let mut need_download = false;

    let python_core = work_dir.join("python_core");

    // 检查 resources 目录中的 7z 文件并解压
    let resources_dir = install_dir(Some(&app_handle))?.join("resources");
    if resources_dir.exists() {
        let entries = fs::read_dir(&resources_dir).map_err(|e| format!("读取resources目录失败: {}", e))?;
        
        for entry in entries {
            let entry = entry.map_err(|e| format!("读取目录项失败: {}", e))?;
            let path = entry.path();
            
            if path.is_file() && path.extension().and_then(|s| s.to_str()) == Some("7z") {
                let file_name = path.file_stem().and_then(|s| s.to_str()).unwrap_or("");
                let output_dir = work_dir.join(file_name);
                
                // 如果对应的目录不存在，则解压
                if !output_dir.exists() {
                    info!("发现7z文件，正在解压: {} -> {}", path.display(), output_dir.display());
                    unzip_file(&path, &output_dir, &app_handle)?;
                    info!("解压完成: {}", file_name);
                }
            }
        }
    }

    if !python_core.exists() {
        need_download = true;
    }
    if need_download {
        // 等待前端拉起
        while !MIAN_WINDOW_ONLOAD.load(Ordering::SeqCst) {
            thread::sleep(Duration::from_millis(10));
        }
        let main_window_2 = app_handle.get_window("main").ok_or("获取主窗口")?;

        send_msg(r"\u6838\u5fc3\u4f9d\u8d56\u68c0\u6d4b".to_string(), 0.0, &main_window_2);

        // 获取远程配置
        let python_map = get_python_url(&config.remote_addr)?;

        // 运行rpa_download.exe
        setup_download(python_map, &work_dir, &main_window_2, &app_handle)?;

        // 重新检测
        if !python_core.exists() {
            return Err(format!("下载失败 {}", python_core.display()));
        }
        send_msg(r"\u6838\u5fc3\u4f9d\u8d56\u5b8c\u6210".to_string(), 50.0, &main_window_2);
    }


    // 启动rpa_setup.py
    let python_exe = if env::consts::OS == "windows" {
        python_core.join("python.exe").display().to_string()
    } else {
        python_core.join("bin").join("python3.7").display().to_string()
    };
    let mut curr_attempt = 0;
    let mut last_success_time = SystemTime::now();

    loop {
        info!("command python_exe {}", curr_attempt);

        let conf_path = install_dir(Some(&app_handle))?.join("resources").join("conf.json").display().to_string();
        setup_command(&python_exe, vec![
            &String::from("-m"),
            &String::from("astronverse.scheduler"),
            &format!("--conf={}", conf_path),
        ],  &work_dir, &app_handle);

        //  如果运行超过10分钟会重新计算次数, 并立即执行
        if SystemTime::now().duration_since(last_success_time).unwrap() > Duration::from_secs(600) {
            curr_attempt = 0
        } else {
            // 休眠10秒
            thread::sleep(Duration::from_secs(10));
        }
        last_success_time = SystemTime::now();
        curr_attempt += 1;

        // 如果在10分钟内错误次数到达5次就直接结束
        if curr_attempt > 5 {
            break
        }
    }

    Ok(())
}

fn send_msg(body: String, step: f32, main_window: &Window) {
    let json_str = format!(
        r#"{{"type": "sync", "msg": {{"msg": "{}","step": {}}}}}"#,
        body,
        step
    );
    info!("send_msg {}", json_str);
    match main_window.emit("scheduler-event", general_purpose::STANDARD.encode(&json_str)) {
        Ok(_) => {}
        Err(e) => {
            error!("{}", e);
        }
    }
}

fn setup_download(urls: HashMap<String, String>, work_dir: &PathBuf, main_window: &Window, app_handle: &tauri::AppHandle) -> Result<(), String> {
    let stp: f32 = 25.0 / urls.len() as f32;
    let mut c_stp: f32 = 0.0;
    for (key, url) in urls {
        send_msg(format!("{}", r"\u6b63\u5728\u5b89\u88c5\u6838\u5fc3\u4f8d\u8d56:\u4e0b\u8f7d\u4e2d"), c_stp, main_window);

        let parsed = Url::parse(&url).map_err(|e| format!("URL解析失败: {}", e))?;
        let path = parsed.path();

        let path_name = Path::new(path)
            .file_name()
            .ok_or("无法从URL提取文件名")?
            .to_str()
            .ok_or("文件名包含非法字符")?;

        let zip_path = work_dir.join(path_name);

        // 下载文件
        tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
            .unwrap()
            .block_on(download_file(&url, &zip_path))?;

        c_stp += stp;
        send_msg(format!("{}", r"\u6b63\u5728\u5b89\u88c5\u6838\u5fc3\u4f8d\u8d56:\u89e3\u538b\u4e2d"), c_stp, main_window);

        // 解压文件
        let parent = zip_path.parent()
            .ok_or("无法获取 ZIP 文件的父目录".to_string())?;

        let output_dir = parent.join(&key);
        unzip_file(&zip_path, &output_dir, app_handle)?;

        c_stp += stp;
        send_msg(format!("{}", r"\u6b63\u5728\u5b89\u88c5\u6838\u5fc3\u4f8d\u8d56:\u5b8c\u6210"), c_stp, main_window);
    }

    Ok(())
}

fn setup_command_output<T: std::io::Read + Send + 'static>(stream: T, prefix: &'static str, main_window: Option<Window>) {
    let reader = BufReader::new(stream);

    if let Some(window) = main_window {
        for line in reader.lines() {
            match line {
                Ok(content) => {
                    let content = content.trim_matches('"').trim();
                    if content.starts_with("||emit||") {
                        let message = content.trim_start_matches("||emit||").trim();
                        match window.emit("scheduler-event", message) {
                            Ok(_) => {}
                            Err(e) => {
                                error!("{}", e);
                            }
                        }
                    }
                },
                Err(e) => error!("{} 读取失败: {}", prefix, e),
            }
        }
    }
    else {
        for line in reader.lines() {
            match line {
                Ok(content) => info!("{} {}", prefix, content),
                Err(e) => error!("{} 读取失败: {}", prefix, e),
            }
        }
    }
}

fn setup_command(cmd: &str, args: Vec<&String>, work_dir: &PathBuf, app_handle: &tauri::AppHandle) -> bool {
    // 构建子进程
    info!("command: {} {:?} {}", cmd, args, work_dir.display());
    let mut cmd_build = Command::new(cmd);

    cmd_build.args(args)
        .current_dir(work_dir)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    #[cfg(target_os = "windows")]
    {
        // 仅 Windows 设置隐藏窗口
        cmd_build.creation_flags(CREATE_NO_WINDOW.0 as u32);
    }
    let mut process = match cmd_build.spawn()
    {
        Ok(p) => p,
        Err(e) => {
            error!("启动命令 '{}' 失败: {}", cmd, e);
            return false;
        }
    };
    // 等待前端加载
    while !MIAN_WINDOW_ONLOAD.load(Ordering::SeqCst) {
        thread::sleep(Duration::from_millis(10));
    }
    let main_window = match app_handle.get_window("main").ok_or("获取主窗口")
    {
        Ok(p) => p,
        Err(e) => {
            error!("启动命令 '{}' 失败: {}", cmd, e);
            return false;
        }
    };
    send_msg(r"\u5de5\u7a0b\u542f\u52a8".to_string(), 60.0, &main_window);

    // 获取输出管道（安全unwrap因为已配置piped）
    let stdout = process.stdout.take().expect("标准输出管道获取失败");
    let stderr = process.stderr.take().expect("错误输出管道获取失败");
    // 启动输出处理线程
    let stdout_handler = thread::spawn(move || setup_command_output(stdout,"[输出]", Some(main_window)));
    let stderr_handler = thread::spawn(move || setup_command_output(stderr, "[错误]", None));
    // 主线程等待进程结束
    let exit_status = match process.wait() {
        Ok(s) => s,
        Err(e) => {
            error!("等待命令 '{}' 失败: {}", cmd, e);
            return false;
        }
    };
    // 等待输出线程完成
    let (stdout_res, stderr_res) = (stdout_handler.join(), stderr_handler.join());
    // 处理线程错误
    if let Err(e) = stdout_res {
        error!("'{}' 的 stdout 线程异常: {:?}", cmd, e);
        return false;
    }
    if let Err(e) = stderr_res {
        error!("'{}' 的 stderr 线程异常: {:?}", cmd, e);
        return false;
    }
    // 最终状态检查
    if !exit_status.success() {
        error!("命令 '{}' 异常退出，状态码: {}", cmd, exit_status);
    }
    exit_status.success()
}

fn check_if_running(process_name: &str) -> Result<bool, String> {
    #[cfg(target_os = "windows")]
    {
        let mut cmd = Command::new("tasklist");
        cmd.creation_flags(CREATE_NO_WINDOW.0 as u32);
        let output = cmd.args(&[
                "/FI",
                &format!("IMAGENAME eq {}", process_name),
                "/FO",
                "CSV"
            ])
            .output().map_err(|e| format!("运行失败: {}", e))?;

        let output_str = String::from_utf8_lossy(&output.stdout);
        let line_count = output_str.lines().count();
        if line_count > 2
        {
            // 除了自己还有其他人
            return  Ok(true);
        }
        Ok(false)
    }
    #[cfg(not(target_os = "windows"))]
    {
        // 在Linux/macOS上使用ps命令
        let output = Command::new("ps")
            .args(&["-C", process_name, "--no-headers"])
            .output()
            .map_err(|e| format!("运行失败: {}", e))?;

        let output_str = String::from_utf8_lossy(&output.stdout);
        let process_count = output_str.lines().count();
        
        // 如果找到超过1个进程（包括自己），说明有重复运行
        Ok(process_count > 1)
    }
}

fn get_python_url(remote_url: &str) -> Result<HashMap<String, String>, String> {
    let os = env::consts::OS;
    let arch = env::consts::ARCH;
    let url = format!("{}/api/rpa_update/v2/rpa_soft/python?platform={}&arch={}", remote_url, os, arch);
    info!("get_python_url: {}", url);
    let response = reqwest::blocking::get(url).map_err(|e| format!("请求构建错误: {}", e))?;
    if response.status().is_success() {
        let data: HashMap<String, String> = response.json().map_err(|e| format!("请求返回值错误: {}", e))?;
        Ok(data)
    } else {
        Err(format!("请求失败： {}", response.status()))
    }
}

async fn download_file(url: &String, output_path: &Path) -> Result<(), String> {
    if output_path.exists() {
        return Ok(());
    }
    let temp_path = output_path.with_extension("temp");
    let mut temp_file = File::create(&temp_path).await.map_err(|e| format!("创建临时文件失败: {}", e))?;

    let uri = url.parse::<Uri>().map_err(|e| format!("解析URL失败: {}", e))?;

    let client = Client::builder().build::<_, Body>(HttpsConnector::new());
    let response = client.get(uri).await.map_err(|e| format!("请求失败: {}", e))?;
    if !response.status().is_success() {
        return Err(format!("HTTP错误: {}", response.status()));
    }

    let content_length = response.headers()
        .get("content-length")
        .and_then(|v| v.to_str().ok())
        .and_then(|s| s.parse::<u64>().ok())
        .unwrap_or(0);

    let mut downloaded = 0u64;
    let mut body = response.into_body();
    while let Some(chunk) = body.data().await {
        let chunk = chunk.map_err(|e| format!("下载中断: {}", e))?;
        let chunk_size = chunk.len() as u64;
        downloaded += chunk_size;

        if content_length > 0 {
            let percentage = (downloaded as f64 / content_length as f64 * 100.0).round();
            println!("下载进度: {:.1}%", percentage);
        }

        temp_file.write_all(&chunk).await.map_err(|e| format!("写入失败: {}", e))?;
    }

    temp_file.flush().await.map_err(|e| format!("写入失败: {}", e))?;

    fs::rename(&temp_path, output_path).map_err(|e| format!("重命名失败: {}", e))?;

    Ok(())
}

fn unzip_file(zip_path: &Path, output_dir: &Path, app_handle: &tauri::AppHandle) -> Result<(), String> {
    if output_dir.exists() {
        return Ok(());
    }

    let temp_output: PathBuf = PathBuf::from(format!("{}.temp", output_dir.display()));

    let cmd = install_dir(Some(app_handle))?.join("resources").join("7zr.exe").to_str().ok_or("获取cmd失败")?.to_string();

    // 执行解压命令
    info!("cmd {} zip_path {} output_dir {}", cmd, zip_path.display(), output_dir.display());

    let mut cmd_build = Command::new(cmd);
    #[cfg(target_os = "windows")]
    {
        // 仅 Windows 设置隐藏窗口
        cmd_build.creation_flags(CREATE_NO_WINDOW.0 as u32);
    }
    
    let output = cmd_build
        .args(&["x", "-y"]) // x 表示解压，-y 表示确认覆盖
        .arg(OsStr::new(zip_path)) // 处理非 UTF-8 路径
        .arg(format!("-o{}", temp_output.display())) // 注意解压得使用绝对路径，不然导致解压到磁盘跟路径
        .stdout(Stdio::piped())    // 捕获输出
        .stderr(Stdio::piped())
        .output()
        .map_err(|e| format!("执行命令失败: {}", e))?;


    if !output.status.success() {
        let error_msg = String::from_utf8_lossy(&output.stderr);
        return Err(format!("解压失败 (退出码 {}): {}", output.status.code().unwrap_or(-1), error_msg.trim()));
    }

    fs::rename(&temp_output, output_dir).map_err(|e| format!("重命名失败: {}", e))?;

    Ok(())
}
