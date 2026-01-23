package com.iflytek.rpa.market.entity.vo;

import com.iflytek.rpa.utils.response.QuotaCodeEnum;
import lombok.Data;

@Data
public class AcceptResultVo {
    /**
     * S_SUCCESS("000", "成功"),
     * S_REPEAT_JOIN("001", "重复加入"),
     * E_OVER_LIMIT("101", "超出上限"),
     * E_EXPIRE("102", "失效");
     */
    String resultCode;

    public AcceptResultVo(QuotaCodeEnum codeEnum) {
        this.resultCode = codeEnum.getResultCode();
    }

    public AcceptResultVo() {
        resultCode = null;
    }
}
