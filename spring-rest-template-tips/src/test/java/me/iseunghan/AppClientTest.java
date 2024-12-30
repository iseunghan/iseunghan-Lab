package me.iseunghan;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.DEFINED_PORT)
class AppClientTest {
    @Autowired
    private AppClient appClient;

    @Test
    void callApi() {
        assertDoesNotThrow(() -> appClient.callApi());
    }
}