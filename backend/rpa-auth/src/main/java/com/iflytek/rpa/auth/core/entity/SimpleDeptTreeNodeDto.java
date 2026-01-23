package com.iflytek.rpa.auth.core.entity;

import java.util.ArrayList;
import java.util.List;
import lombok.Data;

/**
 * 简化的部门树节点DTO - 仅包含必要字段以优化性能
 * @author AI Assistant
 * @date 2025-09-24
 */
@Data
public class SimpleDeptTreeNodeDto {

    /**
     * 部门ID
     */
    private String id;

    /**
     * 部门名称
     */
    private String name;

    /**
     * 父部门ID
     */
    private String pid;

    /**
     * 部门人数
     */
    private Long userNum;

    /**
     * 部门负责人名称
     */
    private String userName;

    /**
     * 组织ID（等同于id字段，为了兼容前端）
     */
    private String orgId;

    /**
     * 子部门列表
     */
    private List<SimpleDeptTreeNodeDto> nodes = new ArrayList<>();

    public SimpleDeptTreeNodeDto() {}

    public SimpleDeptTreeNodeDto(String id, String name, String pid, Long userNum, String userName) {
        this.id = id;
        this.orgId = id; // orgId与id保持一致
        this.name = name;
        this.pid = pid;
        this.userNum = userNum;
        this.userName = userName;
    }
}
