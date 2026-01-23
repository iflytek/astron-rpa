package com.iflytek.rpa.base.controller;

import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CSmartComponentDto;
import com.iflytek.rpa.base.entity.vo.SmartComponentVo;
import com.iflytek.rpa.base.service.CSmartComponentService;
import com.iflytek.rpa.utils.response.AppResponse;
import javax.annotation.Resource;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/smart")
public class CSmartComponentController {
    @Resource
    private CSmartComponentService smartComponentService;

    @PostMapping("/save")
    public AppResponse<SmartComponentVo> save(@RequestBody CSmartComponentDto smartComponentDto) throws Exception {
        return smartComponentService.save(smartComponentDto);
    }

    @PostMapping("/detail/all")
    public AppResponse<SmartComponentVo> getBySmartId(@RequestBody CSmartComponentDto smartComponentDto)
            throws Exception {
        BaseDto baseDto = new BaseDto();
        baseDto.setMode(smartComponentDto.getMode());
        baseDto.setRobotId(smartComponentDto.getRobotId());
        baseDto.setRobotVersion(smartComponentDto.getRobotVersion());
        String smartId = smartComponentDto.getSmartId();

        return smartComponentService.getBySmartId(baseDto, smartId);
    }

    @PostMapping("/detail/version")
    public AppResponse<SmartComponentVo> getBySmartIdAndVersion(@RequestBody CSmartComponentDto smartComponentDto)
            throws Exception {
        BaseDto baseDto = new BaseDto();
        baseDto.setMode(smartComponentDto.getMode());
        baseDto.setRobotId(smartComponentDto.getRobotId());
        baseDto.setRobotVersion(smartComponentDto.getRobotVersion());
        String smartId = smartComponentDto.getSmartId();
        Integer version = smartComponentDto.getVersion();

        return smartComponentService.getBySmartIdAndVersion(baseDto, smartId, version);
    }

    @PostMapping("/delete")
    public AppResponse<Integer> delete(@RequestBody CSmartComponentDto smartComponentDto) throws Exception {
        return smartComponentService.delete(smartComponentDto);
    }
}
