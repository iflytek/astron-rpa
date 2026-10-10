-- Add the optional semantic choice node without replacing existing custom metadata.
START TRANSACTION;

INSERT INTO rpa.c_atom_meta_new (atom_key, atom_content)
SELECT 'SemanticAI.choose', '{"key": "SemanticAI.choose", "title": "语义选择", "version": "1.0.0", "src": "astronverse.ai.semantic.SemanticAI().choose", "comment": "根据判断说明 @{instruction} 对文本进行分类，输出所选候选或无法判断。", "inputList": [{"types": "Str", "formType": {"type": "INPUT_VARIABLE_PYTHON"}, "key": "instruction", "title": "判断说明", "name": "instruction", "tip": "描述分类标准；无法确定时返回 abstain。", "value": [{"type": "str", "value": ""}], "required": true}, {"types": "Str", "formType": {"type": "INPUT_VARIABLE_PYTHON"}, "key": "text", "title": "待判断文本", "name": "text", "tip": "输入文本或引用网页提取的文本变量。", "value": [{"type": "str", "value": ""}], "required": true}, {"types": "List", "formType": {"type": "INPUT_VARIABLE_PYTHON"}, "key": "options", "title": "候选列表", "name": "options", "tip": "引用 List 变量，每项为包含 id 和 label 的字典；id 必须唯一，不能使用 __abstain__。", "value": [{"type": "str", "value": ""}], "required": true}], "outputList": [{"types": "Dict", "formType": {"type": "RESULT"}, "key": "semantic_result", "title": "语义选择结果", "subTitle": "AI生成", "tip": "字典包含 status、selected_id、confidence；网络或服务错误走节点异常处理。"}], "icon": "single-chat", "helpManual": ""}'
WHERE NOT EXISTS (
    SELECT 1 FROM rpa.c_atom_meta_new WHERE atom_key = 'SemanticAI.choose'
);

UPDATE rpa.c_atom_meta_new
SET atom_content = JSON_ARRAY_APPEND(
    atom_content,
    '$.atomicTree',
    JSON_OBJECT(
        'key', 'semantic-ai',
        'title', 'AI语义判断',
        'atomics', JSON_ARRAY(JSON_OBJECT(
            'key', 'SemanticAI.choose', 'title', '语义选择', 'icon', 'single-chat'
        ))
    )
), update_time = CURRENT_TIMESTAMP
WHERE atom_key = 'atomCommon'
  AND JSON_TYPE(JSON_EXTRACT(atom_content, '$.atomicTree')) = 'ARRAY'
  AND JSON_SEARCH(atom_content, 'one', 'SemanticAI.choose', NULL, '$.atomicTree**.key') IS NULL;

COMMIT;
