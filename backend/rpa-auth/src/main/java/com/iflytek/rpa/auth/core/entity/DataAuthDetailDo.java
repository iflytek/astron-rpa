package com.iflytek.rpa.auth.core.entity;

import lombok.Data;

import java.util.List;

@Data
public class DataAuthDetailDo {
    /**
     * all、in_dept、onlyself、checked_dept
     */
    private String dataAuthType;

    private List<String> deptIdList;

    private List<String> deptIdPathList;
}
