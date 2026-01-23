package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.UapExtendPropertyDto;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * UapExtendPropertyDto映射器
 * 用于将core包下的UapExtendPropertyDto和UAP客户端的UapExtendPropertyDto互相转换
 *
 * @author xqcao2
 */
@Component
public class UapExtendPropertyDtoMapper {

    /**
     * 将core包下的UapExtendPropertyDto转换为UAP客户端的UapExtendPropertyDto
     *
     * @param uapExtendPropertyDto core包下的UapExtendPropertyDto
     * @return UAP客户端的UapExtendPropertyDto
     */
    public com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto toUapExtendPropertyDto(
            UapExtendPropertyDto uapExtendPropertyDto) {
        if (uapExtendPropertyDto == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto uapExtendProperty =
                new com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(uapExtendPropertyDto, uapExtendProperty);
        return uapExtendProperty;
    }

    /**
     * 将UAP客户端的UapExtendPropertyDto转换为core包下的UapExtendPropertyDto
     *
     * @param uapExtendPropertyDto UAP客户端的UapExtendPropertyDto
     * @return core包下的UapExtendPropertyDto
     */
    public UapExtendPropertyDto fromUapExtendPropertyDto(
            com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto uapExtendPropertyDto) {
        if (uapExtendPropertyDto == null) {
            return null;
        }

        UapExtendPropertyDto uapExtendProperty = new UapExtendPropertyDto();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(uapExtendPropertyDto, uapExtendProperty);
        return uapExtendProperty;
    }

    /**
     * 批量将core包下的UapExtendPropertyDto列表转换为UAP客户端的UapExtendPropertyDto列表
     *
     * @param uapExtendPropertyDtoList core包下的UapExtendPropertyDto列表
     * @return UAP客户端的UapExtendPropertyDto列表
     */
    public List<com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto> toUapExtendPropertyDtoList(
            List<UapExtendPropertyDto> uapExtendPropertyDtoList) {
        if (uapExtendPropertyDtoList == null || uapExtendPropertyDtoList.isEmpty()) {
            return Collections.emptyList();
        }

        return uapExtendPropertyDtoList.stream()
                .map(this::toUapExtendPropertyDto)
                .filter(uapExtendProperty -> uapExtendProperty != null)
                .collect(Collectors.toList());
    }

    /**
     * 批量将UAP客户端的UapExtendPropertyDto列表转换为core包下的UapExtendPropertyDto列表
     *
     * @param uapExtendPropertyDtoList UAP客户端的UapExtendPropertyDto列表
     * @return core包下的UapExtendPropertyDto列表
     */
    public List<UapExtendPropertyDto> fromUapExtendPropertyDtoList(
            List<com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto> uapExtendPropertyDtoList) {
        if (uapExtendPropertyDtoList == null || uapExtendPropertyDtoList.isEmpty()) {
            return Collections.emptyList();
        }

        return uapExtendPropertyDtoList.stream()
                .map(this::fromUapExtendPropertyDto)
                .filter(uapExtendProperty -> uapExtendProperty != null)
                .collect(Collectors.toList());
    }
}
