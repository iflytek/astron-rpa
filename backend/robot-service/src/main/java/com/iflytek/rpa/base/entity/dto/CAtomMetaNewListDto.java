package com.iflytek.rpa.base.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotEmpty;
import java.util.List;

/**
 * 新原子能力查询DTO
 */
@Data
public class CAtomMetaNewListDto {

    @NotEmpty(message = "keys不能为空")
    private List<String> keys;
}
