package com.iflytek.rpa.notify.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.iflytek.rpa.notify.entity.NotifySend;
import com.iflytek.rpa.notify.entity.dto.CreateNotifyDto;
import com.iflytek.rpa.notify.entity.dto.NotifyListDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;

public interface NotifySendService extends IService<NotifySend> {
    AppResponse<?> createNotify(CreateNotifyDto createNotifyDto) throws NoLoginException;

    AppResponse<?> notifyList(NotifyListDto notifyListDto) throws NoLoginException;

    AppResponse<?> hasNotify() throws NoLoginException;

    AppResponse<?> setAllNotifyRead() throws NoLoginException;

    AppResponse<?> setSelectedNotifyRead(Long notifyId) throws NoLoginException;

    AppResponse<?> rejectJoinTeam(Long notifyId) throws NoLoginException;

    AppResponse<?> acceptJoinTeam(Long notifyId) throws NoLoginException;
}
