package me.iseunghan.springzipunziphandling.util;

import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.*;

class ZipUtilsTest {

    @Test
    void directoryZippingTest() throws IOException {
        // given
        final Path zipFilePath = Path.of("src/test/resources/test-dir");
        final Path testZipPath = Path.of("src/test/resources/test.zip");
        Files.deleteIfExists(testZipPath);  // delete test-zip

        // when
        byte[] bytes = ZipUtils.zipFile(zipFilePath.toFile());
        Files.write(testZipPath, bytes);

        // then
        assertThat(testZipPath).exists();
    }

    @Test
    void fileZippingTest() throws IOException {
        // given
        final Path zipFilePath = Path.of("src/test/resources/file1.txt");
        final Path testZipPath = Path.of("src/test/resources/test2.zip");
        Files.deleteIfExists(testZipPath);  // delete test-zip

        // when
        byte[] bytes = ZipUtils.zipFile(zipFilePath.toFile());
        Files.write(testZipPath, bytes);

        // then
        assertThat(testZipPath).exists();
    }
}