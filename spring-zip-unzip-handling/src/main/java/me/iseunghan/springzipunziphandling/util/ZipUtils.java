package me.iseunghan.springzipunziphandling.util;

import jakarta.annotation.Nullable;
import lombok.extern.slf4j.Slf4j;

import java.io.*;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Objects;
import java.util.function.Function;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
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
                throw new RuntimeException(e);
            } catch (IOException e) {
                log.error("Error while zipping file: {}, Exception: {}", parentFile, e.getMessage());
                throw new RuntimeException(e);
            }
        }
    }

    public static void unZipFile(String dstPath, File zipFile) throws IOException {
        unZipFile(dstPath, new FileInputStream(zipFile), null);
    }

    public static void unZipFile(String dstPath, InputStream inputStream, @Nullable Function<Path, Path> renameDuplicatedFilename) throws IOException {
        try (ZipInputStream zipInputStream = new ZipInputStream(inputStream, Charset.forName("EUC-KR"))) {
            ZipEntry entry;
            byte[] buffer = new byte[DEFAULT_BUFFER_SIZE];

            while ((entry = zipInputStream.getNextEntry()) != null) {
                final String entryName = entry.getName();
                if (entry.isDirectory() || entryName.startsWith("__MACOSX")) continue;

                File entryFile;
                if (renameDuplicatedFilename == null) {
                    entryFile = new File(dstPath, entryName);
                } else {
                    Path path = Path.of(dstPath, entryName);
                    entryFile = renameDuplicatedFilename.apply(path).toFile();
                }
                Files.createDirectories(entryFile.getParentFile().toPath());

                try (BufferedOutputStream outputStream = new BufferedOutputStream(new FileOutputStream(entryFile))) {
                    int bytesRead;
                    while ((bytesRead = zipInputStream.read(buffer)) != -1) {
                        outputStream.write(buffer, 0, bytesRead);
                    }
                }
                zipInputStream.closeEntry();
            }
        }
    }
}
