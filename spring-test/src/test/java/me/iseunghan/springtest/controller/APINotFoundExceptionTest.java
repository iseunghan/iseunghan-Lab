package me.iseunghan.springtest.controller;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.web.client.RestTemplate;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class APINotFoundExceptionTest {
    @LocalServerPort private int port;

    @Test
    void 없는_API라면_404에러가_발생한다() throws Exception {
        // given
        RestTemplate restTemplate = new RestTemplate();

        // when & then
        assertThatThrownBy(() -> restTemplate.getForObject("http://localhost:" + port + "/api/404", String.class));
    }
}
