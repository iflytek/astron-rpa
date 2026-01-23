package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.Resource;
import com.iflytek.sec.uap.client.core.dto.resource.UapResource;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * Resource映射器
 * 用于将UAP客户端的UapResource转换为core包下的Resource
 *
 * @author xqcao2
 */
@Component
public class ResourceMapper {

    /**
     * 将UAP客户端的UapResource转换为核心实体Resource
     *
     * @param uapResource UAP客户端的UapResource
     * @return core包下的Resource
     */
    public Resource fromUapResource(UapResource uapResource) {
        if (uapResource == null) {
            return null;
        }

        Resource resource = new Resource();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(uapResource, resource);

        return resource;
    }

    /**
     * 批量将UAP客户端的UapResource列表转换为核心实体Resource列表
     *
     * @param uapResources UAP客户端的UapResource列表
     * @return core包下的Resource列表
     */
    public List<Resource> fromUapResources(List<UapResource> uapResources) {
        if (uapResources == null || uapResources.isEmpty()) {
            return Collections.emptyList();
        }

        return uapResources.stream()
                .map(this::fromUapResource)
                .filter(resource -> resource != null)
                .collect(Collectors.toList());
    }

    /**
     * 将core包下的Resource转换为UAP客户端的UapResource
     *
     * @param resource core包下的Resource
     * @return UAP客户端的UapResource
     */
    public UapResource toUapResource(Resource resource) {
        if (resource == null) {
            return null;
        }

        UapResource uapResource = new UapResource();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(resource, uapResource);

        return uapResource;
    }

    /**
     * 批量将core包下的Resource列表转换为UAP客户端的UapResource列表
     *
     * @param resources core包下的Resource列表
     * @return UAP客户端的UapResource列表
     */
    public List<UapResource> toUapResources(List<Resource> resources) {
        if (resources == null || resources.isEmpty()) {
            return Collections.emptyList();
        }

        return resources.stream()
                .map(this::toUapResource)
                .filter(uapResource -> uapResource != null)
                .collect(Collectors.toList());
    }
}
