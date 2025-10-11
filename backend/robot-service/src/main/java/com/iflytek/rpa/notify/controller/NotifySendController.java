package com.iflytek.rpa.notify.controller;

import com.iflytek.rpa.notify.entity.dto.CreateNotifyDto;
import com.iflytek.rpa.notify.entity.dto.NotifyListDto;
import com.iflytek.rpa.notify.service.NotifySendService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import javax.annotation.Resource;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/notify")
public class NotifySendController {
    @Resource
    private NotifySendService notifySendService;

    /**
     * 产生消息
     *
     * @param createNotifyDto
     * @return 产生消息是否成功
     */
    @PostMapping("/create-notify")
    public AppResponse<?> createNotify(@RequestBody CreateNotifyDto createNotifyDto) throws NoLoginException {
        return notifySendService.createNotify(createNotifyDto);
    }

    /**
     * 消息列表
     *
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/notify-List")
    public AppResponse<?> notifyList(@RequestBody NotifyListDto notifyListDto) throws NoLoginException {
        return notifySendService.notifyList(notifyListDto);
    }

    @GetMapping("/hasNotify")
    public AppResponse<?> hasNotify() throws NoLoginException {
        return notifySendService.hasNotify();
    }

    /**
     * 一键已读
     *
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/set-all-notify-read")
    public AppResponse<?> setAllNotifyRead() throws NoLoginException {
        return notifySendService.setAllNotifyRead();
    }

    /**
     * 已读指定消息
     *
     * @param notifyId
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/set-selected-notify-read")
    public AppResponse<?> setSelectedNotifyRead(@RequestParam("notifyId") Long notifyId) throws NoLoginException {
        return notifySendService.setSelectedNotifyRead(notifyId);
    }

    @GetMapping("/reject-join-team")
    public AppResponse<?> rejectJoinTeam(@RequestParam("notifyId") Long notifyId) throws NoLoginException {
        return notifySendService.rejectJoinTeam(notifyId);
    }

    @GetMapping("/accept-join-team")
    public AppResponse<?> acceptJoinTeam(@RequestParam("notifyId") Long notifyId) throws NoLoginException {
        return notifySendService.acceptJoinTeam(notifyId);
    }
}
