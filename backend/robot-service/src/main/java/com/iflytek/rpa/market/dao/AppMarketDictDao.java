package com.iflytek.rpa.market.dao;

import com.iflytek.rpa.market.entity.AppMarketDict;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * @author mjren
 * @date 2024-01-19 15:42
 * @copyright Copyright (c) 2024 mjren
 */
@Mapper
public interface AppMarketDictDao {

    List<AppMarketDict> getAppType();

    AppMarketDict getDictValueByCodeAndType(@Param("dictCode") String dictCode, @Param("userType") String  userType);

    String getCodeInfo(@Param("dictCode")  String dictCode);
}
