package com.iflytek.rpa.auth.auditRecord.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.auth.auditRecord.dao.AuditRecordDao;
import com.iflytek.rpa.auth.auditRecord.entity.AuditRecord;
import com.iflytek.rpa.auth.auditRecord.entity.enums.EventMoudleEnum;
import com.iflytek.rpa.auth.auditRecord.entity.enums.EventTypeEnum;
import com.iflytek.rpa.auth.auditRecord.service.AuditRecordService;
import com.iflytek.rpa.auth.exception.NoLoginException;
import com.iflytek.rpa.auth.sp.uap.utils.TenantUtils;
import com.iflytek.rpa.auth.sp.uap.utils.UserUtils;
import com.iflytek.rpa.auth.utils.StringUtils;
import java.util.Date;
import org.springframework.stereotype.Service;

/**
 * @author jqfang3
 * @since 2025-08-04
 */
@Service
public class AuditRecordServiceImpl extends ServiceImpl<AuditRecordDao, AuditRecord> implements AuditRecordService {
    @Override
    public void saveAuditRecord(String moduleName, String typeName, String message) throws NoLoginException {
        AuditRecord auditRecord = new AuditRecord();
        auditRecord.setEventModuleCode(EventMoudleEnum.getEnum(moduleName).getCode());
        auditRecord.setEventModuleName(
                String.valueOf(EventMoudleEnum.getEnum(moduleName).getName()));
        auditRecord.setEventTypeCode(EventTypeEnum.getEnum(typeName).getCode());
        auditRecord.setEventTypeName(
                String.valueOf(EventTypeEnum.getEnum(typeName).getName()));
        auditRecord.setEventDetail(message);
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        if (!StringUtils.isEmpty(userId) && !StringUtils.isEmpty(tenantId)) {
            auditRecord.setCreatorId(userId);
            auditRecord.setTenantId(tenantId);
            String userName = UserUtils.getLoginNameById(userId);
            auditRecord.setCreatorName(userName);
            auditRecord.setCreateTime(new Date());
            save(auditRecord);
        }
    }
}
