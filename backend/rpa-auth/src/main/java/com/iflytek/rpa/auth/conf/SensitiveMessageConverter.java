package com.iflytek.rpa.auth.conf;

import ch.qos.logback.classic.pattern.ClassicConverter;
import ch.qos.logback.classic.spi.ILoggingEvent;
import com.iflytek.rpa.auth.utils.SensitiveDataSanitizer;

/** Applies the central redaction policy to every formatted rpa-auth log message. */
public class SensitiveMessageConverter extends ClassicConverter {

    @Override
    public String convert(ILoggingEvent event) {
        return SensitiveDataSanitizer.sanitize(event.getFormattedMessage());
    }
}
