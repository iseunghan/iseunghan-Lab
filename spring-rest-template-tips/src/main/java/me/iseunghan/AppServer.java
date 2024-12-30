package me.iseunghan;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AppServer {

    @GetMapping("/")
    public String hello(HttpServletRequest request) throws IllegalAccessException {
        System.out.printf(">> [Server Get Request] Header: %s %n", request.getHeader("Authorization"));
        if (!request.getHeader("Authorization").equals("Bearer my-auth-token")) {
            throw new IllegalAccessException("not authenticated request");
        }
        return "greeting";
    }
}
