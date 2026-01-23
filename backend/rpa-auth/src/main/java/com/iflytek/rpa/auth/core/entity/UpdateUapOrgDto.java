package com.iflytek.rpa.auth.core.entity;

import java.util.List;

/**
 * 创建机构DTO
 * @author xqcao2
 *
 */
public class UpdateUapOrgDto {

    /**
     * 机构信息
     */
    private UpdateOrgDto uapOrg;

    /**
     * 扩展信息
     */
    private List<UapExtendPropertyDto> extands;

    public UpdateOrgDto getUapOrg() {
        return uapOrg;
    }

    public void setUapOrg(UpdateOrgDto uapOrg) {
        this.uapOrg = uapOrg;
    }

    public List<UapExtendPropertyDto> getExtands() {
        return extands;
    }

    public void setExtands(List<UapExtendPropertyDto> extands) {
        this.extands = extands;
    }
}
