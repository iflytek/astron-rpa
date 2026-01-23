package com.iflytek.rpa.base.controller;

import com.iflytek.rpa.base.service.ClientVersionUpdateService;
import java.net.URI;
import javax.annotation.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * 客户端版本更新控制器
 */
@RestController
@RequestMapping("/client-version-update")
public class ClientVersionUpdateController {

    @Resource
    private ClientVersionUpdateService clientVersionUpdateService;

    /**
     * 检查客户端版本是否需要更新
     *
     * @param version 当前版本号
     * @return 如果已是最新版本返回204，否则返回302重定向到最新版本下载URL
     */
    @GetMapping("/update-check/{os}/{arch}/{version}/latest.yml")
    public ResponseEntity<Void> updateCheck(
            @PathVariable("os") String os, @PathVariable("arch") String arch, @PathVariable("version") String version)
            throws Exception {
        String latestVersionUrl = clientVersionUpdateService.checkVersionSimple(os, arch, version);
        if (latestVersionUrl == null) {
            return ResponseEntity.ok().build();
        }
        HttpHeaders headers = new HttpHeaders();
        headers.setLocation(URI.create(latestVersionUrl));
        return ResponseEntity.status(HttpStatus.MOVED_PERMANENTLY)
                .headers(headers)
                .build();
    }
}
