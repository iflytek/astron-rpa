package com.iflytek.rpa.auth.conf;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpHeaders;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.session.web.http.CookieSerializer;

class SessionConfigTest {

    @Test
    void shouldMarkSessionCookieSecureForHttpsDeployment() {
        String setCookie = writeSessionCookie(true);

        assertThat(setCookie).contains("Secure").contains("HttpOnly").contains("SameSite=Lax");
    }

    @Test
    void shouldAllowExplicitLegacyHttpCookieMode() {
        String setCookie = writeSessionCookie(false);

        assertThat(setCookie).doesNotContain("Secure").contains("HttpOnly").contains("SameSite=Lax");
    }

    private String writeSessionCookie(boolean secure) {
        CookieSerializer serializer = new SessionConfig(secure).cookieSerializer();
        MockHttpServletRequest request = new MockHttpServletRequest();
        MockHttpServletResponse response = new MockHttpServletResponse();
        CookieSerializer.CookieValue cookieValue = new CookieSerializer.CookieValue(request, response, "session-id");

        serializer.writeCookieValue(cookieValue);

        return response.getHeader(HttpHeaders.SET_COOKIE);
    }
}
