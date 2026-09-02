package com.iflytek.rpa.example.entity.Dto;

import lombok.Data;

@Data
public class WorkflowsUpsertDto {
    String project_id;
    String name;
    String english_name;
    String description;
    Integer version;
    Integer status;
    String parameters;
    String example_project_id;

    public static WorkflowsUpsertDto published(
            String projectId,
            String name,
            String description,
            Integer version,
            String parameters,
            String exampleProjectId) {
        WorkflowsUpsertDto workflow = new WorkflowsUpsertDto();
        String workflowName = name == null || name.trim().isEmpty() ? projectId : name;
        workflow.setProject_id(projectId);
        workflow.setName(workflowName);
        workflow.setEnglish_name(workflowName);
        workflow.setDescription(description);
        workflow.setVersion(version);
        workflow.setStatus(1);
        workflow.setParameters(parameters);
        workflow.setExample_project_id(exampleProjectId);
        return workflow;
    }
}
