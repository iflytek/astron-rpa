package com.iflytek.rpa.auth.conf;

import ch.qos.logback.classic.pattern.ThrowableProxyConverter;
import ch.qos.logback.classic.spi.ILoggingEvent;
import com.iflytek.rpa.auth.utils.SensitiveDataSanitizer;

/** Preserves stack traces while redacting credentials from exception text. */
public class SensitiveThrowableConverter extends ThrowableProxyConverter {

    @Override
    public String convert(ILoggingEvent event) {
        return SensitiveDataSanitizer.sanitize(super.convert(event));
    }
}
