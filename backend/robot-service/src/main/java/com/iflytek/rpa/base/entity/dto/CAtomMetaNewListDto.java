package com.iflytek.rpa.base.entity.dto;

import java.util.List;
import javax.validation.constraints.NotEmpty;
import lombok.Data;

/**
 * 新原子能力查询DTO
 */
@Data
public class CAtomMetaNewListDto {

    @NotEmpty(message = "keys不能为空")
    private List<String> keys;
}
