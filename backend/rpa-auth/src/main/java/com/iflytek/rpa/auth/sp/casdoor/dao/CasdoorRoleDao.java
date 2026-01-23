package com.iflytek.rpa.auth.sp.casdoor.dao;

import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.casbin.casdoor.entity.Role;

/**
 * Casdoor 角色数据访问接口
 *
 * @author Auto Generated
 * @create 2025/12/17
 */
@Mapper
public interface CasdoorRoleDao {

    /**
     * 根据名称模糊查询角色
     *
     * @param keyword      关键字（角色名称）
     * @param owner        租户ID（organization name）
     * @param databaseName 数据库名称
     * @return 角色列表（Casdoor Role 实体）
     */
    List<Role> searchRoleByName(
            @Param("keyword") String keyword, @Param("owner") String owner, @Param("databaseName") String databaseName);
}
