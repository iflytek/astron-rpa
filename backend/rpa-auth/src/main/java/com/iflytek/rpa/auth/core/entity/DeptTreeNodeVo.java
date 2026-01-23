package com.iflytek.rpa.auth.core.entity;

import lombok.Data;

/**
 * @author jqfang4
 * @date 2025-10-13
 */
@Data
public class DeptTreeNodeVo {
    private String id;
    private String name;
    private String pid;
    private Boolean hasNodes;
}
