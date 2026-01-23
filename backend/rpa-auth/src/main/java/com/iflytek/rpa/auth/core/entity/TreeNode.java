package com.iflytek.rpa.auth.core.entity;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/11/28 9:51
 */
public class TreeNode implements Serializable {

    /**
     *
     */
    private static final long serialVersionUID = 1L;

    private String id;

    private String appId;

    private String appName;
    private String name;
    private String pid;
    private String firstLevelId;
    private Integer sort;
    private String value;
    private String deptType;
    private String code;

    private Boolean hasNodes;

    private String status;

    private Boolean checked;

    private List<TreeNode> nodes = new ArrayList<>();

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getAppId() {
        return appId;
    }

    public void setAppId(String appId) {
        this.appId = appId;
    }

    public String getAppName() {
        return appName;
    }

    public void setAppName(String appName) {
        this.appName = appName;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPid() {
        return pid;
    }

    public void setPid(String pid) {
        this.pid = pid;
    }

    public String getFirstLevelId() {
        return firstLevelId;
    }

    public void setFirstLevelId(String firstLevelId) {
        this.firstLevelId = firstLevelId;
    }

    public Integer getSort() {
        return sort;
    }

    public void setSort(Integer sort) {
        this.sort = sort;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getDeptType() {
        return deptType;
    }

    public void setDeptType(String deptType) {
        this.deptType = deptType;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public Boolean getHasNodes() {
        return hasNodes;
    }

    public void setHasNodes(Boolean hasNodes) {
        this.hasNodes = hasNodes;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Boolean getChecked() {
        return checked;
    }

    public void setChecked(Boolean checked) {
        this.checked = checked;
    }

    public List<TreeNode> getNodes() {
        return nodes;
    }

    public void setNodes(List<TreeNode> nodes) {
        this.nodes = nodes;
    }
}
