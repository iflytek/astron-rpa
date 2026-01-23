package com.iflytek.rpa.market.entity.enums;

import lombok.Getter;

@Getter
public enum ExpireTypeEnum {
    FOUR_HOURS("4H", "4小时"),
    TWENTY_FOUR_HOURS("24H", "24小时"),
    SEVEN_DAYS("7D", "7天"),
    THIRTY_DAYS("30D", "30天"),
    ;

    private final String code;
    private final String name;

    ExpireTypeEnum(String code, String name) {
        this.code = code;
        this.name = name;
    }

    /**
     * 根据code获取枚举
     *
     * @param code 失效时间类型代码
     * @return 对应的枚举值，如果不存在则返回null
     */
    public static ExpireTypeEnum getByCode(String code) {
        if (code == null) {
            return null;
        }
        for (ExpireTypeEnum expireTypeEnum : values()) {
            if (expireTypeEnum.getCode().equalsIgnoreCase(code)) {
                return expireTypeEnum;
            }
        }
        return null;
    }
}
