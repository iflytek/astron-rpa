package com.iflytek.rpa.auth.idp.iflytekIdentity;

import com.iflytek.acount.sdk.CAccountClient;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * 专门负责创建 {@link CAccountClient}，方便在单元测试中进行替换或模拟。
 */
@Component
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "saas", matchIfMissing = true)
public class IflytekAccountClientFactory {

    public CAccountClient create(
            String kongUrl, int timeOut, String accessKeyId, String accessKeySecret, boolean useAesEncrypt) {
        return new CAccountClient.Builder()
                .setKongUrl(kongUrl)
                .setTimeOut(timeOut)
                .setAccessKeyId(accessKeyId)
                .setAccessKeySecret(accessKeySecret)
                .setUseAesEncrypt(useAesEncrypt)
                .build();
    }
}
