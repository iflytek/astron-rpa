package com.iflytek.rpa.dispatch.entity;

import com.iflytek.rpa.dispatch.entity.enums.DispatchTaskFromType;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RedisListBo {
    private String dispatchTaskId;
    private DispatchTaskFromType dispatchTaskFromType;
}
