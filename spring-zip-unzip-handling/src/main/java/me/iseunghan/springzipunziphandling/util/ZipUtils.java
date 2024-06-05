package me.iseunghan.springzipunziphandling.util;

import lombok.extern.slf4j.Slf4j;

import java.io.*;
import java.util.Objects;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import static org.springframework.util.StringUtils.hasText;

@Slf4j
public class ZipUtils {
    public static int DEFAULT_BUFFER_SIZE = 2048;

    public static byte[] zipFile(File sourceFile) {
        try (ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream()) {
            try (ZipOutputStream zipOutputStream = new ZipOutputStream(byteArrayOutputStream)) {
                addFileToZip(sourceFile, zipOutputStream, null);
            }
            return byteArrayOutputStream.toByteArray();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private static void addFileToZip(File parentFile, ZipOutputStream zipOutputStream, String parentFolderName) {
        String currentPath = hasText(parentFolderName) ? parentFolderName + "/" + parentFile.getName() : parentFile.getName();
        if (parentFile.isDirectory()) {
            for (File f : Objects.requireNonNull(parentFile.listFiles())) {
                addFileToZip(f, zipOutputStream, currentPath);
            }
        } else {
            byte[] buffer = new byte[DEFAULT_BUFFER_SIZE];
            try (FileInputStream fileInputStream = new FileInputStream(parentFile)) {
                zipOutputStream.putNextEntry(new ZipEntry(currentPath));

                int length;
                while ((length = fileInputStream.read(buffer)) > 0) {
                    zipOutputStream.write(buffer, 0, length);
                }
                zipOutputStream.closeEntry();
            } catch (FileNotFoundException e) {
                log.error("File not found: {}, Exception: {}", parentFile, e.getMessage());
            } catch (IOException e) {
                log.error("Error while zipping file: {}, Exception: {}", parentFile, e.getMessage());
            }
        }
    }
}
