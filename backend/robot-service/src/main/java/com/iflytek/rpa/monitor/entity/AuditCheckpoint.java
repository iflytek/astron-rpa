package com.iflytek.rpa.monitor.entity;

import java.util.Date;

/**
 * @author mjren
 * @date 2025-01-14 17:34
 * @copyright Copyright (c) 2025 mjren
 */
public class AuditCheckpoint {

    private Long id;

    private String auditObjectType;

    private String lastProcessedId;

    private String auditStatus;

    private Date countTime;

    private Date updateTime;

    private Integer deleted;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getAuditObjectType() {
        return auditObjectType;
    }

    public void setAuditObjectType(String auditObjectType) {
        this.auditObjectType = auditObjectType;
    }

    public String getLastProcessedId() {
        return lastProcessedId;
    }

    public void setLastProcessedId(String lastProcessedId) {
        this.lastProcessedId = lastProcessedId;
    }

    public String getAuditStatus() {
        return auditStatus;
    }

    public void setAuditStatus(String auditStatus) {
        this.auditStatus = auditStatus;
    }

    public Date getCountTime() {
        return countTime;
    }

    public void setCountTime(Date countTime) {
        this.countTime = countTime;
    }

    public Date getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(Date updateTime) {
        this.updateTime = updateTime;
    }

    public Integer getDeleted() {
        return deleted;
    }

    public void setDeleted(Integer deleted) {
        this.deleted = deleted;
    }
}
