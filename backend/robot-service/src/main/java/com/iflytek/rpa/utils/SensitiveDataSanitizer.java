package com.iflytek.rpa.utils;

import java.util.regex.Pattern;

/** Creates sanitized copies of log text without changing application data. */
public final class SensitiveDataSanitizer {

    public static final String REDACTED = "[REDACTED]";

    private static final String SENSITIVE_KEY =
            "(?:api[ _-]?key|api[ _-]?secret|hashed[ _-]?key|password|passwd|pwd|os[ _-]?pwd|"
                    + "terminal[ _-]?pwd|confirm[ _-]?password|old[ _-]?password|new[ _-]?password|"
                    + "access[ _-]?token|refresh[ _-]?token|id[ _-]?token|temp[ _-]?token|token|"
                    + "authorization|cookie|cache[ _-]?key|session(?:[ _-]?id)?|jsessionid|"
                    + "casdoor[ _-]?session[ _-]?id|client[ _-]?secret|private[ _-]?key|"
                    + "verification[ _-]?code|verify[ _-]?code|"
                    + "sms[ _-]?code|captcha|credential|secret|"
                    + "param[ _-]?json)";

    private static final Pattern QUOTED_VALUE = Pattern.compile(
            "([\"']" + SENSITIVE_KEY + "[\"']\\s*[:=]\\s*)" + "(\"(?:\\\\.|[^\"\\\\])*\"|'(?:\\\\.|[^'\\\\])*')",
            Pattern.CASE_INSENSITIVE);
    private static final Pattern QUOTED_ARRAY_VALUE =
            Pattern.compile("([\"']" + SENSITIVE_KEY + "[\"']\\s*[:=]\\s*\\[)[^\\]]*(\\])", Pattern.CASE_INSENSITIVE);
    private static final Pattern LABEL_VALUE = Pattern.compile(
            "(\\b" + SENSITIVE_KEY + "\\b\\s*[:=]\\s*)(?!\\[REDACTED\\])([^\\s,;&}\\]]+)", Pattern.CASE_INSENSITIVE);
    private static final Pattern BEARER_VALUE = Pattern.compile("(\\bBearer\\s+)([^\\s,;]+)", Pattern.CASE_INSENSITIVE);
    private static final Pattern QUERY_API_KEY = Pattern.compile("([?&]key=)([^&\\s]+)", Pattern.CASE_INSENSITIVE);
    private static final Pattern PHONE_VALUE = Pattern.compile(
            "((?:phone|mobile)\\s*[\"']?\\s*[:=]\\s*[\"']?)(1\\d{2})\\d{4}(\\d{4})", Pattern.CASE_INSENSITIVE);
    private static final Pattern BARE_PHONE_VALUE = Pattern.compile("(?<!\\d)(1\\d{2})\\d{4}(\\d{4})(?!\\d)");

    private SensitiveDataSanitizer() {}

    public static String sanitize(Object source) {
        if (source == null) {
            return "";
        }

        String sanitized = source.toString();
        sanitized = replace(QUOTED_ARRAY_VALUE, sanitized, "$1\"" + REDACTED + "\"$2");
        sanitized = replace(QUOTED_VALUE, sanitized, "$1\"" + REDACTED + "\"");
        sanitized = replace(BEARER_VALUE, sanitized, "$1" + REDACTED);
        sanitized = replace(QUERY_API_KEY, sanitized, "$1" + REDACTED);
        sanitized = replace(LABEL_VALUE, sanitized, "$1" + REDACTED);
        sanitized = replace(PHONE_VALUE, sanitized, "$1$2****$3");
        return replace(BARE_PHONE_VALUE, sanitized, "$1****$2");
    }

    private static String replace(Pattern pattern, String source, String replacement) {
        return pattern.matcher(source).replaceAll(replacement);
    }
}
