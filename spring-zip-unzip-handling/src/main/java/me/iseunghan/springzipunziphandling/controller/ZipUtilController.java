package me.iseunghan.springzipunziphandling.controller;

import jakarta.servlet.http.HttpServletResponse;
import me.iseunghan.springzipunziphandling.util.ZipUtils;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Path;
import java.util.UUID;

@RestController
public class ZipUtilController {

    @PostMapping(value = "/api/v1/zip-upload", produces = MediaType.APPLICATION_JSON_VALUE, consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<String> uploadZipFile(
            @RequestParam("dstPath") String dstPath,
            @RequestPart("file") MultipartFile file
    ) {
        try {
            ZipUtils.unZipFile(dstPath, file.getInputStream());
        } catch (IOException e) {
            return ResponseEntity.ok("failed to upload zip");
        }
        return ResponseEntity.ok("success to upload zip");
    }

    @GetMapping(value = "/api/v1/file-zipping-and-download")
    public void downloadZipFile(
            @RequestParam(value = "folderName") String folderName,
            HttpServletResponse response
    ) {
        try {
            byte[] bytes = ZipUtils.zipFile(Path.of(folderName).toFile());
            response.setContentType("application/zip");
            response.setHeader("Content-Disposition", "attachment; filename=".concat(UUID.randomUUID().toString()).concat(".zip"));
            response.getOutputStream().write(bytes);
        } catch (IOException e) {
            throw new RuntimeException("Failed to download zip file", e);
        }
    }
}
