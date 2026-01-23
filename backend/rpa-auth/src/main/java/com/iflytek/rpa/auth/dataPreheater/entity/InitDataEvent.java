package com.iflytek.rpa.auth.dataPreheater.entity;

import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.Setter;
import org.springframework.context.ApplicationEvent;

@Getter
@Setter
@EqualsAndHashCode(callSuper = true)
public class InitDataEvent extends ApplicationEvent {
    private String tenantId;

    public InitDataEvent(Object source, String tenantId) {
        super(source);
        this.tenantId = tenantId;
    }
}
