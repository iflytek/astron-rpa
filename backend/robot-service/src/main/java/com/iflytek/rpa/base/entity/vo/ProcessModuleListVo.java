package com.iflytek.rpa.base.entity.vo;

import lombok.Data;

@Data
public class ProcessModuleListVo {
    String ResourceCategory; // 资源分类 ： 流程 ， 代码模块
    String name; // 资源名称
    String resourceId; // 资源id
}
