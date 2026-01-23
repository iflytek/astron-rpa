package com.iflytek.rpa.notify.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.iflytek.rpa.conf.LongJsonSerializer;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.Date;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class NotifySend implements Serializable {

    private static final long serialVersionUID = 3271461913224607218L;

    // 主键，主键自增
    @JsonSerialize(using = LongJsonSerializer.class) // 传给前端的时候使用LongJson的格式，防止id过长溢出
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    // 租户Id
    private String tenantId;

    // 用户Id
    private String userId;

    // 消息体Id
    private String messageInfo;

    // 消息类型，邀人消息teamMarketInvite，更新消息teamMarketUpdate
    private String messageType;

    // 操作结果，未读1， 已读2，已加入3，已拒绝4
    private Integer operateResult;

    // 市场id
    private String marketId;

    private String userType;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    // 逻辑删除
    @TableLogic(value = "0", delval = "1")
    private Integer deleted;

    private String appName;

}
