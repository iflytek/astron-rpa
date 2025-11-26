import subprocess
import sys

from astronverse.scheduler.utils.utils import EmitType, emit_to_front


def linux_env_check():
    """linux环境检测"""
    if sys.platform == "win32":
        return

    try:
        result = subprocess.run(
            [
                "gsettings",
                "get",
                "org.gnome.desktop.interface",
                "toolkit-accessibility",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.stdout.strip() != "true":
            emit_to_front(EmitType.ALERT, msg={"msg": "首次安装，请手动重启电脑后重启打开", "type": "normal"})

            # 环境写入
            subprocess.run(
                [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.interface",
                    "toolkit-accessibility",
                    "true",
                ],
                check=True,
                encoding="utf-8",
                errors="replace",
            )
            # qt写入
            result = subprocess.run(
                ["grep", "^export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1", "/etc/profile"],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if not result.stdout:
                subprocess.run(
                    [
                        "sudo",
                        "sh",
                        "-c",
                        'echo "export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1" >> /etc/profile',
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
    except subprocess.CalledProcessError as e:
        pass
