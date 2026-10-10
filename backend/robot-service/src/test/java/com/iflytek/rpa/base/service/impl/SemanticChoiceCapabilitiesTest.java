package com.iflytek.rpa.base.service.impl;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.*;

import org.junit.jupiter.api.Test;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;

class SemanticChoiceCapabilitiesTest {
    private static final String URL = "http://ai-service:8010/v1/decision/capabilities";
    private final SemanticChoiceCapabilities capabilities =
            new SemanticChoiceCapabilities(new RestTemplateBuilder(), URL);
    private final RestTemplate rest =
            (RestTemplate) org.springframework.test.util.ReflectionTestUtils.getField(capabilities, "restTemplate");
    private final MockRestServiceServer server =
            MockRestServiceServer.bindTo(rest).build();

    @Test
    void acceptsOnlyExplicitBooleanEnabled() {
        for (String body :
                new String[] {"{\"enabled\":true}", "{\"enabled\":false}", "{}", "{\"enabled\":\"true\"}", "invalid"}) {
            server.reset();
            server.expect(requestTo(URL)).andRespond(withSuccess(body, MediaType.APPLICATION_JSON));
            assertEquals(body.equals("{\"enabled\":true}"), capabilities.isEnabled());
            server.verify();
        }
    }

    @Test
    void serviceFailureDisablesCapability() {
        server.expect(requestTo(URL)).andRespond(withServerError());
        assertFalse(capabilities.isEnabled());
    }

    @Test
    void timeoutDisablesCapability() {
        server.expect(requestTo(URL)).andRespond(request -> {
            throw new java.net.SocketTimeoutException("timeout");
        });
        assertFalse(capabilities.isEnabled());
    }
}
