package com.iflytek.rpa.example.service.impl;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.alibaba.fastjson.JSONObject;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import com.iflytek.rpa.base.entity.dto.QueryParamDto;
import com.iflytek.rpa.base.service.handler.ExecutorModeHandler;
import com.iflytek.rpa.example.config.OpenApiProperties;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

class SampleUsersServiceImplTest {

    private static final String UPSERT_URL = "http://openapi-service:8020/workflows/upsert";

    private SampleUsersServiceImpl service;
    private RobotExecuteDao robotExecuteDao;
    private ExecutorModeHandler executorModeHandler;
    private RestTemplate restTemplate;

    @BeforeEach
    void setUp() {
        service = spy(new SampleUsersServiceImpl());
        robotExecuteDao = mock(RobotExecuteDao.class);
        executorModeHandler = mock(ExecutorModeHandler.class);
        restTemplate = mock(RestTemplate.class);

        OpenApiProperties properties = new OpenApiProperties();
        properties.setWorkflowsUpsertUrl(UPSERT_URL);
        ReflectionTestUtils.setField(service, "robotExecuteDao", robotExecuteDao);
        ReflectionTestUtils.setField(service, "executorModeHandler", executorModeHandler);
        ReflectionTestUtils.setField(service, "openApiProperties", properties);
        ReflectionTestUtils.setField(service, "expoUserId", "example-user");
        doReturn(restTemplate).when(service).createRestTemplate();
    }

    @Test
    void shouldSynchronizePublishedWorkflowToConfiguredUrl() throws Exception {
        RobotExecute robot = robot("robot-1", "Invoice Bot", 3);
        when(robotExecuteDao.getRobotExecute("robot-1", "user-1", "tenant-1")).thenReturn(robot);
        when(executorModeHandler.getParamInside4NewVersion(
                        any(QueryParamDto.class), eq("user-1"), eq("tenant-1"), eq(3)))
                .thenReturn(emptyParameters());
        stubSuccessfulPost();

        service.sendOpenApi("robot-1", 3, "user-1", "tenant-1");

        HttpEntity<String> requestEntity = captureRequest("user-1");
        JSONObject request = JSONObject.parseObject(requestEntity.getBody());
        assertEquals("robot-1", request.getString("project_id"));
        assertEquals("Invoice Bot", request.getString("name"));
        assertEquals("Invoice Bot", request.getString("english_name"));
        assertEquals(1, request.getInteger("status"));
        assertEquals(3, request.getInteger("version"));
        assertEquals("[]", request.getString("parameters"));
    }

    @Test
    void shouldUseRobotIdWhenStoredNameIsBlank() throws Exception {
        RobotExecute robot = robot("robot-2", " ", 1);
        when(robotExecuteDao.getRobotExecute("robot-2", "user-2", "tenant-2")).thenReturn(robot);
        when(executorModeHandler.getParamInside4NewVersion(
                        any(QueryParamDto.class), eq("user-2"), eq("tenant-2"), eq(1)))
                .thenReturn(emptyParameters());
        stubSuccessfulPost();

        service.sendOpenApi("robot-2", 1, "user-2", "tenant-2");

        JSONObject request = JSONObject.parseObject(captureRequest("user-2").getBody());
        assertEquals("robot-2", request.getString("name"));
        assertEquals("robot-2", request.getString("english_name"));
    }

    @Test
    void shouldUseRobotIdWhenPublishedRobotCannotBeLoaded() throws Exception {
        when(robotExecuteDao.getRobotExecute("robot-missing", "user-2", "tenant-2"))
                .thenReturn(null);
        when(executorModeHandler.getParamInside4NewVersion(
                        any(QueryParamDto.class), eq("user-2"), eq("tenant-2"), eq(1)))
                .thenReturn(emptyParameters());
        stubSuccessfulPost();

        service.sendOpenApi("robot-missing", 1, "user-2", "tenant-2");

        JSONObject request = JSONObject.parseObject(captureRequest("user-2").getBody());
        assertEquals("robot-missing", request.getString("name"));
    }

