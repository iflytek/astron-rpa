package com.iflytek.rpa.monitor.service;

import com.iflytek.rpa.monitor.entity.HisDataEnum;
import java.util.List;

/**
 * 监控管理数据概览卡片配置数据枚举(HisDataEnum)表服务接口
 *
 * @author mjren
 * @since 2024-11-01 11:36:34
 */
public interface HisDataEnumService {

    <T> List<HisDataEnum> getOverViewData(String parentCode, T hisCloudBase, Class<T> clazz);
}
