package com.iflytek.rpa.base.service.impl;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.base.dao.CAtomMetaNewDao;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.TenantExpirationDto;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.ArrayList;
import java.util.Collections;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

class CAtomMetaNewServiceImplTest {
    private final CAtomMetaNewServiceImpl service = new CAtomMetaNewServiceImpl();
    private final CAtomMetaNewDao dao = mock(CAtomMetaNewDao.class);
    private final RpaAuthFeign auth = mock(RpaAuthFeign.class);
    private final SemanticChoiceCapabilities capabilities = mock(SemanticChoiceCapabilities.class);
    private final ObjectMapper mapper = new ObjectMapper();

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(service, "cAtomMetaNewDao", dao);
        ReflectionTestUtils.setField(service, "semanticChoiceCapabilities", capabilities);
        ReflectionTestUtils.setField(service, "rpaAuthFeign", auth);
        TenantExpirationDto tenant = new TenantExpirationDto();
        tenant.setTenantType("enterprise");
        when(auth.getExpiration()).thenReturn(AppResponse.success(tenant));
    }

    @Test
    void hidesDisabledSemanticNodeAndEmptyCategoryWithoutChangingOtherMetadata() throws Exception {
        when(dao.getAtomContentByKey("atomCommon"))
                .thenReturn(
                        "{\"atomicTree\":[{\"key\":\"semantic-ai\",\"atomics\":[{\"key\":\"SemanticAI.choose\"}]},{\"key\":\"other\",\"custom\":42}],\"atomicTreeExtend\":[{\"key\":\"SemanticAI.choose\"}],\"customRoot\":true}");
        JsonNode result = mapper.readTree(service.getAtomTree().getData());
        assertEquals(1, result.path("atomicTree").size());
        assertEquals(42, result.path("atomicTree").get(0).path("custom").asInt());
        assertTrue(result.path("customRoot").asBoolean());
        assertEquals(0, result.path("atomicTreeExtend").size());
    }

    @Test
    void enabledReturnsOriginalTree() throws Exception {
        String tree = "{\"atomicTree\":[{\"key\":\"semantic-ai\",\"atomics\":[{\"key\":\"SemanticAI.choose\"}]}]}";
        when(dao.getAtomContentByKey("atomCommon")).thenReturn(tree);
        when(capabilities.isEnabled()).thenReturn(true);
        assertEquals(tree, service.getAtomTree().getData());
    }

    @Test
    void preservesOtherSemanticChildrenAndExistingTenantFilter() throws Exception {
        TenantExpirationDto tenant = new TenantExpirationDto();
        tenant.setTenantType("personal");
        when(auth.getExpiration()).thenReturn(AppResponse.success(tenant));
        when(dao.getAtomContentByKey("atomCommon"))
                .thenReturn(
                        "{\"atomicTree\":[{\"key\":\"enterprise\",\"atomics\":[]},{\"key\":\"semantic-ai\",\"atomics\":[{\"key\":\"SemanticAI.choose\"},{\"key\":\"Other.choose\"}]}]}");
        JsonNode result = mapper.readTree(service.getAtomTree().getData()).path("atomicTree");
        assertEquals(1, result.size());
        assertEquals(
                "Other.choose", result.get(0).path("atomics").get(0).path("key").asText());
        assertEquals(1, result.get(0).path("atomics").size());
    }

    @Test
    void rawMetadataRemainsAvailableForSavedFlows() {
        service.getListByKeys(new ArrayList<>(Collections.singletonList("SemanticAI.choose")));
        verify(dao).getListByKeys(Collections.singletonList("SemanticAI.choose"));
        service.getAll();
        verify(dao).getAll();
    }
}
