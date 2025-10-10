import os

from astronverse.baseline.logger.logger import logger
from astronverse.browser_plugin.utils import Registry


def run_reg_file(plugin_id):
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        policy_reg_path = os.path.join(project_root, "plugins", "windows_policy.reg")
        # check registry key exists
        path_machine_exists = Registry.exist(
            r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist", key_type="machine"
        )

        if path_machine_exists:
            values_machine = Registry.query_value(
                r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist", key_type="machine"
            )
            logger.info(f"ExtensionInstallAllowlist machine values {values_machine}")
            if plugin_id in values_machine:
                return True
            else:
                os.startfile(policy_reg_path)
                logger.info("overwrite machine policy")
            return True
        else:
            os.startfile(policy_reg_path)
            return True
    except Exception as e:
        logger.error(f"reg error: {e}")
        return False
