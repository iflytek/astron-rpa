package com.iflytek.rpa.monitor.dao;

import com.iflytek.rpa.monitor.entity.HisDataEnum;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 监控管理数据概览卡片配置数据枚举(HisDataEnum)表数据库访问层
 *
 * @author mjren
 * @since 2024-11-01 11:36:34
 */
@Mapper
public interface HisDataEnumDao {

    List<HisDataEnum> getEnumByParentCode(@Param("parentCode") String parentCode);
}

