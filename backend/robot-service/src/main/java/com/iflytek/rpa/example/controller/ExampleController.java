package com.iflytek.rpa.example.controller;

import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/example")
@Slf4j
public class ExampleController {
    @GetMapping("/insert")
    public void insertExample() {
        log.info("received hook");
    }
}
