package com.iflytek.rpa.base.annotation;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.Signature;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class LoggingAspect {

    @Around("@annotation(logExecutionTime)")
    public Object logExecutionTime(ProceedingJoinPoint joinPoint, LogExecutionTime logExecutionTime) throws Throwable {

        // 切入点方法执行之前的处理
        long startTime = System.currentTimeMillis();
        System.out.println("### method started !!! ### ");

        // 继续执行被拦截的方法
        Object proceed = joinPoint.proceed();

        // 切入点方法执行之后的处理
        long endTime = System.currentTimeMillis();
        Signature signature = joinPoint.getSignature(); // 获取方法签名 ： 方法的全路径
        long executionTime = endTime - startTime;
        System.out.println("### method ended !!! ### ");
        System.out.println(signature + "executed in " + executionTime + "ms");
        return proceed;
    }
}
