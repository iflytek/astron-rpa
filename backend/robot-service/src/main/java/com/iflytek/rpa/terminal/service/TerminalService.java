package com.iflytek.rpa.terminal.service;

import com.iflytek.rpa.terminal.entity.dto.BeatDto;
import com.iflytek.rpa.terminal.entity.dto.RegistryDto;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.List;

public interface TerminalService {
    AppResponse<String> registry(RegistryDto terminal) throws NoLoginException;

    AppResponse<String> processBeat(BeatDto beatDto);

    void updateStatusByTerminalIdList(List<String> terminalIdList, String status);
}
