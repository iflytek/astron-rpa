package com.iflytek.rpa.auth.core.controller;

import com.iflytek.rpa.auth.core.entity.AddUserDto;
import com.iflytek.rpa.auth.idp.AuthenticationService;
import com.iflytek.rpa.auth.utils.AppResponse;
import javax.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 控制台-用户管理
 */
@RestController
@Slf4j
@RequiredArgsConstructor
@RequestMapping("/user-manage")
public class UserManageController {

    @Autowired
    private AuthenticationService authenticationService;

    @Autowired
    private ApplicationEventPublisher eventPublisher;

    @PostMapping("/add")
    public AppResponse<String> addUser(@RequestBody @Validated AddUserDto user, HttpServletRequest request) {
        return authenticationService.addUser(user, request);
    }
}
