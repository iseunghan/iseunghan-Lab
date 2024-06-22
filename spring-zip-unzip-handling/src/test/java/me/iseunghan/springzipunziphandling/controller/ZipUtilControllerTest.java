package me.iseunghan.springzipunziphandling.controller;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.http.MediaType.MULTIPART_FORM_DATA_VALUE;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = ZipUtilController.class)
class ZipUtilControllerTest {
    @Autowired private MockMvc mockMvc;

    @DisplayName("Zip Upload Test")
    @Test
    void uploadZipFileTest() throws Exception {
        // given
        MockMultipartFile file = new MockMultipartFile("file", "test.zip", MULTIPART_FORM_DATA_VALUE, (byte[]) null);

        // when & then
        mockMvc.perform(multipart("/api/v1/zip-upload")
                        .file(file)
                        .param("dstPath", "test-dir"))
                .andDo(print())
                .andExpect(status().isOk())
        ;
    }

    @DisplayName("Zip Download Test")
    @Test
    void downloadZipFileTest() throws Exception {
        // given

        // when & then
        mockMvc.perform(get("/api/v1/file-zipping-and-download")
                        .param("folderName", "src/test/resources/test-dir"))
                .andDo(print())
                .andExpect(status().isOk())
        ;
    }
}