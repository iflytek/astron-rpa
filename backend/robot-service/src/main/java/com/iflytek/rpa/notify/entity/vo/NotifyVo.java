package com.iflytek.rpa.notify.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

@Data
public class NotifyVo {
    Long id;
    String messageInfo;
    String messageType;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    // 操作结果，未读1， 已读2，已加入3，已拒绝4
    private Integer operateResult;

    String appName;

    String marketId;
}
