package com.iflytek.rpa.utils.response;

public enum QuotaCodeEnum {
    S_SUCCESS("000", "成功"),

    S_REPEAT_JOIN("001", "重复加入"),

    E_OVER_MARKET_USER_NUM_LIMIT("100", "超出市场人数上限"),

    E_OVER_LIMIT("101", "超出上限"),

    E_EXPIRE("102", "失效");

    private String resultCode;

    private String msg;

    QuotaCodeEnum(String resultCode, String msg) {
        this.resultCode = resultCode;
        this.msg = msg;
    }

    public String getResultCode() {
        return resultCode;
    }

    public String getMsg() {
        return msg;
    }
}
