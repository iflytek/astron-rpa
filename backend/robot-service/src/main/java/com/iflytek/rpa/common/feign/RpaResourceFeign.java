package com.iflytek.rpa.common.feign;

import com.iflytek.rpa.utils.response.AppResponse;
import org.springframework.cloud.openfeign.FeignAutoConfiguration;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * resource-service 文件接口
 *
 * <p>robot-service 只保存文件ID，S3 对象的生命周期由 resource-service 管理，
 * 因此清理孤儿文件需要经由该服务。</p>
 */
@FeignClient(
        name = "rpa-resource",
        url = "${resource.base-url:http://rpa-opensource-resource-service:8030}",
        configuration = FeignAutoConfiguration.class)
public interface RpaResourceFeign {

    /**
     * 根据文件ID删除文件（幂等）
     *
     * @param fileId 文件ID
     * @return 删除结果
     */
    @DeleteMapping("/api/resource/file/delete")
    AppResponse<Boolean> deleteFile(@RequestParam("fileId") String fileId);
}
