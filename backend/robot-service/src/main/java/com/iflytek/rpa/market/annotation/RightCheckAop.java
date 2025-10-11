package com.iflytek.rpa.market.annotation;

import com.iflytek.rpa.market.dao.AppMarketDictDao;
import com.iflytek.rpa.market.dao.AppMarketUserDao;
import com.iflytek.rpa.market.entity.AppMarketDict;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.UserUtils;
import java.lang.reflect.Method;
import java.lang.reflect.Parameter;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class RightCheckAop {
    private static final Logger log = LoggerFactory.getLogger(RightCheckAop.class);

    @Autowired
    private AppMarketUserDao appMarketUserDao;

    @Autowired
    private AppMarketDictDao appMarketDictDao;

    @Around("@annotation(rightCheck)")
    public Object process(ProceedingJoinPoint joinPoint, RightCheck rightCheck) throws Throwable {
        // 如果功能编码在DB中不存在，说明编码不对
        String dictCode = appMarketDictDao.getCodeInfo(rightCheck.dictCode());
        if (null == dictCode) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "功能编码未注册");
        }
        Method method = ((MethodSignature) joinPoint.getSignature()).getMethod();
        Object[] args = joinPoint.getArgs();
        Parameter[] parameters = method.getParameters();
        String marketId = null;
        // 获取marketId
        for (int i = 0; i < parameters.length; i++) {
            Parameter parameter = parameters[i];
            Object argValue = args[i];
            if (argValue instanceof String && "marketId".equals(parameter.getName())) {
                marketId = argValue.toString();
            } else if (argValue.getClass().equals(rightCheck.clazz())) {
                try {
                    marketId = argValue.getClass()
                            .getMethod("getMarketId")
                            .invoke(argValue)
                            .toString();
                } catch (Exception e) {
                    log.error("获取marketId失败,message:{}", e.getMessage());
                    return AppResponse.error(ErrorCodeEnum.E_PARAM);
                }
            }
        }

        if (null == marketId) {
            log.info("获取marketId失败");
            return AppResponse.error(ErrorCodeEnum.E_PARAM);
        }
        String userId = UserUtils.nowUserId();
        // 查询角色
        String userType = appMarketUserDao.getUserTypeForCheck(userId, marketId);
        if (null == userType) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "市场中不存在该人员");
        }
        // 查询权限
        AppMarketDict appMarketDict = appMarketDictDao.getDictValueByCodeAndType(rightCheck.dictCode(), userType);
        if (null != appMarketDict && "F".equals(appMarketDict.getDictValue())) {
            log.warn(
                    "用户无权限,userId:{},marketId:{},dictCode:{},dictValue:{}",
                    userId,
                    marketId,
                    rightCheck.dictCode(),
                    appMarketDict.getDictValue());
            return AppResponse.error(ErrorCodeEnum.E_SERVICE_POWER_LIMIT, "当前角色无 " + appMarketDict.getName() + " 操作权限");
        }
        // 有权限，继续
        return joinPoint.proceed();
    }
}
