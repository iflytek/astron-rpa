package com.iflytek.rpa.market.entity.vo;

import java.util.List;
import lombok.Data;

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
