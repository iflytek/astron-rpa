from pathlib import Path

from app.logger import get_logger

logger = get_logger(__name__)
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

prompt_dict = {
    # 主要原子能力
    "translate": "translate_prompt.md",
    "code_review": "code_review_prompt.md",
    "document_summary": "document_summary_prompt.md",
    "sql_generator": "sql_generator_prompt.md",
    "business_analysis": "business_analysis_prompt.md",
    "email_writer": "email_writer_prompt.md",
    # 招聘相关
    "recruit_keywords": "recruit/recruit_keywords_prompt.md",
    "recruit_rating_custom": "recruit/recruit_rating_prompt_custom.md",
    "recruit_rating_default": "recruit/recruit_rating_prompt_default.md",
    # 合同相关
    "contract": "contract/contract_common_prompt.md",
    # 智能组件
    "smart_web_auto": "smart/web_auto_prompt.md",
    "smart_data_process": "smart/data_process_prompt.md",
    "smart_optimize_input": "smart/optimize_input_prompt.md",
}


def format_prompt(prompt_type: str, params: dict = {}) -> str:
    """格式化prompt模板"""
    from string import Template

    template_file_name = prompt_dict.get(prompt_type)
    if not template_file_name:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    template_file_path = PROMPTS_DIR / template_file_name

    if not template_file_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_file_path}")

    # 读取文件
    content = template_file_path.read_text(encoding="utf-8")
    template = Template(content)

    return template.safe_substitute(**params)


def get_available_prompts() -> list:
    """获取可用的prompt类型列表"""
    return list(prompt_dict.keys())
