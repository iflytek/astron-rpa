package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotNull;
import java.util.List;

/**
 * 共享文件批量删除DTO
 */
@Data
public class SharedFileBatchDeleteDto {
    /**
     * 共享文件ID List
     */
    @NotNull(message = "共享文件ID-List不能为空")
    private List<String> fileIds;

}
