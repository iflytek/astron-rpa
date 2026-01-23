package com.iflytek.rpa.base.annotation;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONException;
import java.lang.reflect.Method;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.UUID;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

/**
 * API日志切面
 * 提供全局的方法调用日志记录功能
 */
@Aspect
@Component
@Slf4j
public class ApiLogAspect {

    /**
     * 时间格式化器，用于统一日志时间格式
     */
    private static final DateTimeFormatter TIMESTAMP_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS");

    /**
     * 定义切点：拦截所有Controller层的方法
     */
    @Pointcut("execution(* com.iflytek.rpa..*.controller..*(..))")
    public void controllerPointcut() {}

    /**
     * 定义切点：拦截所有标注@RestController或@Controller的类中的方法
     */
    @Pointcut(
            "within(@org.springframework.web.bind.annotation.RestController *) || within(@org.springframework.stereotype.Controller *)")
    public void controllerClassPointcut() {}

    /**
     * 定义切点：拦截所有Service层的方法
     */
    @Pointcut("execution(* com.iflytek.rpa.*.service.*(..))")
    public void servicePointcut() {}

    /**
     * 定义切点：拦截标注了@ApiLog注解的方法
     */
    @Pointcut("@annotation(com.iflytek.rpa.base.annotation.ApiLog)")
    public void apiLogPointcut() {}

    /**
     * 定义切点：拦截类上标注了@ApiLog注解的所有方法
     */
    @Pointcut("@within(com.iflytek.rpa.base.annotation.ApiLog)")
    public void apiLogClassPointcut() {}

    /**
     * 环绕通知：记录方法执行的详细信息
     */
    @Around("controllerPointcut() || controllerClassPointcut() || apiLogPointcut() || apiLogClassPointcut()")
    public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
        // 检查是否被@NoApiLog注解排除
        if (shouldExcludeLogging(joinPoint)) {
            return joinPoint.proceed();
        }
        // 生成请求ID
        String requestId = UUID.randomUUID().toString().replace("-", "").substring(0, 8);

        // 获取方法信息
        MethodSignature methodSignature = (MethodSignature) joinPoint.getSignature();
        Method method = methodSignature.getMethod();
        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = method.getName();

        // 获取注解配置
        ApiLog apiLog = getApiLogAnnotation(method, joinPoint.getTarget().getClass());

        // 记录开始时间
        long startTime = System.currentTimeMillis();

