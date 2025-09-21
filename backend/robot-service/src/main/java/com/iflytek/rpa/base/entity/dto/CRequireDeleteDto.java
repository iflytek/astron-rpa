package com.iflytek.rpa.base.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import java.util.List;

@Data
public class CRequireDeleteDto {
    @NotBlank
    private String robotId;

    private List<Integer> idList;

    private String creatorId;
}