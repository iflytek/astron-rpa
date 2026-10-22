package com.iflytek.rpa.base.security;

import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.test.util.ReflectionTestUtils;

/**
 * 覆盖 issue #790：原子能力写接口的令牌校验。
 *
 * <p>限流依赖 Redis，这里把窗口配置关掉，只验证令牌一侧的行为。</p>
 */
class AtomAdminAccessGuardTest {

    private AtomAdminAccessGuard guard;

    @BeforeEach
    void setUp() {
        guard = new AtomAdminAccessGuard();
        ReflectionTestUtils.setField(guard, "maxRequests", 0);
        ReflectionTestUtils.setField(guard, "windowSeconds", 0L);
    }

    @Test
    void rejectsEveryWriteWhenNoTokenIsConfigured() {
        ReflectionTestUtils.setField(guard, "adminToken", "");

        assertThatThrownBy(() -> guard.checkWriteAccess(requestWithToken("anything")))
                .isInstanceOf(ServiceException.class)
                .hasFieldOrPropertyWithValue("code", ErrorCodeEnum.E_NO_POWER.getCode());
    }

    @Test
    void rejectsRequestWithoutTheHeader() {
        ReflectionTestUtils.setField(guard, "adminToken", "s3cret");

        assertThatThrownBy(() -> guard.checkWriteAccess(new MockHttpServletRequest()))
                .isInstanceOf(ServiceException.class);
    }

    @Test
    void rejectsWrongToken() {
        ReflectionTestUtils.setField(guard, "adminToken", "s3cret");

        assertThatThrownBy(() -> guard.checkWriteAccess(requestWithToken("wrong")))
                .isInstanceOf(ServiceException.class);
    }

    @Test
    void acceptsMatchingToken() {
        ReflectionTestUtils.setField(guard, "adminToken", "s3cret");

        assertThatCode(() -> guard.checkWriteAccess(requestWithToken("s3cret"))).doesNotThrowAnyException();
    }

    private MockHttpServletRequest requestWithToken(String token) {
        MockHttpServletRequest request = new MockHttpServletRequest();
        request.addHeader(AtomAdminAccessGuard.TOKEN_HEADER, token);
        return request;
    }
}
