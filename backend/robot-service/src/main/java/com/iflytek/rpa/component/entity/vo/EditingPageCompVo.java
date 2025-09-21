package com.iflytek.rpa.component.entity.vo;

import lombok.Data;

/**
 * 编辑页的左侧渲染 componentVo
 */
@Data
public class EditingPageCompVo {
    String componentId; // 组件id
    String name; // 组件名称
    String icon; // 图标
    Integer isLatest; // 是否为最新 1 是 ， 0 否
}
