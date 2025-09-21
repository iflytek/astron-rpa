package com.iflytek.rpa.component.entity.vo;

import lombok.Data;

/**
 * 机器人编辑页，组件详情VO
 */
@Data
public class EditingPageCompInfoVo {
    String componentId; // 组件id
    String name; // 组件名称
    String introduction; // 组件简介
    Integer version; // "V" + Integer version
    Integer latestVersion; // "V" + Integer latestVersion
    Integer isLatest; // 1 是，0 否
}
