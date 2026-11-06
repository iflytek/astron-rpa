package com.iflytek.rpa.resource.file.controller;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.iflytek.rpa.resource.common.exp.ServiceException;
import com.iflytek.rpa.resource.common.response.AppResponse;
import com.iflytek.rpa.resource.file.service.FileService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.mockito.Mockito;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

class FileControllerTest {

    private FileController fileController;
    private FileService fileService;

    @BeforeEach
    void setUp() {
        fileController = new FileController();
        fileService = Mockito.mock(FileService.class);
        ReflectionTestUtils.setField(fileController, "fileService", fileService);
        ReflectionTestUtils.setField(fileController, "maxFileSize", 1024L);
        ReflectionTestUtils.setField(fileController, "maxShareSize", 2048L);
    }

    @Test
    void uploadFileUsesConfiguredMaxSizeInErrorMessage() {
        MockMultipartFile file = new MockMultipartFile("file", "large.txt", "text/plain", new byte[1025]);

        assertThatThrownBy(() -> fileController.uploadFile(file))
                .isInstanceOf(ServiceException.class)
                .hasMessage("文件大小不能超过1KB");
    }

    @Test
    void uploadVideoRejectsFilenameWithoutExtension() throws Exception {
        MockMultipartFile file = new MockMultipartFile("file", "video", "video/mp4", new byte[] {1});

        assertThatThrownBy(() -> fileController.uploadVideoFile(file))
                .isInstanceOf(ServiceException.class)
                .hasMessage("视频文件格式不支持，仅支持：mp4, webm, ogg, avi, mov, mpeg");
        verify(fileService, never()).uploadFile(file);
    }

    @Test
    void uploadVideoAcceptsCaseInsensitiveVideoExtension() throws Exception {
        MockMultipartFile file = new MockMultipartFile("file", "video.MP4", "video/mp4", new byte[] {1});
        when(fileService.uploadFile(file)).thenReturn(AppResponse.success("file-id"));

        AppResponse<String> response = fileController.uploadVideoFile(file);

        assertThat(response.getData()).isEqualTo("file-id");
        verify(fileService).uploadFile(file);
    }

    @ParameterizedTest
    @CsvSource({"owner, shared-image", "other-user, shared-image", "other-user, private-image"})
    void fileIdsCannotBeUsedToDeleteExistingObjects(String user, String fileId) throws Exception {
        MockMvcBuilders.standaloneSetup(fileController)
                .build()
                .perform(delete("/api/resource/file/delete")
                        .contextPath("/api/resource")
                        .principal(() -> user)
                        .param("fileId", fileId))
                .andExpect(status().isNotFound());

        verifyNoInteractions(fileService);
    }
}
