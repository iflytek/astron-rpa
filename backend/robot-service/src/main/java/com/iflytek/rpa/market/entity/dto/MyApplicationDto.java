package com.iflytek.rpa.market.entity.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class MyApplicationDto {
    @NotBlank
    String id;
}
