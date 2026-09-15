-- Apply once, with the OpenAPI service stopped. Existing rows remain legacy.
-- MySQL 8; no automatic destructive downgrade. See EXECUTION_MANAGEMENT.md.
ALTER TABLE openai_executions
  ADD COLUMN protocol INT NULL,
  ADD COLUMN idempotency_key_hash VARCHAR(64) NULL,
  ADD COLUMN request_hash VARCHAR(64) NULL,
  ADD COLUMN client_id VARCHAR(36) NULL,
  ADD COLUMN run_id VARCHAR(100) NULL,
  ADD COLUMN dispatch_state VARCHAR(20) NULL,
  ADD COLUMN started_at DATETIME NULL,
  ADD COLUMN execution_timeout INT NULL,
  ADD COLUMN cancel_requested BOOLEAN NOT NULL DEFAULT FALSE,
  ADD COLUMN cancel_supported BOOLEAN NOT NULL DEFAULT FALSE,
  ADD COLUMN secret_fields TEXT NULL,
  ADD UNIQUE KEY uq_execution_user_key (user_id, idempotency_key_hash),
  ADD INDEX ix_openai_executions_dispatch_state (dispatch_state);

-- Keep execution/idempotency receipts when a workflow is deleted. Some older
-- deployments created this table with SQLAlchemy and have no such foreign key.
SET @execution_history_fk = (
  SELECT CONSTRAINT_NAME FROM information_schema.REFERENTIAL_CONSTRAINTS
  WHERE CONSTRAINT_SCHEMA = DATABASE() AND TABLE_NAME = 'openai_executions'
    AND REFERENCED_TABLE_NAME = 'openai_workflows' LIMIT 1
);
SET @drop_execution_history_fk = IF(@execution_history_fk IS NULL, 'SELECT 1',
  CONCAT('ALTER TABLE openai_executions DROP FOREIGN KEY `', REPLACE(@execution_history_fk, '`', '``'), '`'));
PREPARE preserve_execution_history FROM @drop_execution_history_fk;
EXECUTE preserve_execution_history;
DEALLOCATE PREPARE preserve_execution_history;
