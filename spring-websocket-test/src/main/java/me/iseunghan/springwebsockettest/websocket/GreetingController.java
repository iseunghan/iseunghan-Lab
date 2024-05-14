package me.iseunghan.springwebsockettest.websocket;

import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Controller;
import org.springframework.web.util.HtmlUtils;

@Controller
public class GreetingController {

    @MessageMapping("/hello")
    @SendTo("/topic/greetings")
    public Greeting greeting(
            @Payload HelloMessage message,
            @Header("Authorization") String authToken
    ) throws InterruptedException {
        validationToken(authToken);
        Thread.sleep(1000);
        return new Greeting("Hello, " + HtmlUtils.htmlEscape(message.getName()) + "!");
    }

    private void validationToken(String authToken) {
        // validate Auth Token -> 200 or 401 or 403
        System.out.println("Token -> " + authToken);
    }
}
