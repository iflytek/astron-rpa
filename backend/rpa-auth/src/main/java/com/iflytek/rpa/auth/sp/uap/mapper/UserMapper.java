package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.User;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * User映射器
 * 用于将UAP客户端的UapUser转换为core包下的User
 *
 * @author xqcao2
 */
@Component
public class UserMapper {

    /**
     * 将UAP客户端的UapUser转换为核心实体User
     *
     * @param uapUser UAP客户端的UapUser
     * @return core包下的User
     */
    public User fromUapUser(UapUser uapUser) {
        if (uapUser == null) {
            return null;
        }

        User user = new User();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(uapUser, user);

        return user;
    }

    /**
     * 批量将UAP客户端的UapUser列表转换为核心实体User列表
     *
     * @param uapUsers UAP客户端的UapUser列表
     * @return core包下的User列表
     */
    public List<User> fromUapUsers(List<UapUser> uapUsers) {
        if (uapUsers == null || uapUsers.isEmpty()) {
            return Collections.emptyList();
        }

        return uapUsers.stream()
                .map(this::fromUapUser)
                .filter(user -> user != null)
                .collect(Collectors.toList());
    }
}
