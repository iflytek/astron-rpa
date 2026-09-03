package com.iflytek.rpa.auth.utils;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.classic.spi.LoggingEvent;
import com.iflytek.rpa.auth.conf.SensitiveMessageConverter;
import com.iflytek.rpa.auth.conf.SensitiveThrowableConverter;
import org.junit.jupiter.api.Test;
import org.slf4j.LoggerFactory;

class SensitiveDataSanitizerTest {

    @Test
    void redactsStructuredCredentialsAndPreservesNonSensitiveFields() {
        String source = "{\"password\":\"secret password\",\"access_token\":\"token-123\","
                + "\"refresh_token\":[\"refresh-secret\"],\"status\":200}";

        String sanitized = SensitiveDataSanitizer.sanitize(source);

        assertFalse(sanitized.contains("secret password"));
        assertFalse(sanitized.contains("token-123"));
        assertFalse(sanitized.contains("refresh-secret"));
        assertTrue(sanitized.contains("\"password\":\"[REDACTED]\""));
        assertTrue(sanitized.contains("\"refresh_token\":[\"[REDACTED]\"]"));
        assertTrue(sanitized.contains("\"status\":200"));
    }

    @Test
    void redactsHeadersQueryCredentialsAndAuthenticationArtifacts() {
        String source = "Authorization: Bearer bearer-secret Cookie: SESSION=session-secret "
                + "uri=/mcp?key=query-secret 临时凭证：temp-secret 验证码：123456 "
                + "cacheKey: auth:temp_token:temporary-secret";

        String sanitized = SensitiveDataSanitizer.sanitize(source);

        assertFalse(sanitized.contains("bearer-secret"));
        assertFalse(sanitized.contains("session-secret"));
        assertFalse(sanitized.contains("query-secret"));
        assertFalse(sanitized.contains("temp-secret"));
        assertFalse(sanitized.contains("temporary-secret"));
        assertFalse(sanitized.contains("123456"));
    }

    @Test
    void masksPhoneNumbersAndDoesNotMutateUnrelatedText() {
        String source = "phone: 13800138000 keyword: 13900139000 密码：chinese-secret status=success";
        String sanitized = SensitiveDataSanitizer.sanitize(source);

        assertEquals(
                "phone: 138****8000 keyword: 139****9000 密码：[REDACTED] status=success",
                sanitized);
    }

    @Test
    void logbackConvertersRedactMessagesAndThrowableText() {
        Logger logger = (Logger) LoggerFactory.getLogger("sensitive-converter-test");
        ILoggingEvent event = new LoggingEvent(
                getClass().getName(),
                logger,
                Level.ERROR,
                "password=message-secret",
                new IllegalStateException("session_id=throwable-secret"),
                null);

        SensitiveMessageConverter messageConverter = new SensitiveMessageConverter();
        SensitiveThrowableConverter throwableConverter = new SensitiveThrowableConverter();
        messageConverter.start();
        throwableConverter.start();
        try {
            String sanitizedMessage = messageConverter.convert(event);
            String sanitizedThrowable = throwableConverter.convert(event);

            assertFalse(sanitizedMessage.contains("message-secret"));
            assertTrue(sanitizedMessage.contains("password=[REDACTED]"));
            assertFalse(sanitizedThrowable.contains("throwable-secret"));
            assertTrue(sanitizedThrowable.contains("session_id=[REDACTED]"));
        } finally {
            messageConverter.stop();
            throwableConverter.stop();
        }
    }
}
