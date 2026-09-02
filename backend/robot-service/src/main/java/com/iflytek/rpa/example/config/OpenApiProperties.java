package com.iflytek.rpa.example.config;

import com.iflytek.rpa.example.constants.ExampleConstants;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "openapi")
public class OpenApiProperties {

    private String workflowsUpsertUrl = ExampleConstants.WORKFLOWS_UPSERT_URL;

    public String getWorkflowsUpsertUrl() {
        return workflowsUpsertUrl;
    }

    public void setWorkflowsUpsertUrl(String workflowsUpsertUrl) {
        if (workflowsUpsertUrl == null || workflowsUpsertUrl.trim().isEmpty()) {
            this.workflowsUpsertUrl = ExampleConstants.WORKFLOWS_UPSERT_URL;
            return;
        }
        this.workflowsUpsertUrl = workflowsUpsertUrl;
    }
}
