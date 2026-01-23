package com.iflytek.rpa.example.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.utils.response.AppResponse;

/**
 * 用户从系统模板中注入的样例数据(SampleUsers)表服务接口
 *
 * @author makejava
 * @since 2024-12-19
 */
public interface SampleUsersService {
    AppResponse<Boolean> insertUserSample(String userId, String tenantId);

    void sendOpenApi(String robotId, Integer version, String userId, String tenantId) throws JsonProcessingException;
}
