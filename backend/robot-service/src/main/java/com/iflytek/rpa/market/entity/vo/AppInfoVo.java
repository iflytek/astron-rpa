package com.iflytek.rpa.market.entity.vo;

import java.util.Date;
import lombok.Data;

@Data
public class AppInfoVo {
    String appName;
    Long downloadNum;
    Long checkNum;
    String appIntro; // 应用介绍
    Integer allowOperate; // 操作按钮显隐 0 不允许 ； 1 允许
    Integer obtainStatus; // 0: 获取 1: 重新获取
    Integer updateStatus; // 0: 不提示更新 1: 提示更新
    String appId;
    String marketId;
    String resourceUuid; // 对应自己的resourceId，如果没有获取这个字段就为空
    String iconUrl; // 应用图标
    String securityLevel; // 密级标识
    Date expiryDate; // 红色密级标识的截止时间
    String expiryDateStr; // 红色密级标识的截止时间提示
    private Boolean editFlag;
}
