package com.iflytek.rpa.monitor.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.iflytek.rpa.monitor.entity.HisTerminal;
import java.util.List;

public interface HisTerminalService extends IService<HisTerminal> {
    void insertBatch(List<HisTerminal> hisRobotBatchData);
}
