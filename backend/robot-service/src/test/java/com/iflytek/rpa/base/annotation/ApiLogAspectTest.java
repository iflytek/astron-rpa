package com.iflytek.rpa.base.annotation;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.read.ListAppender;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.stream.Collectors;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.reflect.MethodSignature;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.LoggerFactory;

class ApiLogAspectTest {

    private final Logger logger = (Logger) LoggerFactory.getLogger(ApiLogAspect.class);
    private final ListAppender<ILoggingEvent> appender = new ListAppender<>();

    @BeforeEach
    void captureLogs() {
        appender.start();
        logger.addAppender(appender);
    }

    @AfterEach
    void releaseLogs() {
        logger.detachAppender(appender);
        appender.stop();
    }

    @Test
    void redactsParametersAndResultsWithoutChangingBusinessData() throws Throwable {
        Map<String, Object> input = new LinkedHashMap<>();
        input.put("osPwd", "desktop-secret");
        input.put("status", "free");
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("api_key", "result-secret");
        ProceedingJoinPoint call = invocation(input);
        when(call.proceed()).thenReturn(result);

        assertSame(result, new ApiLogAspect().around(call));
        assertTrue(input.get("osPwd").equals("desktop-secret"));
        assertTrue(result.get("api_key").equals("result-secret"));
        assertFalse(logs().contains("desktop-secret"));
        assertFalse(logs().contains("result-secret"));
        assertTrue(logs().contains("[REDACTED]"));
        assertTrue(logs().contains("free"));
    }

    @Test
    void propagatesOriginalFailureWithoutLoggingItsMessageOrTrace() throws Throwable {
        RuntimeException failure = new RuntimeException("unlabelled-private-value");
        ProceedingJoinPoint call = invocation("safe");
        when(call.proceed()).thenThrow(failure);

        assertSame(failure, assertThrows(RuntimeException.class, () -> new ApiLogAspect().around(call)));
        assertFalse(logs().contains("unlabelled-private-value"));
        assertTrue(logs().contains("RuntimeException"));
        for (ILoggingEvent event : appender.list) {
            assertNull(event.getThrowableProxy());
        }
    }

    @Test
    void serializationFailureDoesNotLeakOrChangeTheReturnValue() throws Throwable {
        BrokenValue value = new BrokenValue();
        ProceedingJoinPoint call = invocation(value);
        when(call.proceed()).thenReturn(value);

        assertSame(value, new ApiLogAspect().around(call));
        assertFalse(logs().contains("serialization-private-value"));
        assertTrue(logs().contains("IllegalStateException"));
    }

    private String logs() {
        return appender.list.stream().map(ILoggingEvent::getFormattedMessage).collect(Collectors.joining("\n"));
    }

    private ProceedingJoinPoint invocation(Object input) throws Exception {
        ProceedingJoinPoint call = mock(ProceedingJoinPoint.class);
        MethodSignature signature = mock(MethodSignature.class);
        when(signature.getMethod()).thenReturn(TestController.class.getMethod("handle", Object.class));
        when(call.getSignature()).thenReturn(signature);
        when(call.getTarget()).thenReturn(new TestController());
        when(call.getArgs()).thenReturn(new Object[] {input});
        return call;
    }

    public static class TestController {
        public Object handle(Object input) {
            return input;
        }
    }

    public static class BrokenValue {
        public String getValue() {
            throw new IllegalStateException("serialization-private-value");
        }
    }
}
