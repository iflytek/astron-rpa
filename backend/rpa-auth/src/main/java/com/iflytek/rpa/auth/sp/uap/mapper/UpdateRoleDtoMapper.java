package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.UpdateRoleDto;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * UpdateRoleDto映射器
 * 用于将core包下的UpdateRoleDto转换为UAP客户端的UpdateRoleDto
 *
 * @author xqcao2
 */
@Component
public class UpdateRoleDtoMapper {

    /**
     * 将core包下的UpdateRoleDto转换为UAP客户端的UpdateRoleDto
     *
     * @param updateRoleDto core包下的UpdateRoleDto
     * @return UAP客户端的UpdateRoleDto
     */
    public com.iflytek.sec.uap.client.core.dto.role.UpdateRoleDto toUapUpdateRoleDto(UpdateRoleDto updateRoleDto) {
        if (updateRoleDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.role.UpdateRoleDto uapUpdateRoleDto =
                new com.iflytek.sec.uap.client.core.dto.role.UpdateRoleDto();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(updateRoleDto, uapUpdateRoleDto);

        return uapUpdateRoleDto;
    }

    /**
     * 将UAP客户端的UpdateRoleDto转换为core包下的UpdateRoleDto
     *
     * @param uapUpdateRoleDto UAP客户端的UpdateRoleDto
     * @return core包下的UpdateRoleDto
     */
    public UpdateRoleDto fromUapUpdateRoleDto(com.iflytek.sec.uap.client.core.dto.role.UpdateRoleDto uapUpdateRoleDto) {
        if (uapUpdateRoleDto == null) {
            return null;
        }

        UpdateRoleDto updateRoleDto = new UpdateRoleDto();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(uapUpdateRoleDto, updateRoleDto);

        return updateRoleDto;
    }
}
