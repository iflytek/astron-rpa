package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.SysProductVersion;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

/**
 * 产品版本表 Mapper 接口
 */
@Mapper
public interface SysProductVersionDao extends BaseMapper<SysProductVersion> {

    /**
     * 根据版本代码查询版本信息
     */
    @Select("SELECT * FROM sys_product_version WHERE version_code = #{versionCode} AND deleted = 0 LIMIT 1")
    SysProductVersion selectByVersionCode(@Param("versionCode") String versionCode);
}
