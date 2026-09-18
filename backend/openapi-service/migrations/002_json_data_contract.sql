-- JSON data workflows may carry up to the public 1 MiB input limit. MEDIUMTEXT
-- keeps the durable request/result record from truncating an accepted value.
-- Apply with the OpenAPI service stopped; no existing rows are deleted.
ALTER TABLE openai_workflows
  MODIFY COLUMN parameters MEDIUMTEXT NULL;

ALTER TABLE openai_executions
  MODIFY COLUMN parameters MEDIUMTEXT NULL,
  MODIFY COLUMN result MEDIUMTEXT NULL,
  ADD COLUMN data_contract MEDIUMTEXT NULL;
