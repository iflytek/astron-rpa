package com.iflytek.rpa.base.service;

import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CSmartComponentDto;
import com.iflytek.rpa.base.entity.dto.RenameModuleDto;
import com.iflytek.rpa.base.entity.vo.SmartComponentVo;
import com.iflytek.rpa.base.service.impl.CSmartComponentServiceImpl;
import com.iflytek.rpa.robot.entity.dto.SaveModuleDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;

import java.sql.SQLException;
import java.util.Map;

public interface CSmartComponentService {
    AppResponse<SmartComponentVo> save(CSmartComponentDto smartComponentDto) throws NoLoginException;

    AppResponse<SmartComponentVo> getBySmartId(BaseDto baseDto, String smartId) throws NoLoginException;

    AppResponse<SmartComponentVo> getBySmartIdAndVersion(BaseDto baseDto, String smartId, Integer version) throws NoLoginException;

    AppResponse<Integer> delete(CSmartComponentDto smartComponentDto) throws NoLoginException;
}
