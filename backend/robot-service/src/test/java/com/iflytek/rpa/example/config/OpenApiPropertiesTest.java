package com.iflytek.rpa.example.config;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.iflytek.rpa.example.constants.ExampleConstants;
import org.junit.jupiter.api.Test;
import org.springframework.boot.context.properties.bind.Bindable;
import org.springframework.boot.context.properties.bind.Binder;
import org.springframework.mock.env.MockEnvironment;

class OpenApiPropertiesTest {

    @Test
    void shouldKeepLegacyUrlAsDefault() {
        OpenApiProperties properties = new OpenApiProperties();

        assertEquals(ExampleConstants.WORKFLOWS_UPSERT_URL, properties.getWorkflowsUpsertUrl());
    }

    @Test
    void shouldAllowDeploymentToOverrideWorkflowUpsertUrl() {
        String configuredUrl = "http://openapi-service:8020/workflows/upsert";
        MockEnvironment environment = new MockEnvironment().withProperty("openapi.workflows-upsert-url", configuredUrl);

        OpenApiProperties properties = Binder.get(environment)
                .bind("openapi", Bindable.of(OpenApiProperties.class))
                .get();

        assertEquals(configuredUrl, properties.getWorkflowsUpsertUrl());
    }

    @Test
    void shouldFallBackToLegacyUrlForBlankConfiguration() {
        OpenApiProperties properties = new OpenApiProperties();

        properties.setWorkflowsUpsertUrl("  ");
        assertEquals(ExampleConstants.WORKFLOWS_UPSERT_URL, properties.getWorkflowsUpsertUrl());

        properties.setWorkflowsUpsertUrl(null);
        assertEquals(ExampleConstants.WORKFLOWS_UPSERT_URL, properties.getWorkflowsUpsertUrl());
    }
}
