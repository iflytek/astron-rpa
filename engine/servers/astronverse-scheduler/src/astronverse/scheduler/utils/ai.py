import ast
from enum import Enum

import requests


class InputType(Enum):
    FILE = "file"
    TEXT = "text"


CONTRACT_FACTOR_DICT = {
    "合同名称": "反映合同内容和性质的完整标题或名称",
    "合同编号": "合同的唯一识别编码",
    "合同签订日期": "双方正式签署合同的日期",
    "合同开始日期": "合同正式生效或开始履行的日期",
    "合同结束日期": "合同有效期结束或阶段履行完成的日期",
    "合同标的": "合同交易对象的完整名称",
    "标的数量": "交易数量及单位",
    "单价": "单位商品或服务价格",
    "税率": "合同适用税率",
    "税额": "依据税率计算出的税款金额",
    "合同总金额": "交易总价及币种",
    "付款方式": "合同约定的支付或结算方式",
    "甲方": "合同甲方名称",
    "乙方": "合同乙方名称",
    "甲方开户行": "甲方开户银行名称",
    "甲方银行账号": "甲方银行账号",
    "乙方开户行": "乙方开户银行名称",
    "乙方银行账号": "乙方银行账号",
}


def extract_pdf(path: str) -> str:
    import pypdf

    pdf_reader = pypdf.PdfReader(path)
    return "\n".join([pdf_reader.pages[page_num].extract_text() for page_num in range(len(pdf_reader.pages))])


def extract_docx(path: str) -> str:
    try:
        from docx import Document as d_doc
    except Exception as exc:
        raise Exception(
            "Docx package depend on Python 3.x version. "
            "If import error, please execute `pip install python-docx`"
        ) from exc

    document = d_doc(path)
    return "\n\n".join([para.text for para in document.paragraphs])


def get_factors(
    contract_type: InputType = InputType.TEXT,
    contract_path: str = "",
    contract_content: str = "",
    custom_factors: str = "",
    contract_validate: str = "",
    model: str = "",
    route_port: int = 13159,
):
    if contract_type == InputType.FILE:
        file_extension = contract_path.split(".")[-1].lower()
        if file_extension == "pdf":
            contract_content = extract_pdf(contract_path)
        elif file_extension in ["docx", "doc"]:
            contract_content = extract_docx(contract_path)
        elif file_extension == "txt":
            with open(contract_path, encoding="utf-8") as f:
                contract_content = f.read()
        else:
            raise ValueError(f"Unsupported contract file type: {file_extension}")

    try:
        factor_config = ast.literal_eval(custom_factors)
    except Exception as exc:
        raise ValueError("custom_factors format error") from exc

    preset_factors = factor_config.get("preset", [])
    custom_factor_list = factor_config.get("custom", [])

    factors = []
    for factor in preset_factors:
        factors.append({"name": factor, "desc": CONTRACT_FACTOR_DICT.get(factor, "")})
    for factor in custom_factor_list:
        factors.append(
            {
                "name": factor.get("name", ""),
                "desc": factor.get("desc", ""),
                "example": factor.get("example", ""),
            }
        )

    payload = {
        "prompt_type": "contract",
        "params": {
            "factors": str(factors),
            "parsed_content": contract_content,
        },
    }
    if model:
        payload["model"] = model

    response = requests.post(
        f"http://127.0.0.1:{route_port}/api/rpa-ai-service/v1/chat/prompt",
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json.get("data", "")
