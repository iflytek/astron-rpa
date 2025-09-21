package com.iflytek.rpa.component.entity.vo;

import lombok.Data;

@Data
public class CompManageVo {
    String componentId;
    String name;
    String icon;
    String introduction;
    Integer version; // 版本
    Integer latestVersion; // 最新版本
    Integer blocked; // 是否安装 1 是： 0 否  （渲染“移除” 和 “安装” 按钮）
    Integer isLatest; // 是否是最新版本 1 是：0 否
}
