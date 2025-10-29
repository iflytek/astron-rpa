package com.iflytek.rpa.example.schedule;

import static com.iflytek.rpa.example.constants.ExampleConstants.EXAMPLE_USER_NAME;

import com.iflytek.rpa.example.service.SampleUsersService;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.utils.UserUtils;
import java.io.IOException;
import lombok.extern.slf4j.Slf4j;
import org.casbin.casdoor.entity.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

@Component
@Slf4j
public class SampleSchedule {

    @Autowired
    SampleUsersService sampleUsersService;

    /**
     * example user sample Inject
     * @throws IOException
     */
    @EventListener(ApplicationReadyEvent.class)
    public void exampleUserSampleInject() throws IOException {
        log.info("example user sample Inject start ......");
        User user = UserUtils.getUserByName(EXAMPLE_USER_NAME);
        String tenantId = user.owner;
        String userId = user.id;
        AppResponse<Boolean> response = sampleUsersService.insertUserSample(userId, tenantId);
        log.info("example user sample Inject result" + response.getMessage());
    }
}
