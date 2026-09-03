package com.iflytek.rpa.auth.conf;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.read.ListAppender;
import java.nio.charset.StandardCharsets;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;
import org.slf4j.LoggerFactory;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.util.StreamUtils;

class RequestLoggingFilterTest {

    @Test
    void logsSanitizedCopiesWithoutChangingRequestOrResponse() throws Exception {
        String requestBody = "{\"password\":\"request-secret\",\"phone\":\"13800138000\"}";
        String responseBody = "{\"access_token\":\"response-secret\",\"status\":\"ok\"}";
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/login");
        request.setQueryString("tempToken=query-secret&mode=login");
        request.addParameter("password", "parameter-secret");
        request.setContentType("application/json");
        request.setContent(requestBody.getBytes(StandardCharsets.UTF_8));
        MockHttpServletResponse response = new MockHttpServletResponse();

        Logger logger = (Logger) LoggerFactory.getLogger(RequestLoggingFilter.class);
        ListAppender<ILoggingEvent> appender = new ListAppender<>();
        appender.start();
        logger.addAppender(appender);

        try {
            new RequestLoggingFilter().doFilter(request, response, (servletRequest, servletResponse) -> {
                StreamUtils.copyToString(servletRequest.getInputStream(), StandardCharsets.UTF_8);
                servletResponse.setContentType("application/json");
                servletResponse.getWriter().write(responseBody);
            });
        } finally {
            logger.detachAppender(appender);
            appender.stop();
        }

        String logs = appender.list.stream()
                .map(ILoggingEvent::getFormattedMessage)
                .collect(Collectors.joining("\n"));

        assertFalse(logs.contains("request-secret"));
        assertFalse(logs.contains("response-secret"));
        assertFalse(logs.contains("query-secret"));
        assertFalse(logs.contains("parameter-secret"));
        assertFalse(logs.contains("13800138000"));
        assertTrue(logs.contains("138****8000"));
        assertEquals(responseBody, response.getContentAsString());
        assertEquals("parameter-secret", request.getParameter("password"));
    }
}
