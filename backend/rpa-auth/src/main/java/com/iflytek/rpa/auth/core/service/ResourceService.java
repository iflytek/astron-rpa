package com.iflytek.rpa.auth.core.service;

import com.iflytek.rpa.auth.core.entity.Resource;
import com.iflytek.rpa.auth.utils.AppResponse;

import javax.servlet.http.HttpServletRequest;
import java.util.List;

/**
 * 资源权限服务
 */
public interface ResourceService {

    /**
     * 当前登录用户在应用中的资源信息
     * @param request HTTP请求
     * @return 资源列表
     */
    AppResponse<List<Resource>> getUserResourceList(HttpServletRequest request);
}

