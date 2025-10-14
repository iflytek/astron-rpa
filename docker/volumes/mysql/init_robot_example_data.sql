-- ----------------------------
-- Records of robot_design
-- ----------------------------
INSERT INTO rpa.robot_design (id, robot_id, name, creator_id, create_time, updater_id, update_time, deleted, tenant_id, app_id, app_version, market_id, resource_status, data_source, transform_status, edit_enable) VALUES (3481, '1978017809128493056', '示例机器人', 'a82228df-3d08-4d05-b31f-f48cfac1de81', '2025-10-14 08:39:30', 'a82228df-3d08-4d05-b31f-f48cfac1de81', '2025-10-14 08:39:58', 0, 'example-org', null, null, null, null, 'create', 'published', '1');

-- ----------------------------
-- Records of robot_execute
-- ----------------------------
INSERT INTO rpa.robot_execute (id, robot_id, name, creator_id, create_time, updater_id, update_time, deleted, tenant_id, app_id, app_version, market_id, resource_status, data_source, param_detail, dept_id_path, type, latest_release_time) VALUES (2667, '1978017809128493056', '示例机器人', 'a82228df-3d08-4d05-b31f-f48cfac1de81', '2025-10-14 08:39:58', 'a82228df-3d08-4d05-b31f-f48cfac1de81', '2025-10-14 08:39:58', 0, 'example-org', null, null, null, null, 'create', null, null, null, '2025-10-14 08:39:58');

-- ----------------------------
-- Records of c_process
-- ----------------------------
INSERT INTO rpa.c_process (id, project_id, process_id, process_content, process_name, deleted, creator_id, create_time, updater_id, update_time, robot_id, robot_version) VALUES (3568, null, '1978017809141075968', '[{"key":"Report.print","version":"1.0.0","id":"bh747906560925765","alias":"日志打印","inputList":[{"key":"report_type","value":"info"},{"key":"msg","value":[{"type":"other","value":"Hello world"}]}],"outputList":[],"advanced":[{"key":"__delay_before__","value":[{"type":"other","value":0}]},{"key":"__delay_after__","value":[{"type":"other","value":0}]}],"exception":[{"key":"__skip_err__","value":"exit"},{"key":"__retry_time__","value":[{"type":"other","value":0}],"show":false},{"key":"__retry_interval__","value":[{"type":"other","value":0}],"show":false}]}]', '主流程', 0, 'a82228df-3d08-4d05-b31f-f48cfac1de81', '2025-10-14 08:39:30', 'a82228df-3d08-4d05-b31f-f48cfac1de81', '2025-10-14 08:40:01', '1978017809128493056', 0);
INSERT INTO rpa.c_process (id, project_id, process_id, process_content, process_name, deleted, creator_id, create_time, updater_id, update_time, robot_id, robot_version) VALUES (3569, null, '1978017809141075968', '[{"key":"Report.print","version":"1.0.0","id":"bh747906560925765","alias":"日志打印","inputList":[{"key":"report_type","value":"info"},{"key":"msg","value":[{"type":"other","value":"Hello world"}]}],"outputList":[],"advanced":[{"key":"__delay_before__","value":[{"type":"other","value":0}]},{"key":"__delay_after__","value":[{"type":"other","value":0}]}],"exception":[{"key":"__skip_err__","value":"exit"},{"key":"__retry_time__","value":[{"type":"other","value":0}],"show":false},{"key":"__retry_interval__","value":[{"type":"other","value":0}],"show":false}]}]', '主流程', 0, 'a82228df-3d08-4d05-b31f-f48cfac1de81', '2025-10-14 08:39:58', 'a82228df-3d08-4d05-b31f-f48cfac1de81', '2025-10-14 08:39:58', '1978017809128493056', 1);

