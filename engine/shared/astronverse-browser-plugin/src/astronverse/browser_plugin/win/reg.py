import os
from astronverse.browser_plugin.utils import Registry
from astronverse.baseline.logger.logger import logger


def run_reg_file(plugin_id):
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        policy_reg_path = os.path.join(project_root, "plugins", "windows_policy.reg")
        # 检查注册表文件是否存在
        path_machine_exists = Registry.exist(
            r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist", key_type="machine"
        )

        if path_machine_exists:
            values_machine = Registry.query_value(
                r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist", key_type="machine"
            )
            logger.info(f"ExtensionInstallAllowlist machine values {values_machine}")
            if plugin_id in values_machine:
                logger.info(f"注册表文件已存在且包含指定 plugin_id {plugin_id}")
                return True
            else:
                os.startfile(policy_reg_path)
                logger.info("覆盖执行注册表文件")
            return True
        else:
            os.startfile(policy_reg_path)
            return True
    except Exception as e:
        logger.error(f"执行注册表文件失败: {e}")
        return False
