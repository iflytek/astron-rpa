package com.iflytek.rpa.resource.file.entity.vo;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class ShareFileUploadVo {
    String fileId;
    Integer type; // 文件枚举类型编码
    String fileName; // 文件名
}
