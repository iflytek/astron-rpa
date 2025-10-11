package com.iflytek.rpa.monitor.dao;

/**
 * @author mjren
 * @date 2025-01-14 17:39
 * @copyright Copyright (c) 2025 mjren
 */
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.monitor.entity.AuditCheckpoint;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface AuditCheckpointDao extends BaseMapper<AuditCheckpoint> {

    Integer insertTaskForYesterday(AuditCheckpoint auditCheckpoint);

    List<AuditCheckpoint> getUnFinishedAuditTask(
            @Param("auditObjectType") String auditObjectType, @Param("startAndEndOfDay") List<String> startAndEndOfDay);

    Integer updateAuditCheckpoint(AuditCheckpoint auditCheckpoint);
}
