package com.iflytek.rpa.auth.sp.casdoor.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import java.io.PrintWriter;
import javax.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/11 10:28
 */
public class ResponseUtils {

    private static final Logger logger = LoggerFactory.getLogger(ResponseUtils.class);

    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static void success(HttpServletResponse response, Object data) {
        AppResponse<?> result = AppResponse.success(data);
        writeResultToResponse(response, result);
    }

    public static void fail(HttpServletResponse response, String message) {
        AppResponse<?> result = AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, message);
        writeResultToResponse(response, result);
    }

    private static void writeResultToResponse(HttpServletResponse response, AppResponse<?> result) {
        try {
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            response.setCharacterEncoding("UTF-8");
            PrintWriter writer = response.getWriter();
            String json = objectMapper.writeValueAsString(result);
            writer.write(json);
            writer.flush();
        } catch (Exception e) {
            logger.error("failed to write to the response stream", e);
        }
    }
}
