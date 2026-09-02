package com.iflytek.rpa.robot.service.impl;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.alibaba.fastjson.JSONObject;
import com.iflytek.rpa.example.config.OpenApiProperties;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

class RobotDesignServiceImplTest {

    private static final String UPSERT_URL = "http://openapi-service:8020/workflows/upsert";

    private RobotDesignServiceImpl service;
    private RestTemplate restTemplate;

    @BeforeEach
    void setUp() {
        service = spy(new RobotDesignServiceImpl());
        restTemplate = mock(RestTemplate.class);
        OpenApiProperties properties = new OpenApiProperties();
        properties.setWorkflowsUpsertUrl(UPSERT_URL);
        ReflectionTestUtils.setField(service, "openApiProperties", properties);
        doReturn(restTemplate).when(service).createRestTemplate();
    }

    @Test
    void shouldDeactivateWorkflowAtConfiguredUrlWhenRobotIsDeleted() {
        when(restTemplate.exchange(eq(UPSERT_URL), eq(HttpMethod.POST), any(HttpEntity.class), eq(String.class)))
                .thenReturn(ResponseEntity.ok("{}"));

        ReflectionTestUtils.invokeMethod(service, "sendDeleteRequestToOpenApi", "robot-1", "user-1");

        ArgumentCaptor<HttpEntity<String>> requestCaptor = captureRequest();
        JSONObject request = JSONObject.parseObject(requestCaptor.getValue().getBody());
        assertEquals("robot-1", request.getString("project_id"));
        assertEquals(0, request.getInteger("status"));
        assertEquals("user-1", requestCaptor.getValue().getHeaders().getFirst("user_id"));
    }

    @Test
    void shouldKeepDeleteOperationCompatibleWhenOpenApiIsUnavailable() {
        when(restTemplate.exchange(eq(UPSERT_URL), eq(HttpMethod.POST), any(HttpEntity.class), eq(String.class)))
                .thenThrow(new ResourceAccessException("unreachable"));

        assertDoesNotThrow(
                () -> ReflectionTestUtils.invokeMethod(service, "sendDeleteRequestToOpenApi", "robot-2", "user-2"));
    }

    @Test
    void shouldCreateDefaultRestTemplate() {
        assertNotNull(new RobotDesignServiceImpl().createRestTemplate());
    }

    @SuppressWarnings("unchecked")
    private ArgumentCaptor<HttpEntity<String>> captureRequest() {
        ArgumentCaptor<HttpEntity<String>> requestCaptor = ArgumentCaptor.forClass(HttpEntity.class);
        verify(restTemplate).exchange(eq(UPSERT_URL), eq(HttpMethod.POST), requestCaptor.capture(), eq(String.class));
        return requestCaptor;
    }
}
