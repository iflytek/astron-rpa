package com.iflytek.rpa.utils;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.alibaba.fastjson.JSON;
import java.util.LinkedHashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

class SensitiveDataSanitizerTest {

    @Test
    void redactsTerminalPasswordWithoutChangingOtherFields() {
        String source = "[{\"account\":\"tester\",\"osPwd\":\"terminal-secret\",\"status\":\"free\"}]";

        String sanitized = SensitiveDataSanitizer.sanitize(source);

        assertFalse(sanitized.contains("terminal-secret"));
        assertTrue(sanitized.contains("\"osPwd\":\"[REDACTED]\""));
        assertTrue(sanitized.contains("\"account\":\"tester\""));
        assertTrue(sanitized.contains("\"status\":\"free\""));
    }

    @Test
    void redactsNestedCredentialsAndTransportSecrets() {
        String source = "{\"password\":\"login-secret\",\"nested\":{\"api_key\":\"key-secret\"},"
                + "\"url\":\"/mcp?key=query-secret\",\"authorization\":\"Bearer bearer-secret\"}";

        String sanitized = SensitiveDataSanitizer.sanitize(source);

        assertFalse(sanitized.contains("login-secret"));
        assertFalse(sanitized.contains("key-secret"));
        assertFalse(sanitized.contains("query-secret"));
        assertFalse(sanitized.contains("bearer-secret"));
    }

    @Test
    void masksPhoneNumbers() {
        String sanitized = SensitiveDataSanitizer.sanitize("phone=13800138000 status=ok");

        assertFalse(sanitized.contains("13800138000"));
        assertTrue(sanitized.contains("138****8000"));
        assertTrue(sanitized.contains("status=ok"));
    }

    @Test
    void redactsCompleteEscapedValuesAndCasdoorCredentials() {
        Map<String, Object> source = new LinkedHashMap<>();
        String secret = "prefix" + (char) 34 + "private-suffix";
        source.put("osPwd", secret);
        source.put("clientSecret", "client-secret");
        source.put("privateKey", "signing-secret");
        source.put("casdoor_session_id", "session-secret");
        source.put("status", "ok");

        String sanitized = SensitiveDataSanitizer.sanitize(JSON.toJSONString(source));

        assertFalse(sanitized.contains("prefix"));
        assertFalse(sanitized.contains("private-suffix"));
        assertFalse(sanitized.contains("client-secret"));
        assertFalse(sanitized.contains("signing-secret"));
        assertFalse(sanitized.contains("session-secret"));
        assertTrue(sanitized.contains("\"status\":\"ok\""));
        assertTrue(source.get("osPwd").equals(secret));
    }
}
