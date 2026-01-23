package com.iflytek.rpa.base.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.base.entity.dto.CParamDto;
import com.iflytek.rpa.base.entity.dto.CParamListDto;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import com.iflytek.rpa.base.entity.dto.QueryParamDto;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.List;
import javax.validation.Valid;

/**
 * 模板参数表服务接口
 * @author tzzhang
 * @since 2025-3-13
 */
public interface CParamService {

    /**
     * @param
     * @return
     */
    AppResponse<List<ParamDto>> getAllParams(QueryParamDto queryParamDto)
            throws JsonProcessingException, NoLoginException;

    /**
     * @param cParamDto
     * @return
     */
    AppResponse<String> addParam(CParamDto cParamDto) throws NoLoginException;

    /**
     * @param id
     * @return
     */
    AppResponse<Boolean> deleteParam(String id) throws NoLoginException;

    /**
     * @param cParamDto
     * @return
     */
    AppResponse<Boolean> updateParam(@Valid CParamDto cParamDto) throws NoLoginException;

    /**
     * @param cParamListDto
     * @return
     */
    AppResponse<Boolean> saveUserParam(CParamListDto cParamListDto) throws NoLoginException, JsonProcessingException;

    void createParamForCurrentVersion(String processId, RobotVersionDto robotVersionDto, Integer version);
}
