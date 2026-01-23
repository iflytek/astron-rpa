package com.iflytek.rpa.common.feign.entity;

import lombok.Data;

/**
 * @author jqfang4
 * @date 2025-10-13
 */
@Data
public class DeptPersonTreeNodeVo extends DeptTreeNodeVo {
    private Integer userNum;
    private String userName;
}
