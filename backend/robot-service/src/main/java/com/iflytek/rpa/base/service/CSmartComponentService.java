package com.iflytek.rpa.base.service;

import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CSmartComponentDto;
import com.iflytek.rpa.base.entity.vo.SmartComponentVo;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;

public interface CSmartComponentService {
    AppResponse<SmartComponentVo> save(CSmartComponentDto smartComponentDto) throws NoLoginException;

    AppResponse<SmartComponentVo> getBySmartId(BaseDto baseDto, String smartId) throws NoLoginException;

    AppResponse<SmartComponentVo> getBySmartIdAndVersion(BaseDto baseDto, String smartId, Integer version)
            throws NoLoginException;

    AppResponse<Integer> delete(CSmartComponentDto smartComponentDto) throws NoLoginException;
}
