package com.iflytek.rpa.utils;

import com.iflytek.rpa.auth.entity.CustomUserDetails;
import com.iflytek.rpa.starter.utils.StringUtils;
import java.util.Objects;
import javax.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.casbin.casdoor.entity.Group;
import org.casbin.casdoor.entity.User;
import org.casbin.casdoor.service.GroupService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

/**
 * @desc: 租户工具类
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/11 14:10
 */
@Component
@Slf4j
public class TenantUtils {

    @Autowired
    private GroupService groupService;

    // 静态变量，用于在静态方法中访问
    private static GroupService staticGroupService;

    @PostConstruct
    public void init() {
        staticGroupService = this.groupService;
    }

    /**
     * 获取当前登录租户ID
     *
     * @return 租户ID
     */
    public static String getTenantId() {
        // 从Spring Security上下文获取当前用户
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.getPrincipal() instanceof CustomUserDetails) {
            CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
            User user = userDetails.getUser();
            if (Objects.nonNull(user)) {
                return user.owner;
            }
            return null;
        }
        return null;
    }

    /**
     * 获取当前登录用户的群组ID
     *
     * @return
     */
    public static String getGroupId() {
        // 从Spring Security上下文获取当前用户
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.getPrincipal() instanceof CustomUserDetails) {
            CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
            User user = userDetails.getUser();
            if (Objects.nonNull(user)) {
                Group groupInfo = getGroupInfoByName(user.name);
                if (Objects.isNull(groupInfo)) {
                    return null;
                }
                return groupInfo.name;
            }
            return null;
        }
        return null;
    }

    /**
     * 根据名字（组织/名字=ID）获取群组信息
     *
     * @param name
     * @return
     */
    public static Group getGroupInfoByName(String name) {
        if (Objects.isNull(staticGroupService) || StringUtils.isEmpty(name)) {
            return null;
        }

        try {
            return staticGroupService.getGroup(name);
        } catch (Exception e) {
            log.error("根据用户名字获取用户群组信息失败: {}", name, e);
            return null;
        }
    }
}
