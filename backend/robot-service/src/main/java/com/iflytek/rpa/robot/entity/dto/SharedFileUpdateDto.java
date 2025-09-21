package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import java.util.List;

@Data
public class SharedFileUpdateDto {
    /**
     * 共享文件ID
     */
    @NotBlank(message = "文件ID不能为空")
    private Long fileId;

    /**
     * 文件名
     */
    @NotBlank(message = "文件名不能为空")
    private String fileName;

    /**
     * 标签/别名
     */
    private List<Long> tags;
}
