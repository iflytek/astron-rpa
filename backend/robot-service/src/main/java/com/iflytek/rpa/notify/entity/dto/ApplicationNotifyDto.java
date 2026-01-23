package com.iflytek.rpa.notify.entity.dto;
import lombok.Data;

@Data
public class ApplicationNotifyDto {
    String tenantId;
    String userId;
    String applicationType;
    String robotId;
    String status;
    String marketId;
}
