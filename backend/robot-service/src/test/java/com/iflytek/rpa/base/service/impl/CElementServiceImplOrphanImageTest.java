package com.iflytek.rpa.base.service.impl;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import com.iflytek.rpa.base.dao.CElementDao;
import com.iflytek.rpa.base.dao.CGroupDao;
import com.iflytek.rpa.base.entity.CElement;
import com.iflytek.rpa.base.entity.CGroup;
import com.iflytek.rpa.base.entity.dto.ServerBaseDto;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.response.AppResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.test.util.ReflectionTestUtils;

/**
 * 重名失败不能修改已有元素或客户端提供的图片引用。
 */
class CElementServiceImplOrphanImageTest {

    private CElementServiceImpl service;
    private CElementDao cElementDao;
    private CGroupDao cGroupDao;
    private RpaAuthFeign rpaAuthFeign;

    @BeforeEach
    void setUp() {
        service = new CElementServiceImpl();
        cElementDao = mock(CElementDao.class);
        cGroupDao = mock(CGroupDao.class);
        rpaAuthFeign = mock(RpaAuthFeign.class);

        ReflectionTestUtils.setField(service, "cElementDao", cElementDao);
        ReflectionTestUtils.setField(service, "cGroupDao", cGroupDao);
        ReflectionTestUtils.setField(service, "rpaAuthFeign", rpaAuthFeign);
        ReflectionTestUtils.setField(service, "idWorker", new IdWorker(0, 0));

        User user = new User();
        user.setId("user-1");
        when(rpaAuthFeign.getLoginUser()).thenReturn(AppResponse.success(user));

        CGroup existingGroup = new CGroup();
        existingGroup.setGroupId("group-1");
        when(cGroupDao.getGroupByGroupName(any(CGroup.class))).thenReturn(existingGroup);
    }

    @ParameterizedTest
    @NullSource
    @ValueSource(strings = {"other-users-image", "shared-image"})
    void duplicateNameRetriesPreserveExistingImageReferences(String imageId) throws Exception {
        CElement existingElement = new CElement();
        existingElement.setImageId("shared-image");
        existingElement.setParentImageId("shared-parent");
        when(cElementDao.getElementSameName(anyString(), any(), anyString(), anyString(), anyString()))
                .thenReturn(existingElement);

        for (int attempt = 0; attempt < 2; attempt++) {
            ServerBaseDto request = dto(imageId);
            AppResponse<?> response = service.createElementByType(request);

            assertThat(response.ok()).isFalse();
            assertThat(response.getMessage()).isEqualTo("名称重复，请重新命名");
            assertThat(request.getElement().getImageId()).isEqualTo(imageId);
        }
        assertThat(existingElement.getImageId()).isEqualTo("shared-image");
        assertThat(existingElement.getParentImageId()).isEqualTo("shared-parent");
        verify(cElementDao, times(2)).getElementSameName(anyString(), any(), anyString(), anyString(), anyString());
        verifyNoMoreInteractions(cElementDao);
    }

    @Test
    void successfulCreateDeletesNothing() throws Exception {
        when(cElementDao.getElementSameName(anyString(), any(), anyString(), anyString(), anyString()))
                .thenReturn(null);

        AppResponse<?> response = service.createElementByType(dto("image-1"));

        assertThat(response.ok()).isTrue();
        verify(cElementDao).insertElement(any(CElement.class));
    }

    private ServerBaseDto dto(String imageId) {
        CElement element = new CElement();
        element.setElementName("元素A");
        element.setRobotId("robot-1");
        element.setRobotVersion(1);
        element.setImageId(imageId);

        ServerBaseDto serverBaseDto = new ServerBaseDto();
        serverBaseDto.setGroupName("默认分组");
        serverBaseDto.setRobotId("robot-1");
        serverBaseDto.setRobotVersion(1);
        serverBaseDto.setElementType("cv");
        serverBaseDto.setElement(element);
        return serverBaseDto;
    }
}
