package com.iflytek.rpa.base.service.impl;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.iflytek.rpa.base.dao.CElementDao;
import com.iflytek.rpa.base.dao.CGroupDao;
import com.iflytek.rpa.base.entity.CElement;
import com.iflytek.rpa.base.entity.CGroup;
import com.iflytek.rpa.base.entity.dto.ServerBaseDto;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.RpaResourceFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.response.AppResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

/**
 * 覆盖 issue #793 的第一处孤儿场景：图片已上传、元素因重名未入库。
 */
class CElementServiceImplOrphanImageTest {

    private CElementServiceImpl service;
    private CElementDao cElementDao;
    private CGroupDao cGroupDao;
    private RpaAuthFeign rpaAuthFeign;
    private RpaResourceFeign rpaResourceFeign;

    @BeforeEach
    void setUp() {
        service = new CElementServiceImpl();
        cElementDao = mock(CElementDao.class);
        cGroupDao = mock(CGroupDao.class);
        rpaAuthFeign = mock(RpaAuthFeign.class);
        rpaResourceFeign = mock(RpaResourceFeign.class);

        ReflectionTestUtils.setField(service, "cElementDao", cElementDao);
        ReflectionTestUtils.setField(service, "cGroupDao", cGroupDao);
        ReflectionTestUtils.setField(service, "rpaAuthFeign", rpaAuthFeign);
        ReflectionTestUtils.setField(service, "rpaResourceFeign", rpaResourceFeign);
        ReflectionTestUtils.setField(service, "idWorker", new IdWorker());

        User user = new User();
        user.setId("user-1");
        when(rpaAuthFeign.getLoginUser()).thenReturn(AppResponse.success(user));

        CGroup existingGroup = new CGroup();
        existingGroup.setGroupId("group-1");
        when(cGroupDao.getGroupByGroupName(any(CGroup.class))).thenReturn(existingGroup);
    }

    @Test
    void duplicateNameDeletesTheImageThatWasJustUploaded() throws Exception {
        when(cElementDao.getElementSameName(anyString(), any(), anyString(), anyString(), anyString()))
                .thenReturn(new CElement());
        when(rpaResourceFeign.deleteFile(anyString())).thenReturn(AppResponse.success(true));

        AppResponse<?> response = service.createElementByType(dto("image-1"));

        assertThat(response.ok()).isFalse();
        assertThat(response.getMessage()).isEqualTo("名称重复，请重新命名");
        verify(rpaResourceFeign).deleteFile(eq("image-1"));
        verify(cElementDao, never()).insertElement(any(CElement.class));
    }

    @Test
    void duplicateNameStillReportsTheRealErrorWhenCleanupFails() throws Exception {
        when(cElementDao.getElementSameName(anyString(), any(), anyString(), anyString(), anyString()))
                .thenReturn(new CElement());
        when(rpaResourceFeign.deleteFile(anyString())).thenThrow(new RuntimeException("resource-service down"));

        AppResponse<?> response = service.createElementByType(dto("image-1"));

        assertThat(response.ok()).isFalse();
        assertThat(response.getMessage()).isEqualTo("名称重复，请重新命名");
    }

    @Test
    void successfulCreateDeletesNothing() throws Exception {
        when(cElementDao.getElementSameName(anyString(), any(), anyString(), anyString(), anyString()))
                .thenReturn(null);

        AppResponse<?> response = service.createElementByType(dto("image-1"));

        assertThat(response.ok()).isTrue();
        verify(rpaResourceFeign, never()).deleteFile(anyString());
        verify(cElementDao).insertElement(any(CElement.class));
    }

    @Test
    void duplicateNameWithoutAnImageCallsNoDelete() throws Exception {
        when(cElementDao.getElementSameName(anyString(), any(), anyString(), anyString(), anyString()))
                .thenReturn(new CElement());

        AppResponse<?> response = service.createElementByType(dto(null));

        assertThat(response.ok()).isFalse();
        verify(rpaResourceFeign, never()).deleteFile(anyString());
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
