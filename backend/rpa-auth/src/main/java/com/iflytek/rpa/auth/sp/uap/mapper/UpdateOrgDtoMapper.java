package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.UpdateOrgDto;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * UpdateOrgDto映射器
 * 用于将core包下的UpdateOrgDto和UAP客户端的UpdateOrgDto互相转换
 *
 * @author xqcao2
 */
@Component
public class UpdateOrgDtoMapper {

    /**
     * 将core包下的UpdateOrgDto转换为UAP客户端的UpdateOrgDto
     *
     * @param updateOrgDto core包下的UpdateOrgDto
     * @return UAP客户端的UpdateOrgDto
     */
    public com.iflytek.sec.uap.client.core.dto.org.UpdateOrgDto toUapUpdateOrgDto(UpdateOrgDto updateOrgDto) {
        if (updateOrgDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.org.UpdateOrgDto uapUpdateOrgDto =
                new com.iflytek.sec.uap.client.core.dto.org.UpdateOrgDto();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(updateOrgDto, uapUpdateOrgDto);

        return uapUpdateOrgDto;
    }

    /**
     * 将UAP客户端的UpdateOrgDto转换为core包下的UpdateOrgDto
     *
     * @param uapUpdateOrgDto UAP客户端的UpdateOrgDto
     * @return core包下的UpdateOrgDto
     */
    public UpdateOrgDto fromUapUpdateOrgDto(com.iflytek.sec.uap.client.core.dto.org.UpdateOrgDto uapUpdateOrgDto) {
        if (uapUpdateOrgDto == null) {
            return null;
        }

        UpdateOrgDto updateOrgDto = new UpdateOrgDto();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(uapUpdateOrgDto, updateOrgDto);

        return updateOrgDto;
    }
}
