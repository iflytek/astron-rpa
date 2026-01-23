package com.iflytek.rpa.auth.blacklist.dto;

import java.io.Serializable;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 黑名单查询 DTO
 *
 * @author system
 * @date 2025-12-16
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class BlacklistQueryDto implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 用户ID（可选）
     */
    private String userId;

    /**
     * 用户名（可选）
     */
    private String username;

    /**
     * 状态（可选）1:生效中, 0:已解封
     */
    private Integer status;

    /**
     * 页码
     */
    private Integer pageNum = 1;

    /**
     * 每页数量
     */
    private Integer pageSize = 10;
}
