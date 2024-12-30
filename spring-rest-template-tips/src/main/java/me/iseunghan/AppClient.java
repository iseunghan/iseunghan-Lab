package me.iseunghan;

import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
@RequiredArgsConstructor
public class AppClient {
    private final RestTemplate restTemplate;

    public void callApi() {
        ResponseEntity<String> response = restTemplate.exchange("http://localhost:8080", HttpMethod.GET, null, String.class);
        System.out.printf("<< [Client Send Request] Header: %s %n", response.getBody());
    }
}
