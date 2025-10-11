package com.iflytek.rpa.monitor.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.monitor.entity.HisBase;
import com.iflytek.rpa.monitor.entity.dto.BaseDto;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 全部机器人和全部终端趋势表(HisCloudBase)表数据库访问层
 *
 * @author mjren
 * @since 2023-04-12 16:45:08
 */
@Mapper
public interface HisBaseDao extends BaseMapper<HisBase> {

    Integer insertBatch(@Param("entities") List<HisBase> hisBaseList);

    HisBase getBaseData(BaseDto baseDto);

    List<HisBase> robotNumHistory(BaseDto baseDto);

    List<HisBase> robotExecuteTimeHistory(BaseDto baseDto);

    List<HisBase> robotExecuteNumAndSuccessRateHistory(BaseDto baseDto);

    List<HisBase> laborSaveHistory(BaseDto baseDto);

    List<HisBase> userNumHistory(BaseDto baseDto);

    List<HisBase> terminalNumHistory(BaseDto baseDto);
}
