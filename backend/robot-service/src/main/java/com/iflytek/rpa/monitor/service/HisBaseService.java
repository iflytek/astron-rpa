package com.iflytek.rpa.monitor.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.iflytek.rpa.monitor.entity.HisBase;
import com.iflytek.rpa.monitor.entity.HisDataEnum;
import com.iflytek.rpa.monitor.entity.dto.BaseDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.text.ParseException;
import java.util.List;

public interface HisBaseService extends IService<HisBase> {

    AppResponse<List<HisDataEnum>> sourceData(BaseDto baseDto) throws ParseException, NoLoginException;

    AppResponse<List<HisDataEnum>> executeData(BaseDto baseDto) throws ParseException, NoLoginException;

    <T> List<HisDataEnum> getOverViewData(String parentCode, T hisCloudBase, Class<T> clazz);

    AppResponse<List<HisBase>> robotNumHistory(BaseDto baseDto) throws ParseException, NoLoginException;

    AppResponse<List<HisBase>> robotExecuteTimeHistory(BaseDto baseDto) throws ParseException, NoLoginException;

    AppResponse<List<HisBase>> robotExecuteNumAndSuccessRateHistory(BaseDto baseDto)
            throws ParseException, NoLoginException;

    AppResponse<List<HisBase>> laborSaveHistory(BaseDto baseDto) throws ParseException, NoLoginException;

    AppResponse<List<HisBase>> userNumHistory(BaseDto baseDto) throws ParseException, NoLoginException;

    AppResponse<List<HisBase>> terminalNumHistory(BaseDto baseDto) throws ParseException, NoLoginException;

    void setDataAuth(BaseDto baseDto);

    void insertBatch(List<HisBase> hisBaseList);
}
