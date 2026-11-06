package com.iflytek.rpa.robot.service.impl;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.robot.dao.SharedVarDao;
import com.iflytek.rpa.robot.dao.SharedVarKeyTenantDao;
import com.iflytek.rpa.robot.entity.SharedVarKeyTenant;
import com.iflytek.rpa.robot.entity.dto.SharedVarBatchDto;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.test.util.ReflectionTestUtils;

/**
 * Covers the tenant scoping that getBatchSharedVar's own DAO query must enforce.
 *
 * <p>getAvailableSharedVars (the /get-shared-var listing used by every other call site) filters
 * by tenant_id in its own SQL. getAvailableByIds (used only by /get-batch-shared-var) did not:
 * any authenticated caller could pass arbitrary shared_var IDs and receive another tenant's
 * usage_type='all' variables, including their sub-variable values, which the response then
 * re-encrypts with the CALLER'S OWN tenant key (obtainable from the caller's own
 * /shared-var-key), making that encryption step provide no protection against the caller who
 * already holds the key used.
 */
class SharedVarServiceImplTest {

    private static final String CALLER_TENANT_ID = "tenant-caller";

    @Mock
    private SharedVarDao sharedVarDao;

    @Mock
    private SharedVarKeyTenantDao sharedVarKeyTenantDao;

    @Mock
    private RpaAuthFeign rpaAuthFeign;

    private SharedVarServiceImpl service;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.initMocks(this);
        service = new SharedVarServiceImpl();
        ReflectionTestUtils.setField(service, "sharedVarDao", sharedVarDao);
        ReflectionTestUtils.setField(service, "sharedVarKeyTenantDao", sharedVarKeyTenantDao);
        ReflectionTestUtils.setField(service, "rpaAuthFeign", rpaAuthFeign);
        ReflectionTestUtils.setField(service, "baseMapper", sharedVarDao);
    }

    @Test
    void getBatchSharedVarScopesTheDaoLookupToTheCallersOwnTenant() throws Exception {
        when(rpaAuthFeign.getTenantId()).thenReturn(AppResponse.success(CALLER_TENANT_ID));
        SharedVarKeyTenant keyTenant = new SharedVarKeyTenant();
        keyTenant.setKey("caller-tenant-aes-key");
        when(sharedVarKeyTenantDao.selectByTenantId(CALLER_TENANT_ID)).thenReturn(keyTenant);
        when(sharedVarDao.getAvailableByIds(eq(CALLER_TENANT_ID), anyList())).thenReturn(new ArrayList<>());

        List<Long> ids = Arrays.asList(1L, 2L, 3L);
        SharedVarBatchDto dto = new SharedVarBatchDto();
        dto.setIds(ids);

        AppResponse<List<com.iflytek.rpa.robot.entity.vo.ClientSharedVarVo>> response =
                service.getBatchSharedVar(dto);

        assertTrue(response.ok());
        // The DAO call must be scoped to the caller's own tenant: a query that omits this
        // argument (the vulnerable one-argument getAvailableByIds(ids) signature) can no longer
        // compile against this call site, and this assertion fails loudly if a future change
        // ever stops passing it.
        verify(sharedVarDao).getAvailableByIds(eq(CALLER_TENANT_ID), eq(ids));
    }
}
