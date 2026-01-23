package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.SysVersionDefaultConfig;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

/**
 * 版本默认配置表 Mapper 接口
 */
@Mapper
public interface SysVersionDefaultConfigDao extends BaseMapper<SysVersionDefaultConfig> {

    /**
     * 根据版本ID查询所有默认配置
     */
    @Select("SELECT * FROM sys_version_default_config WHERE version_id = #{versionId} AND deleted = 0")
    List<SysVersionDefaultConfig> selectByVersionId(@Param("versionId") Long versionId);
}
