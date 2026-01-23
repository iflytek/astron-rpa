package com.iflytek.rpa.auth.auditRecord.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.iflytek.rpa.auth.auditRecord.entity.AuditRecord;
import com.iflytek.rpa.auth.exception.NoLoginException;

/**
 * @author jqfang3
 * @since 2025-08-04
 */
public interface AuditRecordService extends IService<AuditRecord> {
    void saveAuditRecord(String moduleName, String typeName, String message) throws NoLoginException;
}
