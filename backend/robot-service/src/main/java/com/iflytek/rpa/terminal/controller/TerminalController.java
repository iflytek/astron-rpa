package com.iflytek.rpa.terminal.controller;

import com.iflytek.rpa.base.annotation.NoApiLog;
import com.iflytek.rpa.terminal.entity.dto.BeatDto;
import com.iflytek.rpa.terminal.entity.dto.RegistryDto;
import com.iflytek.rpa.terminal.service.TerminalService;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import javax.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 终端信息
 */
@RestController
@RequestMapping("/terminal")
public class TerminalController {

    @Autowired
    private TerminalService terminalService;

    /**
     * 注册终端信息
     * @param registryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/register")
    public AppResponse<String> registry(@RequestBody @Valid RegistryDto registryDto) throws NoLoginException {

        return terminalService.registry(registryDto);
    }

    /**
     * 终端指标数据-心跳
     * @param beatDto
     * @return
     */
    @NoApiLog("轮询接口-终端心跳")
    @PostMapping("/beat")
    public AppResponse<String> processBeat(@RequestBody BeatDto beatDto) {

        return terminalService.processBeat(beatDto);
    }
}
