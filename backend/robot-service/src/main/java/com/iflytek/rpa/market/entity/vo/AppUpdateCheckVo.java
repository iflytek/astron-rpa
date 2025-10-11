package com.iflytek.rpa.market.entity.vo;

import lombok.Data;

@Data
public class AppUpdateCheckVo {
    String appId; // appId
    Integer updateStatus; // 0: 不提示更新 1: 提示更新
}
