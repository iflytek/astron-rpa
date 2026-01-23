package com.iflytek.rpa.market.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.market.entity.AppApplication;
import com.iflytek.rpa.market.entity.dto.MyApplicationPageListDto;
import com.iflytek.rpa.market.entity.vo.MyApplicationPageListVo;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface AppApplicationDao extends BaseMapper<AppApplication> {

    IPage<MyApplicationPageListVo> getMyApplicationPageList(
            IPage<MyApplicationPageListVo> pageConfig, @Param("entity") MyApplicationPageListDto queryDto);

    /**
     * 自动审批未审核的上架申请
     */
    int autoApproveReleaseApplications(@Param("tenantId") String tenantId, @Param("operator") String operator);

    /**
     * 逻辑删除开启阶段的所有审核申请记录
     */
    int deleteAuditRecords(@Param("tenantId") String tenantId, @Param("operator") String operator);

    AppApplication getApplicationByObtainedAppId(
            @Param("appId") String appId, @Param("tenantId") String tenantId, @Param("userId") String userId);

    AppApplication getLatestApplicationByRobotId(String robotId, String tenantId);

    List<String> getPendingMarketInfoJson(String tenantId);
}
