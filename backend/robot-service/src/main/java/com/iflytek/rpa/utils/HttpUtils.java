package com.iflytek.rpa.utils;

import com.iflytek.rpa.task.entity.enums.SourceTypeEnum;
import java.io.PrintWriter;
import java.util.Objects;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

/**
 * @author keler
 */
public class HttpUtils {
    private static final Logger LOGGER = LoggerFactory.getLogger(HttpUtils.class);

    /**
     * 获取请求信息
     * @return HttpServletRequest
     */
    public static String getHeader(String key) {
        return getRequest().getHeader(key);
    }

    /**
     * 获取请求信息
     * @return HttpServletRequest
     */
    public static HttpServletRequest getRequest() {
        return ((ServletRequestAttributes) Objects.requireNonNull(RequestContextHolder.getRequestAttributes()))
                .getRequest();
    }

    /**
     * 获取请求信息
     * @return HttpSession
     */
    public static HttpSession getSession() {
        return getRequest().getSession();
    }

    public static String getSourceType() {
        String userAgent = HttpUtils.getHeader("user-agent");
        if (!StringUtils.isEmpty(userAgent) && userAgent.contains("iFlyRPAStudio")) {
            return SourceTypeEnum.CLIENT.getCode();
        }
        return SourceTypeEnum.WEB.getCode();
    }

    /**
     * 页面打印 AppResponse
     * @param response 错误信息
     * @param servletResponse servlet
     */
    public static void print(String response, ServletResponse servletResponse) {
        PrintWriter out = null;
        try {
            servletResponse.setCharacterEncoding("UTF-8");
            servletResponse.setContentType("application/json");
            out = servletResponse.getWriter();
            out.println(response);
        } catch (Exception e) {
            LOGGER.error("输出JSON报错", e);
        } finally {
            if (null != out) {
                out.flush();
                out.close();
            }
        }
    }
}
