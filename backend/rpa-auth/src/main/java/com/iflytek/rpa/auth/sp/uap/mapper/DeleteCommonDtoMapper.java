package com.iflytek.rpa.auth.sp.uap.mapper;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * DeleteCommonDto映射器
 * 用于将core包下的DeleteCommonDto转换为UAP客户端包下的DeleteCommonDto
 *
 * @author xqcao2
 */
@Component
public class DeleteCommonDtoMapper {

    /**
     * 将core包下的DeleteCommonDto转换为UAP客户端的DeleteCommonDto
     *
     * @param source core包下的DeleteCommonDto
     * @return UAP客户端的DeleteCommonDto
     */
    public com.iflytek.sec.uap.client.core.dto.DeleteCommonDto toUapDeleteCommonDto(
            com.iflytek.rpa.auth.core.entity.DeleteCommonDto source) {
        if (source == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.DeleteCommonDto target =
                new com.iflytek.sec.uap.client.core.dto.DeleteCommonDto();

        // 使用BeanUtils复制属性（字段完全一致）
        BeanUtils.copyProperties(source, target);

        return target;
    }

    /**
     * 将UAP客户端的DeleteCommonDto转换为核心实体DeleteCommonDto
     *
     * @param source UAP客户端的DeleteCommonDto
     * @return core包下的DeleteCommonDto
     */
    public com.iflytek.rpa.auth.core.entity.DeleteCommonDto toCoreDeleteCommonDto(
            com.iflytek.sec.uap.client.core.dto.DeleteCommonDto source) {
        if (source == null) {
            return null;
        }

        com.iflytek.rpa.auth.core.entity.DeleteCommonDto target =
                new com.iflytek.rpa.auth.core.entity.DeleteCommonDto();

        // 使用BeanUtils复制属性（字段完全一致）
        BeanUtils.copyProperties(source, target);

        return target;
    }

    /**
     * 批量将core包下的DeleteCommonDto列表转换为UAP客户端的DeleteCommonDto列表
     *
     * @param sourceList core包下的DeleteCommonDto列表
     * @return UAP客户端的DeleteCommonDto列表
     */
    public List<com.iflytek.sec.uap.client.core.dto.DeleteCommonDto> toUapDeleteCommonDtos(
            List<com.iflytek.rpa.auth.core.entity.DeleteCommonDto> sourceList) {
        if (sourceList == null || sourceList.isEmpty()) {
            return Collections.emptyList();
        }

        return sourceList.stream().map(this::toUapDeleteCommonDto).collect(Collectors.toList());
    }

    /**
     * 批量将UAP客户端的DeleteCommonDto列表转换为核心实体DeleteCommonDto列表
     *
     * @param sourceList UAP客户端的DeleteCommonDto列表
     * @return core包下的DeleteCommonDto列表
     */
    public List<com.iflytek.rpa.auth.core.entity.DeleteCommonDto> toCoreDeleteCommonDtos(
            List<com.iflytek.sec.uap.client.core.dto.DeleteCommonDto> sourceList) {
        if (sourceList == null || sourceList.isEmpty()) {
            return Collections.emptyList();
        }

        return sourceList.stream().map(this::toCoreDeleteCommonDto).collect(Collectors.toList());
    }
}
