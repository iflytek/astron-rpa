package com.iflytek.rpa.quota.service;

public interface QuotaCheckService {

    /**
     * 检查设计器数量配额
     * @return true表示未超限，false表示已超限
     */
    boolean checkDesignerQuota();

    /**
     * 检查市场加入数量配额
     * @return true表示未超限，false表示已超限
     */
    boolean checkMarketJoinQuota();
}
