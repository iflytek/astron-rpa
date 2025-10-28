package com.iflytek.rpa.example.controller;

import com.iflytek.rpa.example.service.SampleUsersService;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.utils.UserUtils;
import java.io.IOException;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.casbin.casdoor.entity.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/example")
@Slf4j
public class ExampleController {

    @Autowired
    SampleUsersService sampleUsersService;

    @PostMapping("/insert")
    public AppResponse<Boolean> insertExample(@RequestBody Map<String, Object> requestBody) throws IOException {
        log.info("received hook with request body: {}", requestBody);

        // get hook info
        if (!requestBody.containsKey("organization") || !requestBody.containsKey("user"))
            throw new ServiceException("hook body from cas-door is missing");
        String name = (String) requestBody.get("user");
        String tenantId = (String) requestBody.get("organization");

        // get user by casdoor api
        User user = UserUtils.getUserByName(name);
        if (user == null) throw new ServiceException("fail to get casdoor user by name");

        // insert sample
        return sampleUsersService.insertUserSample(user.id, tenantId);
    }
}
