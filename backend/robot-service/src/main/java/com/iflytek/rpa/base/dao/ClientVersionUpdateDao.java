package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.ClientUpdateVersion;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 客户端版本更新DAO接口
 *
 * @author system
 * @since 2025-01-XX
 */
@Mapper
public interface ClientVersionUpdateDao extends BaseMapper<ClientUpdateVersion> {

    /**
     * 根据版本号查询版本信息
     *
     * @param version 版本号
     * @return 版本实体
     */
    ClientUpdateVersion getByVersionNum(@Param("versionNum") Integer version);

    /**
     * 查询最新版本（versionNum最大）
     *
     * @param os 操作系统
     * @param arch 架构
     */
    ClientUpdateVersion getLatestVersion(@Param("os") String os, @Param("arch") String arch);

    /**
     * 查询全局最新版本（versionNum最大，不区分操作系统和架构）
     *
     * @return 最新版本信息
     */
    ClientUpdateVersion getGlobalLatestVersion();
}
