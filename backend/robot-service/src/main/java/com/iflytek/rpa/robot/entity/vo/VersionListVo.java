package com.iflytek.rpa.robot.entity.vo;

import com.baomidou.mybatisplus.core.metadata.IPage;
import lombok.Data;

@Data
public class VersionListVo {
    String sourceName;
    IPage<VersionInfo> ansPage;
}
