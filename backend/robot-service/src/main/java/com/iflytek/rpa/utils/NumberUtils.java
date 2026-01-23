package com.iflytek.rpa.utils;

import java.math.BigDecimal;

public class NumberUtils {

    public static BigDecimal getRate(BigDecimal num, BigDecimal totalNum) {
        if (totalNum.equals(BigDecimal.ZERO)) {
            return new BigDecimal(0);
        } else {
            num = num.multiply(new BigDecimal("100"));
            BigDecimal rate = num.divide(totalNum, 2, BigDecimal.ROUND_HALF_UP);
            return rate;
        }
    }

    public static BigDecimal DecimalDivide(BigDecimal num, BigDecimal totalNum) {
        if (totalNum.equals(BigDecimal.ZERO)) {
            return new BigDecimal(0);
        } else {
            BigDecimal rate = num.divide(totalNum, 2, BigDecimal.ROUND_HALF_UP);
            return rate;
        }
    }
}
