package com.iflytek.rpa.auth.auditRecord.constants;

import com.iflytek.rpa.auth.auditRecord.entity.AuditRecord;
import com.iflytek.rpa.auth.auditRecord.entity.enums.EventMoudleEnum;
import com.iflytek.rpa.auth.auditRecord.entity.enums.EventTypeEnum;
import com.iflytek.rpa.auth.auditRecord.service.AuditRecordService;
import com.iflytek.rpa.auth.exception.NoLoginException;
import com.iflytek.rpa.auth.sp.uap.utils.TenantUtils;
import com.iflytek.rpa.auth.sp.uap.utils.UserUtils;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.lang.reflect.Method;
import java.util.Date;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.AfterReturning;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

/**
 * @author jqfang3
 * @since 2025-08-04
 */
@Aspect
@Component
public class AuditLogAop {

    @Autowired
    private AuditRecordService recordService;

    @Pointcut("@annotation(AuditLog)")
    public void logPoint() {}

    @AfterReturning(value = "logPoint()", returning = "res")
    @Transactional
    public void afterAop(JoinPoint joinPoint, AppResponse res) throws NoSuchMethodException, NoLoginException {
        Object target = joinPoint.getTarget();
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        Method method = target.getClass().getMethod(signature.getName(), signature.getParameterTypes());
        AuditLog annotation = method.getAnnotation(AuditLog.class);

        AuditRecord auditRecord = new AuditRecord();
        auditRecord.setEventModuleCode(
                EventMoudleEnum.getEnum(annotation.moduleName()).getCode());
        auditRecord.setEventModuleName(
                String.valueOf(EventMoudleEnum.getEnum(annotation.moduleName()).getName()));
        auditRecord.setEventTypeCode(
                EventTypeEnum.getEnum(annotation.typeName()).getCode());
        auditRecord.setEventTypeName(
                String.valueOf(EventTypeEnum.getEnum(annotation.typeName()).getName()));
        auditRecord.setEventDetail(res.getMessage());
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        if (!StringUtils.isEmpty(userId) && !StringUtils.isEmpty(tenantId)) {
            auditRecord.setCreatorId(userId);
            auditRecord.setTenantId(tenantId);
            String userName = UserUtils.getLoginNameById(userId);
            auditRecord.setCreatorName(userName);
            auditRecord.setCreateTime(new Date());
            recordService.save(auditRecord);
        }
    }
}
