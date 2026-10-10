package com.iflytek.rpa.base.service.impl;

import com.fasterxml.jackson.databind.JsonNode;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

/** Reads deployment capability from the AI service without calling a model. */
@Component
public class SemanticChoiceCapabilities {
    private static final Logger log = LoggerFactory.getLogger(SemanticChoiceCapabilities.class);
    private final RestTemplate restTemplate;
    private final String capabilitiesUrl;

    public SemanticChoiceCapabilities(
            RestTemplateBuilder builder,
            @Value("${ai-service.decision-capabilities-url:http://ai-service:8010/v1/decision/capabilities}")
                    String capabilitiesUrl) {
        this.restTemplate = builder.setConnectTimeout(Duration.ofSeconds(1))
                .setReadTimeout(Duration.ofSeconds(1))
                .build();
        this.capabilitiesUrl = capabilitiesUrl;
    }

    public boolean isEnabled() {
        try {
            JsonNode response = restTemplate.getForObject(capabilitiesUrl, JsonNode.class);
            if (response == null || !response.path("enabled").isBoolean()) {
                log.warn("Semantic choice capability response is invalid; hiding component");
                return false;
            }
            return response.path("enabled").booleanValue();
        } catch (RestClientException exception) {
            // Do not log response bodies or URLs, which may contain deployment secrets.
            log.warn(
                    "Semantic choice capability lookup failed ({}); hiding component",
                    exception.getClass().getSimpleName());
            return false;
        }
    }
}
