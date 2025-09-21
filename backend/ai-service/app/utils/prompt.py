TRANSLATE_PROMPT = """
你是一个翻译大师，你擅长把下面的中文的工程名称翻译成英文，要求简短干练，但保持原有的意思，单词和单词之间用下划线分隔，所有字母均为小写

工程名称：$name

请你只返回翻译后的结果
"""

CODE_REVIEW_PROMPT = """
你是一个资深的代码审查专家，请仔细审查以下代码，从以下几个方面进行评估：

1. 代码质量和最佳实践
2. 潜在的bug和问题
3. 性能优化建议
4. 安全性问题
5. 可读性和维护性

代码语言：$language
代码内容：
$code

请提供详细的审查报告和改进建议。
"""

DOCUMENT_SUMMARY_PROMPT = """
你是一个专业的文档分析师，请仔细阅读以下文档内容，并提供简洁明了的摘要：

文档类型：$doc_type
文档内容：
$content

请提供：
1. 核心要点摘要（3-5点）
2. 关键信息提取
3. 如果有的话，提及重要的数据或结论

请用简洁的中文回复。
"""

SQL_GENERATOR_PROMPT = """
你是一个数据库专家，根据以下需求生成SQL查询语句：

数据库类型：$db_type
表结构信息：$table_info
查询需求：$requirement

请提供：
1. 完整的SQL语句
2. 简要的执行逻辑说明
3. 如果查询复杂，请提供优化建议

请确保SQL语句的正确性和效率。
"""

BUSINESS_ANALYSIS_PROMPT = """
你是一个商业分析专家，请基于以下信息进行分析：

分析主题：$topic
相关数据：$data
分析角度：$perspective

请提供：
1. 现状分析
2. 问题识别
3. 改进建议
4. 预期效果

请用专业而易懂的语言回复。
"""

EMAIL_WRITER_PROMPT = """
你是一个专业的邮件写作助手，请根据以下信息撰写邮件：

邮件类型：$email_type
收件人：$recipient
主要内容：$content
语气要求：$tone

请提供：
1. 合适的邮件主题
2. 完整的邮件正文
3. 如果需要，提供抄送建议

请确保邮件专业、清晰、有礼貌。
"""

RECRUIT_KEYWORDS_PROMPT = """
你是一个拥有多年大厂专业招聘经验的招聘经理，
目标任务：现在你需要根据下面的岗位名称，岗位描述和人才画像，在下面的要求列表中返回最合适的一项（严格从列表中选择， 每个要求列表返回一项），然后再返回2个用于搜索该岗位相关职位的关键词（字数控制在5个左右），以上所有全部用逗号隔开
要求列表：$keywords_list

职位名称：$job_name

岗位描述和人才画像：$job_description
"""

RECRUIT_RATING_PROMPT_CUSTOM = """
你是一个拥有多年大厂专业招聘经验的招聘经理，擅于分析候选人简历与岗位的匹配程度
目标任务：现需要你对我给到的候选人的候选人简历和$job_name的岗位评分画像进行匹配，请通过优秀的招聘专家角度来主观客观判断，根据以下几个评分画像维度对候选人进行评分，全部维度加起来总分为100分。
整理并以JSON的格式返回下面信息：候选人姓名、岗位、各维度匹配得分、打分原因、匹配度总分(所有项目加起来总分为100分)，不返回岗位任职要求。

########## 评分维度 ##########
$rating_dimensions

########## 候选人简历信息 ##########
$resume
"""

RECRUIT_RATING_PROMPT_DEFAULT = """
你是一个招聘大数据智能分析助手，请帮我评估现有岗位描述、候选人简历信息之间的匹配度。
########## 岗位描述 ##########
$job_description

根据上面的岗位描述获取该岗位（$job_name）需要以下哪些任职要求：
职位职能,学历要求,专业要求,工作年限,学校要求,任职公司要求,专业技能要求,软性技能要求,加分技能要求,语言要求,证书,性别要求,年龄要求,管理能力要求,职能经验要求,行业经验要求。

########## 候选人简历信息 ##########
$resume

根据获取到的岗位任职要求和简历信息作多维度细化分析，岗位介绍中没有提及的任职要求对简历不做要求，总结成3-6个评分画像维度。
根据总结出的画像维度，对候选人简历进行分析，判断其简历与岗位描述之间的匹配度，并给出评分。注意分配维度权重，重要的方面权重高，不重要的方面权重低。
要求总结出的维度满分加起来为一百分，比如维度A满分30分，维度B满分40分，维度C满分30分，总和为100分。
整理并以 JSON 的格式返回下面信息：候选人姓名、岗位、各维度匹配得分（并记录维度单项满分，比如某维度满分为30得分为10，输出10/30）、打分原因、匹配度总分(所有维度加起来总分为100分)。不返回岗位任职要求。

"""

CONTRACT_COMMON_PROMPT = """
作为一名合同文件解析专家，你的任务是从用户提供的**合同文件内容**中，逐一精准提取用户指定的**提取要素**，并按照要求输出结果。请严格遵循**任务要求**和**输出格式**。

=====================
### **提取要素**：

请从合同文件中提取以下所有要素的信息：

$factors

=====================
### **任务要求**：

1. *逐项匹配*：对于每个要素，请在合同文件内容中进行逐一匹配，并直接提取原文信息；
2. *严格来源*：所有要素信息必须直接源自合同文件原文，请勿进行任何归纳、总结或推理；
3. *重复出现*：如果某要素在合同文件中多次重复出现相同内容，仅提取一处即可；
4. *多处匹配*：如果某要素对应信息包含合同文件中不同位置的多处内容，请将不同位置的内容拼接成一个字符串，并使用中文逗号 `，`进行分隔；
5. *无匹配时*：若某要素在合同文件中未找到对应信息，请将该要素的值设置为空字符串 `""`；
6. *仅返回结果*：请勿添加任何解释性文字、评论或无关内容。

=====================
### **合同文件内容**：

以下是用户提供的合同文件内容，请按照**任务要求**给出提取结果：

$parsed_content

=====================
### **输出格式**：

请严格按照以下 JSON 格式返回结果，确保字段名与要素一一对应，且仅包含提取的内容：

{
  "要素1名称": ["要素1原文信息1"，"要素1原文信息2"],
  "要素2名称": "要素2原文信息",
  "要素3名称": "",
  ...
}

"""


prompt_dict = {
    "translate": TRANSLATE_PROMPT,
    "code_review": CODE_REVIEW_PROMPT,
    "document_summary": DOCUMENT_SUMMARY_PROMPT,
    "sql_generator": SQL_GENERATOR_PROMPT,
    "business_analysis": BUSINESS_ANALYSIS_PROMPT,
    "email_writer": EMAIL_WRITER_PROMPT,
    "recruit_keywords": RECRUIT_KEYWORDS_PROMPT,
    "recruit_rating_custom": RECRUIT_RATING_PROMPT_CUSTOM,
    "recruit_rating_default": RECRUIT_RATING_PROMPT_DEFAULT,
    "contract": CONTRACT_COMMON_PROMPT
}


def format_prompt(prompt_type: str, params: dict) -> str:
    """格式化prompt模板"""
    from string import Template
    template = Template(prompt_dict.get(prompt_type))
    if not template:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    
    try:
        return template.safe_substitute(**params)
    except KeyError as e:
        raise ValueError(f"Missing required parameter: {e}")

def get_available_prompts() -> list:
    """获取可用的prompt类型列表"""
    return list(prompt_dict.keys())