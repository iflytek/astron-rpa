-- user id from casdoor.user
SET @user_id = (SELECT id FROM casdoor.user WHERE name = 'example-user');

-- ----------------------------
-- Records of robot_design
-- ----------------------------
INSERT INTO rpa.robot_design (id, robot_id, name, creator_id, create_time, updater_id, update_time, deleted, tenant_id, app_id, app_version, market_id, resource_status, data_source, transform_status, edit_enable) VALUES (3483, '1978748427445473280', '示例机器人', @user_id, '2025-10-16 09:02:43', @user_id, '2025-10-16 09:03:14', 0, 'example-org', null, null, null, null, 'create', 'editing', '1');

-- ----------------------------
-- Records of c_process
-- ----------------------------
INSERT INTO rpa.c_process (id, project_id, process_id, process_content, process_name, deleted, creator_id, create_time, updater_id, update_time, robot_id, robot_version) VALUES (3571, null, '1978748427479027712', '[{"key":"Report.print","version":"1.0.0","id":"bh748620057231429","alias":"日志打印","inputList":[{"key":"report_type","value":"info"},{"key":"msg","value":[{"type":"other","value":"Hello world"}]}],"outputList":[],"advanced":[{"key":"__delay_before__","value":[{"type":"other","value":0}]},{"key":"__delay_after__","value":[{"type":"other","value":0}]}],"exception":[{"key":"__skip_err__","value":"exit"},{"key":"__retry_time__","value":[{"type":"other","value":0}],"show":false},{"key":"__retry_interval__","value":[{"type":"other","value":0}],"show":false}]}]', '主流程', 0, @user_id, '2025-10-16 09:02:43', @user_id, '2025-10-16 09:03:15', '1978748427445473280', 0);


