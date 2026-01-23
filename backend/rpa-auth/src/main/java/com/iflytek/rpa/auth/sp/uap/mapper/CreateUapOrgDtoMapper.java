package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.sec.uap.client.core.dto.org.CreateUapOrgDto;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.stereotype.Component;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/11/25 14:57
 */
@Component
public class CreateUapOrgDtoMapper {
    /**
     * 将客户端的CreateUapOrgDto转换为UAP客户端的CreateUapOrgDto
     */
    public CreateUapOrgDto toUapCreateUapOrgDto(com.iflytek.rpa.auth.core.entity.CreateUapOrgDto source) {
        if (source == null) {
            return null;
        }

        CreateUapOrgDto target = new CreateUapOrgDto();

        target.setUapOrg(toUapCreateOrgDto(source.getUapOrg()));
        target.setExtands(toUapExtendPropertyDtos(source.getExtands()));

        return target;
    }

    /**
     * 将客户端的CreateOrgDto转换为UAP客户端的CreateOrgDto
     */
    public com.iflytek.sec.uap.client.core.dto.org.CreateOrgDto toUapCreateOrgDto(
            com.iflytek.rpa.auth.core.entity.CreateOrgDto source) {
        if (source == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.org.CreateOrgDto target =
                new com.iflytek.sec.uap.client.core.dto.org.CreateOrgDto();

        target.setName(source.getName());
        target.setCode(source.getCode());
        target.setProvince(source.getProvince());
        target.setProvinceCode(source.getProvinceCode());
        target.setCity(source.getCity());
        target.setCityCode(source.getCityCode());
        target.setDistrict(source.getDistrict());
        target.setDistrictCode(source.getDistrictCode());
        target.setShortName(source.getShortName());
        target.setOrgType(source.getOrgType());
        target.setHigherOrg(source.getHigherOrg());
        target.setStatus(source.getStatus());
        target.setSort(source.getSort());
        target.setRemark(source.getRemark());

        return target;
    }

    /**
     * 将客户端的UapExtendPropertyDto列表转换为UAP客户端的UapExtendPropertyDto列表
     */
    public List<com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto> toUapExtendPropertyDtos(
            List<com.iflytek.rpa.auth.core.entity.UapExtendPropertyDto> sourceList) {
        if (sourceList == null) {
            return null;
        }

        return sourceList.stream().map(this::toUapExtendPropertyDto).collect(Collectors.toList());
    }

    /**
     * 将客户端的UapExtendPropertyDto转换为UAP客户端的UapExtendPropertyDto
     */
    public com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto toUapExtendPropertyDto(
            com.iflytek.rpa.auth.core.entity.UapExtendPropertyDto source) {
        if (source == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto target =
                new com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto();

        target.setId(source.getId());
        target.setValue(source.getValue());

        return target;
    }

    /**
     * 批量转换CreateUapOrgDto列表
     */
    public List<CreateUapOrgDto> toUapCreateOrgDtos(List<com.iflytek.rpa.auth.core.entity.CreateUapOrgDto> sourceList) {
        if (sourceList == null) {
            return null;
        }

        return sourceList.stream().map(this::toUapCreateUapOrgDto).collect(Collectors.toList());
    }
}
