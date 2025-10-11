package com.iflytek.rpa.market.entity.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class UseDeleteDto {
    @NotBlank
    String id;
}
