package me.iseunghan.springwebsockettest.websocket;

import lombok.extern.slf4j.Slf4j;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
public class WebSocketSessionManager {
    private final Map<String, WebSocketSession> userSessions = new ConcurrentHashMap<>();
    private final Map<String, Set<String>> userDeviceSubscriptions = new ConcurrentHashMap<>();

    public void updateSubscription(String userId, String message) {
        Set<String> subscription = userDeviceSubscriptions.computeIfAbsent(userId, k -> ConcurrentHashMap.newKeySet());
        subscription.clear();
        Arrays.stream(message.substring(1, message.length() - 1).split(","))
                .map(String::trim)
                .forEach(subscription::add);
        log.info(">> [subscription]: {}", message);
    }

    public Set<String> getSubscriptions(String userId) {
        return userDeviceSubscriptions.getOrDefault(userId, ConcurrentHashMap.newKeySet());
    }

    public void broadcastToSubscribedUsers(String topic, String message) {
        userDeviceSubscriptions.forEach((userId, subscriptions) -> {
            if (subscriptions.contains(topic)) {
                WebSocketSession session = userSessions.get(userId);
                if (session != null && session.isOpen()) {
                    try {
                        session.sendMessage(new TextMessage("{\"deviceId\": \"%s\", %s".formatted(topic, message.substring(1))));
                    } catch (IOException e) {
                        log.error(e.getMessage(), e);
                    }
                }
            }
        });
    }

    public void registerSession(WebSocketSession session) {
        userSessions.put(session.getId(), session);
    }

    public void unRegisterSession(WebSocketSession session) {
        userSessions.remove(session.getId(), session);
    }
}
