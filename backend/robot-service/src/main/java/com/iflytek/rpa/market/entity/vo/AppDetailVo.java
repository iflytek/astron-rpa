package com.iflytek.rpa.market.entity.vo;

import lombok.Data;

import java.util.List;

@Data
public class AppDetailVo {
    String iconUrl;
    String appName;
    Long downloadNum;
    Long checkNum;
    String introduction;
    String videoPath;

    // 基本信息
    String creatorName;
    String category;
    String fileName;
    String filePath;

    // 使用说明
    String useDescription;

    // 版本信息
    List<AppDetailVersionInfo> versionInfoList;
}
