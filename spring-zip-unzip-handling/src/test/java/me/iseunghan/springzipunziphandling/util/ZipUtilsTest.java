package me.iseunghan.springzipunziphandling.util;

import org.apache.tomcat.util.http.fileupload.FileUtils;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class ZipUtilsTest {

    @Order(1)
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

    @Order(1)
    @Test
    void fileZippingTest() throws IOException {
        // given
        final Path zipFilePath = Path.of("src/test/resources/한글이름_테스트.txt");
        final Path testZipPath = Path.of("src/test/resources/test2.zip");
        Files.deleteIfExists(testZipPath);  // delete test-zip

        // when
        byte[] bytes = ZipUtils.zipFile(zipFilePath.toFile());
        Files.write(testZipPath, bytes);

        // then
        assertThat(testZipPath).exists();
    }

    @Order(2)
    @Test
    void unzipTest() throws IOException {
        // given
        Path dstPath = Path.of("src/test/resources/unzip-result");
        FileUtils.deleteDirectory(dstPath.toFile());
        final Path testZipPath = Path.of("src/test/resources/test.zip");

        // when
        ZipUtils.unZipFile(dstPath.toString(), testZipPath.toFile());

        // then
        assertThat(dstPath).exists();
        assertThat(Path.of(dstPath.toString(), "test-dir", "한글이름_테스트.txt")).exists();
        assertThat(Path.of(dstPath.toString(), "test-dir", "file2.txt")).exists();
        assertThat(Path.of(dstPath.toString(), "test-dir", "file3.txt")).exists();
        assertThat(Path.of(dstPath.toString(), "test-dir", "test-dir2", "한글이름_테스트.txt")).exists();
        assertThat(Path.of(dstPath.toString(), "test-dir", "test-dir2", "file2.txt")).exists();
        assertThat(Path.of(dstPath.toString(), "test-dir", "test-dir2", "test-dir3", "한글이름_테스트.txt")).exists();
        assertThat(Path.of(dstPath.toString(), "test-dir", "test-dir2", "test-dir3", "file2.txt")).exists();
        assertThat(Path.of(dstPath.toString(), "test-dir", "test-dir2", "test-dir3", "test-dir4", "한글이름_테스트.txt")).exists();
        assertThat(Path.of(dstPath.toString(), "test-dir", "test-dir2", "test-dir3", "test-dir4", "file2.txt")).exists();
    }
}