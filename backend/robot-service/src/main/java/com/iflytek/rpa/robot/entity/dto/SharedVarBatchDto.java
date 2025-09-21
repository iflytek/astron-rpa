package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotNull;
import java.util.List;

/**
 * 共享变量更新DTO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Data
public class SharedVarBatchDto {

    /**
     * 共享变量ID List
     */
    @NotNull(message = "共享变量ID-List不能为空")
    private List<Long> ids;
} 