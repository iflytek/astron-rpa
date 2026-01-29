package com.iflytek.rpa.auth.sp.uap.utils;

import java.nio.charset.StandardCharsets;
import java.security.*;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;
import javax.crypto.Cipher;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

/**
 * 授权解密工具类
 * 用于解密租户到期时间
 */
@Slf4j
@Component
public class EncryptUtils {

    /**
     * RSA加密算法
     */
    private static final String ALGORITHM = "RSA";

    /**
     * RSA公钥（Base64格式）
     * 用于解密供应商提供的授权信息
     * 此公钥对应的私钥由供应商持有，用于生成授权
     */
    private static final String PUBLIC_KEY_BASE64 =
            "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoZpsnI0MN53n0rcJNOcPdYOh6jDwcH2EmdfF07Js9Zt0S6ZoX2C5lXJcHg+MDjthVZRKPecMm2vEeBh/1ah/lA+CC/zNW3V0nz0vKuQzS5XXM2bMSYyHqU6UwqIXvQxhuSPrOOUuvE4KyPO/ZsZrU9tkaCdygfu20hOzEBKtrbRoEz8Bwhn2bCdBjG0SjFZyumNj7UQ9G+K69urY+lH4lLaY7nwDUboiDjKIbgGTpIYJGzeIsivtlMQVSIBvvSky8GVBDOxqtJ7Q4CH+lzICClyNK3QsOk2y214RCom5AM34iv6VvaWmAQc4Ciy+n4vMFjha9KWLjn582BjVLxm2qQIDAQAB";

    /**
     * RSA公钥对象
     */
    private static PublicKey publicKey;

    /**
     * 初始化RSA公钥
     * 从Base64编码的公钥字符串加载公钥对象
     */
    static {
        try {
            // 从Base64字符串加载公钥
            byte[] publicKeyBytes = Base64.getDecoder().decode(PUBLIC_KEY_BASE64);
            X509EncodedKeySpec keySpec = new X509EncodedKeySpec(publicKeyBytes);
            KeyFactory keyFactory = KeyFactory.getInstance(ALGORITHM);
            publicKey = keyFactory.generatePublic(keySpec);

            log.info("RSA公钥初始化成功");
        } catch (Exception e) {
            log.error("RSA公钥初始化失败", e);
            throw new RuntimeException("RSA公钥初始化失败", e);
        }
    }

    /**
     * 使用公钥解密授权信息
     * 注意：这里使用公钥解密，是因为供应商使用私钥加密
     * 这是RSA的一种特殊用法，用于验证授权信息的真实性
     *
     * @param encryptedText 加密后的Base64字符串（由供应商使用私钥加密）
     * @return 解密后的明文（到期时间，格式：yyyy-MM-dd）
     */
    public static String decrypt(String encryptedText) {
        if (encryptedText == null || encryptedText.isEmpty()) {
            throw new RuntimeException("授权信息解密失败：输入不能为空");
        }

        long startNanos = System.nanoTime();
        try {
            Cipher cipher = Cipher.getInstance(ALGORITHM);
            cipher.init(Cipher.DECRYPT_MODE, publicKey);

            // 分段解密（支持长文本）
            String[] encryptedBlocks = encryptedText.split("\\|");
            StringBuilder decryptedText = new StringBuilder();

            for (String encryptedBlock : encryptedBlocks) {
                byte[] encryptedBytes = Base64.getDecoder().decode(encryptedBlock);
                byte[] decryptedBytes = cipher.doFinal(encryptedBytes);
                decryptedText.append(new String(decryptedBytes, StandardCharsets.UTF_8));
            }

            return decryptedText.toString();
        } catch (Exception e) {
            log.error("授权信息解密失败，密文：{}", encryptedText, e);
            throw new RuntimeException("授权信息解密失败：" + e.getMessage(), e);
        } finally {
            long costMicros = (System.nanoTime() - startNanos) / 1_000;
            log.info("授权信息解密耗时 {} 微秒", costMicros);
        }
    }
}
