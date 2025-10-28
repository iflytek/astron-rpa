package com.iflytek.rpa.example.entity.Dto;

import lombok.Data;

@Data
public class WorkflowsUpsertDto {
    String project_id;
    String name;
    String english_name;
    String description;
    String version;
    Integer status;
    String parameters;
}
