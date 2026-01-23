package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.CreateRoleDto;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * CreateRoleDto映射器
 * 用于将core包下的CreateRoleDto转换为UAP客户端的CreateRoleDto
 *
 * @author xqcao2
 */
@Component
public class CreateRoleDtoMapper {

    /**
     * 将core包下的CreateRoleDto转换为UAP客户端的CreateRoleDto
     *
     * @param createRoleDto core包下的CreateRoleDto
     * @return UAP客户端的CreateRoleDto
     */
    public com.iflytek.sec.uap.client.core.dto.role.CreateRoleDto toUapCreateRoleDto(CreateRoleDto createRoleDto) {
        if (createRoleDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.role.CreateRoleDto uapCreateRoleDto =
                new com.iflytek.sec.uap.client.core.dto.role.CreateRoleDto();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(createRoleDto, uapCreateRoleDto);

        return uapCreateRoleDto;
    }

    /**
     * 将UAP客户端的CreateRoleDto转换为core包下的CreateRoleDto
     *
     * @param uapCreateRoleDto UAP客户端的CreateRoleDto
     * @return core包下的CreateRoleDto
     */
    public CreateRoleDto fromUapCreateRoleDto(com.iflytek.sec.uap.client.core.dto.role.CreateRoleDto uapCreateRoleDto) {
        if (uapCreateRoleDto == null) {
            return null;
        }

        CreateRoleDto createRoleDto = new CreateRoleDto();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(uapCreateRoleDto, createRoleDto);

        return createRoleDto;
    }
}
