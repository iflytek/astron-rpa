package com.iflytek.rpa.monitor.service.impl;

import com.iflytek.rpa.monitor.dao.HisDataEnumDao;
import com.iflytek.rpa.monitor.entity.HisDataEnum;
import com.iflytek.rpa.monitor.service.HisDataEnumService;
import java.lang.reflect.Field;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.annotation.Resource;
import org.springframework.stereotype.Service;
import org.springframework.util.ReflectionUtils;

/**
 * 监控管理数据概览卡片配置数据枚举(HisDataEnum)表服务实现类
 *
 * @author mjren
 * @since 2024-11-01 11:36:36
 */
@Service("hisDataEnumService")
public class HisDataEnumServiceImpl implements HisDataEnumService {
    @Resource
    private HisDataEnumDao hisDataEnumDao;

    public <T> List<HisDataEnum> getOverViewData(String parentCode, T valueEntity, Class<T> valueClaZZ) {
        List<HisDataEnum> hisDataEnumList = hisDataEnumDao.getEnumByParentCode(parentCode);
        for (HisDataEnum hisDataEnum : hisDataEnumList) {
            String percent = hisDataEnum.getPercent();
            if (null != percent) {
                doReplaceFormate(percent, hisDataEnum, valueEntity, valueClaZZ);
            }
            String propertyName = hisDataEnum.getField();
            // 从HisCloudBase找到propertyName字段
            Field field = ReflectionUtils.findField(valueClaZZ, propertyName);
            if (null != field) {
                field.setAccessible(true);
                // 从HisCloudBase找到propertyName字段的值
                Object value = null;
                if (null != valueEntity) {
                    value = ReflectionUtils.getField(field, valueEntity);
                }
                // 设置值
                hisDataEnum.setNum(value == null ? "0" : value.toString());
            }
        }
        //        hisDataEnumList.sort(Comparator.comparing(HisDataEnum::getOrder));
        return hisDataEnumList;
    }

    public <T> void doReplaceFormate(String percent, HisDataEnum hisDataEnum, T valueEntity, Class<T> valueClaZZ) {
        StringBuffer sb = new StringBuffer();
        String template = "\\{\\w+\\}";
        Matcher m = Pattern.compile(template).matcher(percent);
        if (m.find()) {
            String param = m.group();
            String propertyName = param.substring(1, param.length() - 1);
            Field field = ReflectionUtils.findField(valueClaZZ, propertyName);
            if (null != field) {
                field.setAccessible(true);
                Object value = ReflectionUtils.getField(field, valueEntity);
                m.appendReplacement(sb, value == null ? "0" : value.toString());
            }
        }
        m.appendTail(sb);
        hisDataEnum.setPercent(sb.toString());
    }
}
