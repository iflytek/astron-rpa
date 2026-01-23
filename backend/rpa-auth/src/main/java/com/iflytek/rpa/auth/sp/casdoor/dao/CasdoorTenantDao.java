package com.iflytek.rpa.auth.sp.casdoor.dao;

import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * Casdoor 租户数据访问接口
 *
 * @author Auto Generated
 * @create 2025/12/11
 */
@Mapper
public interface CasdoorTenantDao {

    /**
     * 获取未分类的租户ID列表
     *
     * @param databaseName 数据库名称
     * @return 未分类的租户ID列表
     */
    List<String> getNoClassifyTenantIds(@Param("databaseName") String databaseName);
}