    @Test
    void shouldPreserveExampleWorkflowMappingDuringSynchronization() throws Exception {
        RobotExecute robot = robot("robot-3", "Example Bot", 4);
        when(robotExecuteDao.getExpoUserRobotId("Example Bot", "example-user")).thenReturn("example-robot-3");
        when(executorModeHandler.getParamInside(any(QueryParamDto.class), eq("user-3"), eq("tenant-3")))
                .thenReturn(emptyParameters());
        stubSuccessfulPost();

        ReflectionTestUtils.invokeMethod(service, "sendOpenApiRequest", robot, "user-3", "tenant-3");

        JSONObject request = JSONObject.parseObject(captureRequest("user-3").getBody());
        assertEquals("example-robot-3", request.getString("example_project_id"));
        assertEquals("Example Bot", request.getString("name"));
        assertEquals(1, request.getInteger("status"));
        assertEquals(4, request.getInteger("version"));
    }

    @Test
    void shouldPropagateWorkflowSynchronizationFailure() throws Exception {
        RobotExecute robot = robot("robot-4", "Failing Bot", 1);
        when(robotExecuteDao.getRobotExecute("robot-4", "user-4", "tenant-4")).thenReturn(robot);
        when(executorModeHandler.getParamInside4NewVersion(
                        any(QueryParamDto.class), eq("user-4"), eq("tenant-4"), eq(1)))
                .thenReturn(emptyParameters());
        when(restTemplate.exchange(eq(UPSERT_URL), eq(HttpMethod.POST), any(HttpEntity.class), eq(String.class)))
                .thenThrow(new ResourceAccessException("unreachable"));

        assertThrows(ResourceAccessException.class, () -> service.sendOpenApi("robot-4", 1, "user-4", "tenant-4"));
    }

    @Test
    void shouldPropagateExampleWorkflowSynchronizationFailure() throws Exception {
        RobotExecute robot = robot("robot-5", "Example Failure", 1);
        when(robotExecuteDao.getExpoUserRobotId("Example Failure", "example-user"))
                .thenReturn("example-robot-5");
        when(executorModeHandler.getParamInside(any(QueryParamDto.class), eq("user-5"), eq("tenant-5")))
                .thenReturn(emptyParameters());
        when(restTemplate.exchange(eq(UPSERT_URL), eq(HttpMethod.POST), any(HttpEntity.class), eq(String.class)))
                .thenThrow(new ResourceAccessException("unreachable"));

        assertThrows(
                ResourceAccessException.class,
                () -> ReflectionTestUtils.invokeMethod(service, "sendOpenApiRequest", robot, "user-5", "tenant-5"));
    }

    @Test
    void shouldCreateDefaultRestTemplate() {
        assertNotNull(new SampleUsersServiceImpl().createRestTemplate());
    }

    @SuppressWarnings("unchecked")
    private HttpEntity<String> captureRequest(String expectedUserId) {
        ArgumentCaptor<HttpEntity<String>> requestCaptor = ArgumentCaptor.forClass(HttpEntity.class);
        verify(restTemplate).exchange(eq(UPSERT_URL), eq(HttpMethod.POST), requestCaptor.capture(), eq(String.class));
        HttpEntity<String> request = requestCaptor.getValue();
        assertEquals("application/json", request.getHeaders().getContentType().toString());
        assertEquals(expectedUserId, request.getHeaders().getFirst("user_id"));
        return request;
    }

    private void stubSuccessfulPost() {
        when(restTemplate.exchange(eq(UPSERT_URL), eq(HttpMethod.POST), any(HttpEntity.class), eq(String.class)))
                .thenReturn(ResponseEntity.ok("{}"));
    }

    private AppResponse<List<ParamDto>> emptyParameters() {
        return AppResponse.success(Collections.emptyList());
    }

    private RobotExecute robot(String robotId, String name, int version) {
        RobotExecute robot = new RobotExecute();
        robot.setRobotId(robotId);
        robot.setName(name);
        robot.setRobotVersion(version);
        return robot;
    }
}
