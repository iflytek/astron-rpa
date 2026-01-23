package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.Org;
import com.iflytek.sec.uap.client.core.dto.org.UapOrg;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * Org映射器
 * 用于将UAP客户端的UapOrg转换为core包下的Org
 *
 * @author xqcao2
 */
@Component
public class OrgMapper {

    /**
     * 将UAP客户端的UapOrg转换为核心实体Org
     *
     * @param uapOrg UAP客户端的UapOrg
     * @return core包下的Org
     */
    public Org fromUapOrg(UapOrg uapOrg) {
        if (uapOrg == null) {
            return null;
        }

        Org org = new Org();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(uapOrg, org);

        return org;
    }

    /**
     * 批量将UAP客户端的UapOrg列表转换为核心实体Org列表
     *
     * @param uapOrgs UAP客户端的UapOrg列表
     * @return core包下的Org列表
     */
    public List<Org> fromUapOrgs(List<UapOrg> uapOrgs) {
        if (uapOrgs == null || uapOrgs.isEmpty()) {
            return Collections.emptyList();
        }

        return uapOrgs.stream().map(this::fromUapOrg).filter(org -> org != null).collect(Collectors.toList());
    }
}
