package me.iseunghan.springwebsockettest.websocket.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;

@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {
    /**
     * MessageBroker를 사용하기 위한 설정
     */
    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        config
                .setApplicationDestinationPrefixes("/app", "/app2", "/app3")  // @MessageMapping에 대한 Prefix를 설정한다.
                .enableSimpleBroker("/topic");
    }

    /**
     * Websocket Connection을 위한 Endpoint 설정
     */
    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/gs-guide-websocket");
    }
}