        try {
            // 记录方法调用开始信息
            logMethodStart(requestId, className, methodName, joinPoint.getArgs(), apiLog);

            // 执行目标方法
            Object result = joinPoint.proceed();

            // 计算执行时间
            long endTime = System.currentTimeMillis();
            long executionTime = endTime - startTime;

            // 记录方法调用成功信息
            logMethodSuccess(requestId, className, methodName, result, executionTime, apiLog);

            return result;

        } catch (Throwable throwable) {
            // 计算执行时间
            long endTime = System.currentTimeMillis();
            long executionTime = endTime - startTime;

            // 记录方法调用异常信息
            logMethodException(requestId, className, methodName, throwable, executionTime, apiLog);

            // 重新抛出异常
            throw throwable;
        }
    }

    /**
     * 检查是否应该排除日志记录
     */
    private boolean shouldExcludeLogging(ProceedingJoinPoint joinPoint) {
        MethodSignature methodSignature = (MethodSignature) joinPoint.getSignature();
        Method method = methodSignature.getMethod();
        Class<?> targetClass = joinPoint.getTarget().getClass();

        // 检查方法上是否有@NoApiLog注解
        if (method.isAnnotationPresent(NoApiLog.class)) {
            return true;
        }

        // 检查类上是否有@NoApiLog注解
        if (targetClass.isAnnotationPresent(NoApiLog.class)) {
            return true;
        }

        return false;
    }

    /**
     * 获取ApiLog注解
     */
    private ApiLog getApiLogAnnotation(Method method, Class<?> targetClass) {
        // 优先获取方法上的注解
        ApiLog apiLog = method.getAnnotation(ApiLog.class);
        if (apiLog != null) {
            return apiLog;
        }

        // 获取类上的注解
        return targetClass.getAnnotation(ApiLog.class);
    }

    /**
     * 记录方法调用开始信息
     */
    private void logMethodStart(String requestId, String className, String methodName, Object[] args, ApiLog apiLog) {
        try {
            String timestamp = LocalDateTime.now().format(TIMESTAMP_FORMATTER);
            StringBuilder logMsg = new StringBuilder();

            // 标准化日志格式：[时间戳] [状态] 键值对格式
            logMsg.append("[").append(timestamp).append("] ");
            logMsg.append("[API开始] ");
            logMsg.append("requestId=").append(requestId);
            logMsg.append(" className=").append(className);
            logMsg.append(" methodName=").append(methodName);

            // 获取HTTP请求信息
            HttpServletRequest request = getHttpServletRequest();
            if (request != null) {
                logMsg.append(" httpMethod=").append(request.getMethod());
                logMsg.append(" requestUrl=").append(request.getRequestURL());
            }

            // 记录操作描述
            if (apiLog != null && !apiLog.value().isEmpty()) {
                logMsg.append(" operation=").append(apiLog.value().replaceAll("\\s+", "_"));
            }

            // 记录请求参数
            if (apiLog == null || apiLog.logParams()) {
                String params = formatParameters(args, apiLog);
                logMsg.append(" params=").append(params.replaceAll("\\s+", " "));
            }

            log.info(logMsg.toString());

        } catch (Exception e) {
            log.warn(
                    "[{}] [API日志异常] requestId={} message={}",
                    LocalDateTime.now().format(TIMESTAMP_FORMATTER),
                    requestId,
                    e.getMessage());
        }
    }

    /**
     * 记录方法调用成功信息
     */
    private void logMethodSuccess(
            String requestId, String className, String methodName, Object result, long executionTime, ApiLog apiLog) {
        try {
            String timestamp = LocalDateTime.now().format(TIMESTAMP_FORMATTER);
            StringBuilder logMsg = new StringBuilder();

            // 标准化日志格式
            logMsg.append("[").append(timestamp).append("] ");
            logMsg.append("[API成功] ");
            logMsg.append("requestId=").append(requestId);
            logMsg.append(" className=").append(className);
            logMsg.append(" methodName=").append(methodName);

            // 记录执行时间
            if (apiLog == null || apiLog.logTime()) {
                logMsg.append(" executionTime=").append(executionTime).append("ms");

                // 性能标识，便于grep过滤
                if (executionTime > 5000) {
                    logMsg.append(" performanceLevel=SLOW");
                } else if (executionTime > 1000) {
                    logMsg.append(" performanceLevel=ATTENTION");
                } else {
                    logMsg.append(" performanceLevel=NORMAL");
                }
            }

            // 记录返回结果大小
            String resultStr = formatResult(result, apiLog);
            logMsg.append(" resultSize=").append(resultStr.length()).append("bytes");

            // 记录返回结果
            if (apiLog == null || apiLog.logResult()) {
                logMsg.append(" result=").append(resultStr.replaceAll("\\s+", " "));
            }

            // 添加状态标识
            logMsg.append(" status=SUCCESS");

            log.info(logMsg.toString());

        } catch (Exception e) {
            log.warn(
                    "[{}] [API日志异常] requestId={} message={}",
                    LocalDateTime.now().format(TIMESTAMP_FORMATTER),
                    requestId,
                    e.getMessage());
        }
    }

    /**
     * 记录方法调用异常信息
     */
    private void logMethodException(
            String requestId,
            String className,
            String methodName,
            Throwable throwable,
            long executionTime,
            ApiLog apiLog) {
        try {
            String timestamp = LocalDateTime.now().format(TIMESTAMP_FORMATTER);
            StringBuilder logMsg = new StringBuilder();

            // 标准化日志格式
            logMsg.append("[").append(timestamp).append("] ");
            logMsg.append("[API异常] ");
            logMsg.append("requestId=").append(requestId);
            logMsg.append(" className=").append(className);
            logMsg.append(" methodName=").append(methodName);

            // 记录执行时间
            if (apiLog == null || apiLog.logTime()) {
                logMsg.append(" executionTime=").append(executionTime).append("ms");
            }

            // 记录异常信息
            if (apiLog == null || apiLog.logException()) {
                logMsg.append(" exceptionType=").append(throwable.getClass().getSimpleName());
                String exceptionMessage = throwable.getMessage();
                if (exceptionMessage != null) {
                    // 清理异常消息中的换行符和多余空格，便于grep
                    exceptionMessage = exceptionMessage.replaceAll("\\s+", " ").trim();
                    logMsg.append(" exceptionMessage=").append(exceptionMessage);
                }

                // 添加异常根因（如果是包装异常）
                Throwable rootCause = getRootCause(throwable);
                if (rootCause != throwable) {
                    logMsg.append(" rootCauseType=").append(rootCause.getClass().getSimpleName());
                }
            }

            // 添加状态标识
            logMsg.append(" status=ERROR");

            log.error(logMsg.toString(), throwable);

        } catch (Exception e) {
            log.warn(
                    "[{}] [API日志异常] requestId={} message={}",
                    LocalDateTime.now().format(TIMESTAMP_FORMATTER),
                    requestId,
                    e.getMessage());
        }
    }

    /**
     * 格式化请求参数
     */
    private String formatParameters(Object[] args, ApiLog apiLog) {
        if (args == null || args.length == 0) {
            return "无参数";
        }

        try {
            String jsonStr = JSON.toJSONString(args);

            // 限制长度
            int maxLength = apiLog != null ? apiLog.maxParamLength() : 2000;
            if (jsonStr.length() > maxLength) {
                jsonStr = jsonStr.substring(0, maxLength) + "...[已截取]";
            }

            return jsonStr;

        } catch (JSONException e) {
            return "参数序列化失败: " + e.getMessage();
        } catch (Exception e) {
            return "参数格式化异常: " + e.getMessage();
        }
    }

    /**
     * 格式化返回结果
     */
    private String formatResult(Object result, ApiLog apiLog) {
        if (result == null) {
            return "null";
        }

        try {
            String jsonStr = JSON.toJSONString(result);

            // 限制长度
            int maxLength = apiLog != null ? apiLog.maxResultLength() : 2000;
            if (jsonStr.length() > maxLength) {
                jsonStr = jsonStr.substring(0, maxLength) + "...[已截取]";
            }

            return jsonStr;

        } catch (JSONException e) {
            return "结果序列化失败: " + e.getMessage();
        } catch (Exception e) {
            return "结果格式化异常: " + e.getMessage();
        }
    }

    /**
     * 获取HTTP请求对象
     */
    private HttpServletRequest getHttpServletRequest() {
        try {
            ServletRequestAttributes attributes =
                    (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
            return attributes != null ? attributes.getRequest() : null;
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 获取客户端真实IP地址
     */
    private String getClientIpAddress(HttpServletRequest request) {
        String[] headers = {
            "X-Forwarded-For",
            "X-Real-IP",
            "Proxy-Client-IP",
            "WL-Proxy-Client-IP",
            "HTTP_CLIENT_IP",
            "HTTP_X_FORWARDED_FOR"
        };

        for (String header : headers) {
            String ip = request.getHeader(header);
            if (ip != null && ip.length() > 0 && !"unknown".equalsIgnoreCase(ip)) {
                // 多级代理的情况下，第一个IP为客户端真实IP
                if (ip.contains(",")) {
                    ip = ip.split(",")[0].trim();
                }
                return ip;
            }
        }

        return request.getRemoteAddr();
    }

    /**
     * 提取用户ID（从session、header或token中）
     */
    private String extractUserId(HttpServletRequest request) {
        try {
            // 1. 尝试从header中获取用户ID
            String userId = request.getHeader("X-User-Id");
            if (userId != null && !userId.isEmpty()) {
                return userId;
            }

            // 2. 尝试从session中获取用户ID
            if (request.getSession(false) != null) {
                Object sessionUserId = request.getSession(false).getAttribute("userId");
                if (sessionUserId != null) {
                    return sessionUserId.toString();
                }
            }

            // 3. 尝试从JWT token中解析用户ID（如果使用JWT）
            String authorization = request.getHeader("Authorization");
            if (authorization != null && authorization.startsWith("Bearer ")) {
                // 这里可以添加JWT解析逻辑
                // 为了简单起见，这里只是提取token的一部分作为标识
                String token = authorization.substring(7);
                if (token.length() > 10) {
                    return "token_" + token.substring(token.length() - 8);
                }
            }

            return null;
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 获取异常的根本原因
     */
    private Throwable getRootCause(Throwable throwable) {
        if (throwable == null) {
            return null;
        }

        Throwable rootCause = throwable;
        while (rootCause.getCause() != null && rootCause.getCause() != rootCause) {
            rootCause = rootCause.getCause();
        }

        return rootCause;
    }
}
