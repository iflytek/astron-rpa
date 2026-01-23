package com.iflytek.rpa.monitor.dao;

import com.iflytek.rpa.terminal.entity.vo.UserVo;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface TenantDao {
    List<String> getAllTenantId(String databaseName);

    List<UserVo> getUserByTenantId(String databaseName, String tenantId, String userName);

    List<String> getManagerUserIds(String databaseName, String tenantId);

    List<String> getNormalUserIds(String databaseName, String tenantId);

    List<String> getAllEnterpriseTenantId(String databaseName);

    List<String> getAllTenantIdWithoutClassify(String databaseName);

    Integer updateTenantClassifyFlag(
            @Param("databaseName") String databaseName, @Param("tenantIds") List<String> tenantIds);
}
