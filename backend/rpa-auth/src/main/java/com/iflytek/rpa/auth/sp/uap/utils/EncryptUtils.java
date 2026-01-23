package com.iflytek.rpa.auth.sp.uap.utils;

import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Base64;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * 加解密工具类
 * 用于加密和解密租户到期时间（非买断企业版使用）
 *
 * @author system
 */
@Slf4j
@Component
public class EncryptUtils {

    /**
     * 加密算法
     */
    private static final String ALGORITHM = "AES";

    /**
     * 加密模式
     */
    private static final String TRANSFORMATION = "AES/ECB/PKCS5Padding";

    /**
     * 默认密钥（16字节，128位）
     * 实际使用时建议从配置文件读取，并确保密钥安全
     */
    private static final String DEFAULT_KEY = "RpaAuth2024Key!";

    /**
     * 加密密钥（从配置文件读取，如果没有配置则使用默认密钥）
     */
    private static String encryptKey = DEFAULT_KEY;

    /**
     * 从配置文件读取的密钥
     */
    @Value("${tenant.expiration.encrypt.key:}")
    private String configKey;

    /**
     * Spring初始化后设置密钥
     */
    @javax.annotation.PostConstruct
    public void init() {
        if (configKey != null && !configKey.isEmpty() && configKey.length() == 16) {
            encryptKey = configKey;
            log.info("使用配置的租户到期时间加密密钥");
        } else {
            encryptKey = DEFAULT_KEY;
            log.warn("租户到期时间加密密钥未配置或长度不正确，使用默认密钥");
        }
    }

    /**
     * 获取加密密钥
     *
     * @return 加密密钥
     */
    private static String getKey() {
        return encryptKey != null ? encryptKey : DEFAULT_KEY;
    }

    /**
     * 加密字符串
     *
     * @param plainText 明文
     * @return 加密后的Base64字符串
     */
    public static String encrypt(String plainText) {
        if (plainText == null || plainText.isEmpty()) {
            return plainText;
        }

        try {
            SecretKeySpec secretKey = new SecretKeySpec(getKey().getBytes(StandardCharsets.UTF_8), ALGORITHM);
            Cipher cipher = Cipher.getInstance(TRANSFORMATION);
            cipher.init(Cipher.ENCRYPT_MODE, secretKey);
            byte[] encryptedBytes = cipher.doFinal(plainText.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(encryptedBytes);
        } catch (Exception e) {
            log.error("加密失败，明文：{}", plainText, e);
            throw new RuntimeException("加密失败：" + e.getMessage(), e);
        }
    }

    /**
     * 解密字符串
     * 如果输入字符串已经是日期格式（YYYY-MM-DD），则直接返回，不进行解密
     * 如果不是日期格式，则尝试解密
     *
     * @param encryptedText 加密后的Base64字符串或日期字符串
     * @return 解密后的明文或原始日期字符串
     */
    public static String decrypt(String encryptedText) {
        if (encryptedText == null || encryptedText.isEmpty()) {
            return encryptedText;
        }

        // 判断是否是日期格式（YYYY-MM-DD）
        if (isDateFormat(encryptedText)) {
            log.debug("输入字符串已是日期格式，无需解密：{}", encryptedText);
            return encryptedText;
        }

        // 不是日期格式，尝试解密
        try {
            SecretKeySpec secretKey = new SecretKeySpec(getKey().getBytes(StandardCharsets.UTF_8), ALGORITHM);
            Cipher cipher = Cipher.getInstance(TRANSFORMATION);
            cipher.init(Cipher.DECRYPT_MODE, secretKey);
            byte[] decryptedBytes = cipher.doFinal(Base64.getDecoder().decode(encryptedText));
            return new String(decryptedBytes, StandardCharsets.UTF_8);
        } catch (Exception e) {
            log.error("解密失败，密文：{}", encryptedText, e);
            throw new RuntimeException("解密失败：" + e.getMessage(), e);
        }
    }

    /**
     * 判断字符串是否是日期格式（YYYY-MM-DD）
     *
     * @param text 待判断的字符串
     * @return 如果是日期格式返回true，否则返回false
     */
    private static boolean isDateFormat(String text) {
        if (text == null || text.length() != 10) {
            return false;
        }

        // 使用正则表达式简单判断格式
        if (!text.matches("\\d{4}-\\d{2}-\\d{2}")) {
            return false;
        }

        // 尝试解析日期，验证是否为有效日期
        try {
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
            LocalDate.parse(text, formatter);
            return true;
        } catch (DateTimeParseException e) {
            return false;
        }
    }
}
