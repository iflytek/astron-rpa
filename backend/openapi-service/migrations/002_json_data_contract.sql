-- JSON data workflows may carry up to the public 1 MiB input limit. MEDIUMTEXT
-- keeps the durable request/result record from truncating an accepted value.
-- Apply with the OpenAPI service stopped; no existing rows are deleted.
ALTER TABLE openai_workflows
  MODIFY COLUMN parameters MEDIUMTEXT CHARACTER SET utf8mb4 NULL COMMENT '存储JSON字符串格式的参数';

ALTER TABLE openai_executions
  MODIFY COLUMN parameters MEDIUMTEXT CHARACTER SET utf8mb4 NULL COMMENT '执行参数（JSON格式）',
  MODIFY COLUMN result MEDIUMTEXT CHARACTER SET utf8mb4 NULL COMMENT '执行结果（JSON格式）',
  ADD COLUMN data_contract MEDIUMTEXT CHARACTER SET utf8mb4 NULL COMMENT '受理时冻结的JSON数据契约';
