import json
import os
import subprocess

from astronverse.browser_plugin import PluginData, PluginManagerCore, PluginStatus

# https://developer.chrome.com/docs/extensions/how-to/distribute/install-extensions?hl=zh-cn#preference-linux
# https://learn.microsoft.com/zh-cn/microsoft-edge/extensions-chromium/developer-guide/alternate-distribution-options#using-a-preferences-json-file-macos-and-linux


class ChromiumPluginManager(PluginManagerCore):
    root_path = "/opt/google/chrome"
    browser_name = "google-chrome"
    process_name = "chrome"
    extension_path = os.path.join(root_path, "extensions")

    def __init__(self, plugin_data: PluginData, root_path: str, browser_name: str, process_name: str) -> None:
        self.plugin_data = plugin_data
        self.root_path = root_path
        self.browser_name = browser_name
        self.process_name = process_name
        self.extension_path = os.path.join(root_path, "extensions")

    def check_browser(self):
        try:
            result = subprocess.run(
                ["which", self.browser_name],
                check=False,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def check_plugin(self):
        plugin_config_path = os.path.join(self.extension_path, f"{self.plugin_data.plugin_id}.json")
        if os.path.exists(plugin_config_path):
            with open(plugin_config_path, encoding="utf-8") as file:
                plugin_config_data = json.load(file)
                installed_version = plugin_config_data.get("external_version")
                latest_version = self.plugin_data.plugin_version
                latest = installed_version == latest_version
                return PluginStatus(
                    installed=True, installed_version=installed_version, latest_version=latest_version, latest=latest
                )
        else:
            return PluginStatus(installed=False, latest_version=self.plugin_data.plugin_version, latest=False)

    def close_browser(self):
        try:
            subprocess.run(
                ["killall", self.process_name],
                check=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            pass
        except Exception as e:
            pass

    def open_browser(self):
        pass

    def install_plugin(self):
        read_write = os.access(self.root_path, os.R_OK | os.W_OK)
        if not read_write:
            try:
                subprocess.run(
                    ["pkexec", "chmod", "777", self.root_path],
                    check=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError:
                raise Exception("no permission to write /opt/google/chrome")

        if not os.path.exists(self.extension_path):
            os.makedirs(self.extension_path)

        plugin_config_data = {
            "external_crx": self.plugin_data.plugin_path,
            "external_version": self.plugin_data.plugin_version,
        }
        plugin_config_path = os.path.join(self.extension_path, f"{self.plugin_data.plugin_id}.json")
        with open(plugin_config_path, "w", encoding="utf-8") as file:
            json.dump(plugin_config_data, file, indent=4)
        policy_dir = "/etc/opt/chrome/policies/managed"
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        policy_json_path = os.path.join(project_root, "policy", "policy.json")
        if not os.path.exists(policy_dir):
            os.makedirs(policy_dir)
        subprocess.run(
            ["sudo", "cp", policy_json_path, policy_dir],
            check=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
