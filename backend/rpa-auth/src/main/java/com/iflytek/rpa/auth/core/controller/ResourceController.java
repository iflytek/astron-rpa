package com.iflytek.rpa.auth.core.controller;

import com.iflytek.rpa.auth.core.entity.Resource;
import com.iflytek.rpa.auth.core.service.ResourceService;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 资源权限
 */
@RestController
@RequestMapping("/resource")
public class ResourceController {

    @Autowired
    private ResourceService resourceService;

    /**
     * 当前登录用户在应用中的资源信息
     * @param request
     * @return
     */
    @GetMapping("/currentResourceList")
    public AppResponse<List<Resource>> getUserResourceList(HttpServletRequest request) {
        return resourceService.getUserResourceList(request);
    }
}
