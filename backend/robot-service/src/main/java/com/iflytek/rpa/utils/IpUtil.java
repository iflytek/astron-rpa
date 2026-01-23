package com.iflytek.rpa.utils;

import java.net.InetAddress;
import java.util.Objects;
import javax.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpHeaders;
import org.springframework.http.server.reactive.ServerHttpRequest;

/**
 * @ClassName IpUtil
 * @Author taozhang4
 * @Date 2019/9/17 10:02
 **/
public class IpUtil {
    public static final Logger LOGGER = LoggerFactory.getLogger(IpUtil.class);

    /**
     * 各种代理
     * <p>
     * X-Forwarded-For：Squid服务代理
     * Proxy-Client-IP：apache服务代理
     * WL-Proxy-Client-IP：weblogic服务代理
     * X-Real-IP：nginx服务代理
     * HTTP_CLIENT_IP：有些代理服务器
     */
    static final String[] PROXYS = {
        "X-Real-IP", "X-Forwarded-For", "Proxy-Client-IP", "WL-Proxy-Client-IP", "HTTP_CLIENT_IP"
    };

    static final String LOCALHOST_IP_V4 = "127.0.0.1";
    static final String LOCALHOST_IP_V6 = "0:0:0:0:0:0:0:1";

    /**
     * 获取客户端ip reactive
     */
    public static String getIpAddr(ServerHttpRequest request) {
        HttpHeaders headers = request.getHeaders();

        String ipAddress = null;
        for (String proxy : PROXYS) {
            ipAddress = headers.getFirst(proxy);
            if (!StringUtils.isEmpty(ipAddress) && !"unknown".equalsIgnoreCase(ipAddress)) {
                break;
            }
        }

        if (StringUtils.isEmpty(ipAddress) || "unknown".equalsIgnoreCase(ipAddress)) {
            ipAddress = Objects.requireNonNull(request.getRemoteAddress())
                    .getAddress()
                    .getHostAddress();
        }

        String ipSeparator = ",";
        if (!StringUtils.isEmpty(ipAddress) && ipAddress.indexOf(ipSeparator) > 0) {
            ipAddress = ipAddress.substring(0, ipAddress.indexOf(ipSeparator));
        }

        return ipAddress;
    }

    /**
     * 获取客户端ip servlet
     */
    public static String getIpAddr(HttpServletRequest request) {
        String ipAddress = null;

        for (String proxy : PROXYS) {
            ipAddress = request.getHeader(proxy);
            if (!StringUtils.isEmpty(ipAddress) && !"unknown".equalsIgnoreCase(ipAddress)) {
                break;
            }
        }

        if (StringUtils.isEmpty(ipAddress) || "unknown".equalsIgnoreCase(ipAddress)) {
            ipAddress = request.getRemoteAddr();
            // 根据网卡取本机配置的IP
            if (LOCALHOST_IP_V4.equals(ipAddress) || LOCALHOST_IP_V6.equals(ipAddress)) {
                InetAddress inet = null;
                try {
                    inet = InetAddress.getLocalHost();
                    ipAddress = inet.getHostAddress();
                } catch (Exception ignore) {
                }
            }
        }

        String ipSeparator = ",";
        if (!StringUtils.isEmpty(ipAddress) && ipAddress.indexOf(ipSeparator) > 0) {
            ipAddress = ipAddress.substring(0, ipAddress.indexOf(ipSeparator));
        }

        return ipAddress;
    }
}
