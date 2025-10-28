INSERT INTO rpa.sample_templates (id, sample_id, name, type, version, data, description, is_active, is_deleted, created_time, updated_time) VALUES (1, '1978748427445471111', 'sample_robot_design', 'robot_design', '1.0', '{
    "robotId": "1978748427445478888",
    "name": "示例机器人",
    "creatorId": "",
    "createTime": "2025-10-16 09:02:43",
    "updaterId": "",
    "updateTime": "2025-10-16 09:03:14",
    "deleted": 0,
    "tenantId": "example-org",
    "appId": null,
    "appVersion": null,
    "marketId": null,
    "resourceStatus": null,
    "dataSource": "create",
    "transformStatus": "editing",
    "editEnable": "1"
 }', '111', 1, 0, '2025-10-28 14:43:22', '2025-10-28 07:00:57');
INSERT INTO rpa.sample_templates (id, sample_id, name, type, version, data, description, is_active, is_deleted, created_time, updated_time) VALUES (2, '1978748427445472222', 'sample_c_process', 'c_process', '1.0', '{
    "id": 3571,
    "projectId": null,
    "processId": "1978748427479027712",
    "processContent": "[{\\"key\\":\\"Report.print\\",\\"version\\":\\"1.0.0\\",\\"id\\":\\"bh748620057231429\\",\\"alias\\":\\"日志打印\\",\\"inputList\\":[{\\"key\\":\\"report_type\\",\\"value\\":\\"info\\"},{\\"key\\":\\"msg\\",\\"value\\":[{\\"type\\":\\"other\\",\\"value\\":\\"Hello world\\"}]}],\\"outputList\\":[],\\"advanced\\":[{\\"key\\":\\"__delay_before__\\",\\"value\\":[{\\"type\\":\\"other\\",\\"value\\":0}]},{\\"key\\":\\"__delay_after__\\",\\"value\\":[{\\"type\\":\\"other\\",\\"value\\":0}]}],\\"exception\\":[{\\"key\\":\\"__skip_err__\\",\\"value\\":\\"exit\\"},{\\"key\\":\\"__retry_time__\\",\\"value\\":[{\\"type\\":\\"other\\",\\"value\\":0}],\\"show\\":false},{\\"key\\":\\"__retry_interval__\\",\\"value\\":[{\\"type\\":\\"other\\",\\"value\\":0}],\\"show\\":false}]}]",
    "processName": "主流程",
    "deleted": 0,
    "creatorId": "412d8581-9761-4417-8a71-3a87ba3dce82",
    "createTime": "2025-10-16 09:02:43",
    "updaterId": "412d8581-9761-4417-8a71-3a87ba3dce82",
    "updateTime": "2025-10-16 09:03:15",
    "robotId": "1978748427445478888",
    "robotVersion": 0
 }', '222', 1, 0, '2025-10-28 14:43:22', '2025-10-28 07:17:08');
