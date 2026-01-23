package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.RoleBaseDto;
import com.iflytek.rpa.auth.core.entity.UapExtendRelation;
import com.iflytek.rpa.auth.core.entity.User;
import com.iflytek.rpa.auth.core.entity.UserExtendDto;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * UserExtendDto 映射器
 * 在 core 的 UserExtendDto 与 UAP 客户端的 UserExtendDto 之间转换
 *
 * 包含父类 TenantModeExtendDto 以及属性成员：
 * - user：UapUser <-> User（复用 UserMapper）
 * - extands：UapExtendRelation <-> UapExtendRelation（core）
 * - roles：RoleBaseDto（UAP）<-> RoleBaseDto（core）
 */
@Component
public class UserExtendDtoMapper {

    @Autowired
    private UserMapper userMapper;

    /**
     * UAP -> core 的 UserExtendDto 转换
     *
     * @param uapUserExtendDto UAP 的 UserExtendDto
     * @return core 的 UserExtendDto
     */
    public UserExtendDto fromUapUserExtendDto(com.iflytek.sec.uap.client.core.dto.user.UserExtendDto uapUserExtendDto) {
        if (uapUserExtendDto == null) {
            return null;
        }

        UserExtendDto userExtendDto = new UserExtendDto();
        // 复制父类 TenantModeExtendDto 字段（tenantId、requestUrl 等）
        BeanUtils.copyProperties(uapUserExtendDto, userExtendDto);

        // user 字段：UapUser -> User（复用 UserMapper）
        UapUser uapUser = uapUserExtendDto.getUser();
        User coreUser = userMapper.fromUapUser(uapUser);
        userExtendDto.setUser(coreUser);

        // extands 字段：List<UapExtendRelation> (UAP) -> List<UapExtendRelation> (core)
        List<com.iflytek.sec.uap.client.core.dto.extand.UapExtendRelation> uapExtends = uapUserExtendDto.getExtands();
        if (uapExtends != null && !uapExtends.isEmpty()) {
            List<UapExtendRelation> coreExtends =
                    uapExtends.stream().map(this::fromUapExtendRelation).collect(Collectors.toList());
            userExtendDto.setExtands(coreExtends);
        } else {
            userExtendDto.setExtands(Collections.emptyList());
        }

        // roles 字段：List<RoleBaseDto> (UAP) -> List<RoleBaseDto> (core)
        List<com.iflytek.sec.uap.client.core.dto.role.RoleBaseDto> uapRoles = uapUserExtendDto.getRoles();
        if (uapRoles != null && !uapRoles.isEmpty()) {
            List<RoleBaseDto> coreRoles =
                    uapRoles.stream().map(this::fromUapRoleBaseDto).collect(Collectors.toList());
            userExtendDto.setRoles(coreRoles);
        } else {
            userExtendDto.setRoles(Collections.emptyList());
        }

        return userExtendDto;
    }

    /**
     * core -> UAP 的 UserExtendDto 转换
     *
     * @param userExtendDto core 的 UserExtendDto
     * @return UAP 的 UserExtendDto
     */
    public com.iflytek.sec.uap.client.core.dto.user.UserExtendDto toUapUserExtendDto(UserExtendDto userExtendDto) {
        if (userExtendDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.user.UserExtendDto uapUserExtendDto =
                new com.iflytek.sec.uap.client.core.dto.user.UserExtendDto();
        // 复制父类 TenantModeExtendDto 字段（tenantId、requestUrl 等）
        BeanUtils.copyProperties(userExtendDto, uapUserExtendDto);

        // user 字段：User -> UapUser（通过 BeanUtils 简单复制）
        User coreUser = userExtendDto.getUser();
        if (coreUser != null) {
            UapUser uapUser = new UapUser();
            BeanUtils.copyProperties(coreUser, uapUser);
            uapUserExtendDto.setUser(uapUser);
        }

        // extands 字段：List<UapExtendRelation> (core) -> List<UapExtendRelation> (UAP)
        List<UapExtendRelation> coreExtends = userExtendDto.getExtands();
        if (coreExtends != null && !coreExtends.isEmpty()) {
            List<com.iflytek.sec.uap.client.core.dto.extand.UapExtendRelation> uapExtends =
                    coreExtends.stream().map(this::toUapExtendRelation).collect(Collectors.toList());
            uapUserExtendDto.setExtands(uapExtends);
        }

        // roles 字段：List<RoleBaseDto> (core) -> List<RoleBaseDto> (UAP)
        List<RoleBaseDto> coreRoles = userExtendDto.getRoles();
        if (coreRoles != null && !coreRoles.isEmpty()) {
            List<com.iflytek.sec.uap.client.core.dto.role.RoleBaseDto> uapRoles =
                    coreRoles.stream().map(this::toUapRoleBaseDto).collect(Collectors.toList());
            uapUserExtendDto.setRoles(uapRoles);
        }

        return uapUserExtendDto;
    }

    /**
     * UAP 的 UapExtendRelation -> core 的 UapExtendRelation
     */
    private UapExtendRelation fromUapExtendRelation(
            com.iflytek.sec.uap.client.core.dto.extand.UapExtendRelation uapExtendRelation) {
        if (uapExtendRelation == null) {
            return null;
        }

        UapExtendRelation coreRelation = new UapExtendRelation();
        // 包含父类 UapExtand 和 TenantModeExtendDto 的字段
        BeanUtils.copyProperties(uapExtendRelation, coreRelation);
        return coreRelation;
    }

    /**
     * core 的 UapExtendRelation -> UAP 的 UapExtendRelation
     */
    private com.iflytek.sec.uap.client.core.dto.extand.UapExtendRelation toUapExtendRelation(
            UapExtendRelation coreRelation) {
        if (coreRelation == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.extand.UapExtendRelation uapRelation =
                new com.iflytek.sec.uap.client.core.dto.extand.UapExtendRelation();
        BeanUtils.copyProperties(coreRelation, uapRelation);
        return uapRelation;
    }

    /**
     * UAP 的 RoleBaseDto -> core 的 RoleBaseDto
     */
    private RoleBaseDto fromUapRoleBaseDto(com.iflytek.sec.uap.client.core.dto.role.RoleBaseDto uapRoleBaseDto) {
        if (uapRoleBaseDto == null) {
            return null;
        }

        RoleBaseDto coreRoleBaseDto = new RoleBaseDto();
        BeanUtils.copyProperties(uapRoleBaseDto, coreRoleBaseDto);
        return coreRoleBaseDto;
    }

    /**
     * core 的 RoleBaseDto -> UAP 的 RoleBaseDto
     */
    private com.iflytek.sec.uap.client.core.dto.role.RoleBaseDto toUapRoleBaseDto(RoleBaseDto coreRoleBaseDto) {
        if (coreRoleBaseDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.role.RoleBaseDto uapRoleBaseDto =
                new com.iflytek.sec.uap.client.core.dto.role.RoleBaseDto();
        BeanUtils.copyProperties(coreRoleBaseDto, uapRoleBaseDto);
        return uapRoleBaseDto;
    }
}
