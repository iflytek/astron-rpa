package com.iflytek.rpa.example.controller;

import com.iflytek.rpa.starter.exception.ServiceException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/example")
@Slf4j
public class ExampleController {
    @PostMapping("/insert")
    public void insertExample(@RequestBody Map<String, Object> requestBody) {
        log.info("received hook with request body: {}", requestBody);
        
        // 提取organization字段
        if (!requestBody.containsKey("organization") || !requestBody.containsKey("user"))
            throw new ServiceException("hook body from cas-door is missing");

        String user = (String) requestBody.get("user");
        String organization = (String) requestBody.get("organization");

        log.info(user + ":" + organization);
    }
}
