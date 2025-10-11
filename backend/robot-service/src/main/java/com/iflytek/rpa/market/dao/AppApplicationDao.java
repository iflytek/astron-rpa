package com.iflytek.rpa.market.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.market.entity.AppApplication;
import com.iflytek.rpa.market.entity.dto.MyApplicationPageListDto;
import com.iflytek.rpa.market.entity.dto.ReleasePageListDto;
import com.iflytek.rpa.market.entity.dto.UsePageListDto;
import com.iflytek.rpa.market.entity.vo.MyApplicationPageListVo;
import com.iflytek.rpa.market.entity.vo.ReleasePageListVo;
import com.iflytek.rpa.market.entity.vo.UsePageListVo;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface AppApplicationDao extends BaseMapper<AppApplication> {

    IPage<ReleasePageListVo> getReleasePageList(
            IPage<ReleasePageListVo> pageConfig, @Param("entity") ReleasePageListDto queryDto);

    IPage<UsePageListVo> getUsePageList(IPage<UsePageListVo> pageConfig, @Param("entity") UsePageListDto queryDto);

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

    AppApplication getApplicationByObtainedAppId(String appId, String tenantId);
}
