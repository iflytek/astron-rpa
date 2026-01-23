package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.Authority;
import com.iflytek.sec.uap.client.core.dto.authority.UapAuthority;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * Authority映射器
 * 用于将UAP客户端的UapAuthority转换为core包下的Authority
 *
 * @author xqcao2
 */
@Component
public class AuthorityMapper {

    /**
     * 将UAP客户端的UapAuthority转换为核心实体Authority
     *
     * @param uapAuthority UAP客户端的UapAuthority
     * @return core包下的Authority
     */
    public Authority fromUapAuthority(UapAuthority uapAuthority) {
        if (uapAuthority == null) {
            return null;
        }

        Authority authority = new Authority();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(uapAuthority, authority);

        return authority;
    }

    /**
     * 批量将UAP客户端的UapAuthority列表转换为核心实体Authority列表
     *
     * @param uapAuthorities UAP客户端的UapAuthority列表
     * @return core包下的Authority列表
     */
    public List<Authority> fromUapAuthorities(List<UapAuthority> uapAuthorities) {
        if (uapAuthorities == null || uapAuthorities.isEmpty()) {
            return Collections.emptyList();
        }

        return uapAuthorities.stream()
                .map(this::fromUapAuthority)
                .filter(authority -> authority != null)
                .collect(Collectors.toList());
    }
}
