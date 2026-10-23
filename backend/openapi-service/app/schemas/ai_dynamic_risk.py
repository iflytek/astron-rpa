"""Operations requiring explicit request approval, including deliberate denials."""

RISK_COMPONENT_OPERATIONS = {
    "ai": {
        "Agent.call_dify",
        "Agent.call_dify_chatflow",
        "Agent.call_xcagent",
        "Agent.call_astron_agent",
        "ChatAI.single_turn_chat",
        "ChatAI.chat",
        "ChatAI.knowledge_chat",
        "ContractAI.get_factors",
        "DocumentAI.theme_expand",
        "DocumentAI.sentence_expand",
        "DocumentAI.sentence_reduce",
        "RecruitAI.generate_keywords",
        "RecruitAI.rating_resume",
        "SemanticAI.choose",
    },
    "smart": {"Smart.run_code"},
    "script": {"Script.process", "Script.module", "Script.component"},
    "cua": {
        "ComputerUse.run",
        "ComputerUse.custom_action_screen",
        "ComputerUse.extract_data",
        "ComputerUse.fill_form",
        "ComputerUse.process_captcha",
    },
    "browser": {
        "BrowserScript.js_run",
        "BrowserSoftware.set_cookies",
        "BrowserSoftware.empty_cookies",
        "BrowserSoftware.browser_close",
    },
    "database": {"Database.execute_sql"},
    "email": {"Email.send_email"},
    "network": {"Network.http_request", "Network.create_folder", "Network.ftp_rename", "Network.ftp_delete"},
    "enterprise": {
        "Enterprise.upload_to_sharefolder",
        "Enterprise.download_from_sharefolder",
        "Enterprise.get_shared_variable",
    },
    "system": {
        "System.run_command",
        "System.terminate_process",
        "System.screen_lock",
        "System.screen_unlock",
        "System.printer",
    },
    "software": {"Software.cmd", "Software.close"},
    "verifycode": {"VerifyCode.picture_code", "VerifyCode.slider_code", "VerifyCode.click_code"},
}
RISK_OPERATIONS = frozenset().union(*RISK_COMPONENT_OPERATIONS.values())
CODE_OPERATIONS = frozenset(
    {"Smart.run_code", "Script.process", "Script.module", "Script.component", "BrowserScript.js_run"}
)
# These paths cannot yet provide bounded autonomous behavior / an unattended host.
DENIED_OPERATIONS = frozenset(
    {
        "ChatAI.chat",
        "ChatAI.knowledge_chat",
        "System.screen_unlock",
        *RISK_COMPONENT_OPERATIONS["cua"],
        *RISK_COMPONENT_OPERATIONS["verifycode"],
    }
)
INFERENCE_OPERATIONS = frozenset(
    {
        "ChatAI.single_turn_chat",
        "ContractAI.get_factors",
        "DocumentAI.theme_expand",
        "DocumentAI.sentence_expand",
        "DocumentAI.sentence_reduce",
        "RecruitAI.generate_keywords",
        "RecruitAI.rating_resume",
        "SemanticAI.choose",
    }
)
