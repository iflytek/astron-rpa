package com.iflytek.rpa.auth.sp.casdoor.dao;

import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.casbin.casdoor.entity.Group;

/**
 * Casdoor 群组（部门）数据访问接口
 *
 * @author Auto Generated
 * @create 2025/12/11
 */
@Mapper
public interface CasdoorGroupDao {

    /**
     * 根据名称模糊查询群组（部门）
     *
     * @param keyword 关键字（部门名称）
     * @param owner 租户ID（organization name）
     * @param databaseName 数据库名称
     * @return 群组列表
     */
    List<Group> searchDeptByName(
            @Param("keyword") String keyword, @Param("owner") String owner, @Param("databaseName") String databaseName);
}
