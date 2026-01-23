package com.iflytek.rpa.base.entity.dto;

import lombok.Data;

import java.util.List;

@Data
public class AtomListDto {
    // 列表
    private List<Atom> atomList;

    @Data
    public static class Atom {
        private String key;
        private String version;
    }
}